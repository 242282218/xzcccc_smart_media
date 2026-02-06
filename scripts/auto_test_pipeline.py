import argparse
import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass
class TestCase:
    """
    Purpose: Represent a test case definition.
    Input: name, url, method, expected_status, case_type, execute flag, notes.
    Output: None.
    Side effects: None.
    """
    name: str
    url: str
    method: str
    expected_status: int
    case_type: str
    execute: bool
    notes: str = ""
    skip_reason: str = ""


@dataclass
class TestResult:
    """
    Purpose: Represent a test execution result.
    Input: case info and execution details.
    Output: None.
    Side effects: None.
    """
    name: str
    url: str
    method: str
    expected_status: int
    case_type: str
    status: int
    ok: bool
    elapsed_ms: int
    error: str | None = None
    notes: str = ""
    outcome: str = "PASS"


@dataclass
class Discovery:
    """
    Purpose: Collect discovery data.
    Input: frontend routes, api endpoints, view files, errors.
    Output: None.
    Side effects: None.
    """
    frontend_routes: List[str]
    api_endpoints: List[str]
    view_files: List[str]
    openapi_loaded: bool
    discovery_errors: List[str]


@dataclass
class Inputs:
    """
    Purpose: Store resolved runtime inputs.
    Input: parsed environment and defaults.
    Output: None.
    Side effects: None.
    """
    frontend_base: str
    backend_base: str
    openapi_url: str
    router_file: Path
    out_dir: Path


@dataclass
class AnalysisModule:
    """
    Purpose: Store inferred module analysis.
    Input: name and notes.
    Output: None.
    Side effects: None.
    """
    name: str
    notes: str


def _env_first(keys: List[str], default: str) -> str:
    """
    Purpose: Get the first non-empty environment variable among keys.
    Input: list of keys and default.
    Output: value string.
    Side effects: None.
    """
    for key in keys:
        val = os.getenv(key)
        if val:
            return val
    return default


def _is_local_url(url: str) -> bool:
    """
    Purpose: Check whether a URL targets local environment.
    Input: url string.
    Output: True if local, else False.
    Side effects: None.
    """
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    return host in {"localhost", "127.0.0.1", "0.0.0.0"}


def resolve_inputs(root: Path) -> Inputs:
    """
    Purpose: Resolve runtime inputs from environment or defaults.
    Input: project root path.
    Output: Inputs object.
    Side effects: Reads environment variables.
    """
    frontend_base = _env_first(["FRONTEND_BASE", "FRONTEND_URL", "FE_BASE"], "http://localhost:3000")
    backend_base = _env_first(["BACKEND_BASE", "API_BASE", "BE_BASE"], "http://localhost:8000")
    openapi_url = _env_first(["OPENAPI_URL", "SWAGGER_URL"], backend_base.rstrip("/") + "/openapi.json")
    router_file = Path(_env_first(["FRONTEND_ROUTER", "ROUTER_FILE"], str(root / "quark_strm" / "web" / "src" / "router" / "index.ts")))
    out_dir = Path(_env_first(["TEST_OUTPUT_DIR", "OUTPUT_DIR"], str(root / "output")))
    return Inputs(
        frontend_base=frontend_base,
        backend_base=backend_base,
        openapi_url=openapi_url,
        router_file=router_file,
        out_dir=out_dir,
    )


def load_openapi(url: str, timeout: int = 3) -> Tuple[Dict[str, Any], str | None]:
    """
    Purpose: Fetch OpenAPI JSON.
    Input: OpenAPI URL and timeout seconds.
    Output: (openapi dict, error message).
    Side effects: Network I/O.
    """
    try:
        with urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except Exception as exc:
        return {}, str(exc)


def discover_frontend_routes(router_file: Path) -> Tuple[List[str], str | None]:
    """
    Purpose: Parse frontend router file to extract routes.
    Input: router file path.
    Output: (route list, error message).
    Side effects: Reads local file.
    """
    if not router_file.exists():
        return [], f"router file not found: {router_file}"
    text = router_file.read_text(encoding="utf-8", errors="ignore")
    routes = re.findall(r"path:\s*'([^']+)'", text)
    return sorted(set(routes)), None


def discover_view_files(root: Path) -> List[str]:
    """
    Purpose: List frontend view files.
    Input: project root.
    Output: list of view file paths as strings.
    Side effects: Reads filesystem.
    """
    views_dir = root / "quark_strm" / "web" / "src" / "views"
    if not views_dir.exists():
        return []
    return sorted(str(p.relative_to(root)) for p in views_dir.glob("*.vue"))


def _read_text_safe(path: Path) -> str:
    """
    Purpose: Read text safely.
    Input: file path.
    Output: file text or empty string.
    Side effects: Reads local file.
    """
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def discover_api_from_source(root: Path) -> List[str]:
    """
    Purpose: Fallback discovery of API endpoints from source code.
    Input: project root.
    Output: list of endpoints in "METHOD /path" form.
    Side effects: Reads local files.
    """
    api_dirs = [root / "quark_strm" / "app" / "api", root / "quark_strm" / "app" / "api" / "v1" / "endpoints"]
    endpoints: List[str] = []
    for api_dir in api_dirs:
        if not api_dir.exists():
            continue
        for path in api_dir.glob("*.py"):
            text = _read_text_safe(path)
            prefix_match = re.search(r"APIRouter\(prefix=\"([^\"]+)\"", text)
            prefix = prefix_match.group(1) if prefix_match else ""
            for m in re.finditer(r"@router\.(get|post|put|delete|patch|api_route)\(\"([^\"]+)\"", text):
                method = m.group(1).upper()
                if method == "API_ROUTE":
                    method = "GET"
                route = m.group(2)
                full_path = f"{prefix}{route}" if route.startswith("/") else f"{prefix}/{route}"
                endpoints.append(f"{method} {full_path}")
    return sorted(set(endpoints))


def build_api_tests_from_openapi(openapi: Dict[str, Any], backend_base: str) -> Tuple[List[str], List[TestCase]]:
    """
    Purpose: Build test cases from OpenAPI spec.
    Input: OpenAPI dict and backend base URL.
    Output: (endpoint list, test case list).
    Side effects: None.
    """
    endpoints: List[str] = []
    cases: List[TestCase] = []
    paths = openapi.get("paths", {}) if isinstance(openapi, dict) else {}
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, spec in methods.items():
            method_upper = str(method).upper()
            endpoints.append(f"{method_upper} {path}")
            summary = ""
            if isinstance(spec, dict):
                summary = spec.get("summary", "") or spec.get("description", "") or ""
            cases.extend(build_cases_for_endpoint(method_upper, path, backend_base, summary))
    return sorted(set(endpoints)), cases


def build_cases_for_endpoint(method: str, path: str, backend_base: str, summary: str) -> List[TestCase]:
    """
    Purpose: Build up to 3 test cases for a single endpoint.
    Input: HTTP method, path, backend base, summary note.
    Output: list of TestCase.
    Side effects: None.
    """
    base_url = backend_base.rstrip("/") + path
    def _replace_params(url: str, fill: str) -> str:
        return re.sub(r"\{[^}]+\}", fill, url)

    cases: List[TestCase] = []
    case_types = ["normal", "boundary", "abnormal"]
    fills = ["1", "0", "-1"]
    for case_type, fill in zip(case_types, fills):
        url = _replace_params(base_url, fill)
        execute = method == "GET"
        skip_reason = "" if execute else "non-idempotent method"
        cases.append(TestCase(
            name=f"{method} {path} [{case_type}]",
            url=url,
            method=method,
            expected_status=200,
            case_type=case_type,
            execute=execute,
            notes=summary,
            skip_reason=skip_reason,
        ))
    return cases


def build_frontend_tests(frontend_base: str, routes: List[str]) -> List[TestCase]:
    """
    Purpose: Build frontend route GET tests.
    Input: frontend base URL and route list.
    Output: list of TestCase.
    Side effects: None.
    """
    cases: List[TestCase] = []
    for route in routes:
        if route.startswith(":"):
            continue
        url = frontend_base.rstrip("/") + route
        cases.append(TestCase(
            name=f"FE {route}",
            url=url,
            method="GET",
            expected_status=200,
            case_type="normal",
            execute=True,
            notes="frontend route",
        ))
    return cases


def _http_get(url: str, timeout: int = 3) -> Tuple[int, int, str | None]:
    """
    Purpose: Perform HTTP GET request.
    Input: url and timeout seconds.
    Output: (status_code, elapsed_ms, error_message).
    Side effects: Network I/O.
    """
    start = time.time()
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
        elapsed = int((time.time() - start) * 1000)
        return status, elapsed, None
    except HTTPError as exc:
        elapsed = int((time.time() - start) * 1000)
        return exc.code, elapsed, str(exc)
    except URLError as exc:
        elapsed = int((time.time() - start) * 1000)
        return 0, elapsed, str(exc)


def execute_tests(cases: List[TestCase], allow_network: bool) -> List[TestResult]:
    """
    Purpose: Execute test cases with constraints.
    Input: list of TestCase and allow_network flag.
    Output: list of TestResult.
    Side effects: Network I/O.
    """
    results: List[TestResult] = []
    for case in cases:
        if not case.execute:
            results.append(TestResult(
                name=case.name,
                url=case.url,
                method=case.method,
                expected_status=case.expected_status,
                case_type=case.case_type,
                status=0,
                ok=False,
                elapsed_ms=0,
                error=case.skip_reason or "skipped",
                notes=case.notes,
                outcome="SKIPPED",
            ))
            continue
        if not allow_network:
            results.append(TestResult(
                name=case.name,
                url=case.url,
                method=case.method,
                expected_status=case.expected_status,
                case_type=case.case_type,
                status=0,
                ok=False,
                elapsed_ms=0,
                error="blocked: non-local target",
                notes=case.notes,
                outcome="SKIPPED",
            ))
            continue
        status, elapsed_ms, error = _http_get(case.url)
        ok = status == case.expected_status
        outcome = "PASS" if ok else "FAIL"
        results.append(TestResult(
            name=case.name,
            url=case.url,
            method=case.method,
            expected_status=case.expected_status,
            case_type=case.case_type,
            status=status,
            ok=ok,
            elapsed_ms=elapsed_ms,
            error=error,
            notes=case.notes,
            outcome=outcome,
        ))
    return results


def summarize(results: List[TestResult]) -> Dict[str, Any]:
    """
    Purpose: Summarize test results.
    Input: list of TestResult.
    Output: summary dict.
    Side effects: None.
    """
    total = len(results)
    passed = sum(1 for r in results if r.outcome == "PASS")
    failed = sum(1 for r in results if r.outcome == "FAIL")
    skipped = sum(1 for r in results if r.outcome == "SKIPPED")
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": round((passed / total * 100) if total else 0, 2),
    }


def analyze_modules(root: Path, view_files: List[str]) -> List[AnalysisModule]:
    """
    Purpose: Infer system modules and data flows.
    Input: project root and view files.
    Output: list of AnalysisModule.
    Side effects: Reads local files.
    """
    modules: List[AnalysisModule] = []
    api_dir = root / "quark_strm" / "app" / "api"
    if api_dir.exists():
        for path in sorted(api_dir.glob("*.py")):
            name = path.stem
            modules.append(AnalysisModule(
                name=f"backend:{name}",
                notes=f"API module from {path.relative_to(root)}",
            ))
    for view in view_files:
        modules.append(AnalysisModule(
            name=f"frontend:{Path(view).stem}",
            notes=f"View component {view}",
        ))
    return modules


def map_page_to_api(root: Path) -> Dict[str, List[str]]:
    """
    Purpose: Map frontend views to API modules by import scanning.
    Input: project root.
    Output: dict mapping view to api module list.
    Side effects: Reads local files.
    """
    mapping: Dict[str, List[str]] = {}
    views_dir = root / "quark_strm" / "web" / "src" / "views"
    if not views_dir.exists():
        return mapping
    for view_file in views_dir.glob("*.vue"):
        text = _read_text_safe(view_file)
        apis = re.findall(r"@/api/([A-Za-z0-9_-]+)", text)
        mapping[str(view_file.name)] = sorted(set(apis))
    return mapping


def write_report(
    out_dir: Path,
    inputs: Inputs,
    discovery: Discovery,
    modules: List[AnalysisModule],
    mapping: Dict[str, List[str]],
    cases: List[TestCase],
    results: List[TestResult],
    discovery_errors: List[str],
    design_notes: List[str],
    allow_network: bool,
) -> Path:
    """
    Purpose: Write final test report in markdown and JSON.
    Input: collected data and output directory.
    Output: path to markdown report.
    Side effects: Writes files to disk.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize(results)
    failures = [r for r in results if r.outcome == "FAIL"]
    skipped = [r for r in results if r.outcome == "SKIPPED"]

    json_path = out_dir / "auto_test_report.json"
    md_path = out_dir / "auto_test_report.md"

    inputs_dict = asdict(inputs)
    inputs_dict["router_file"] = str(inputs.router_file)
    inputs_dict["out_dir"] = str(inputs.out_dir)

    json_path.write_text(json.dumps({
        "inputs": inputs_dict,
        "discovery": asdict(discovery),
        "modules": [asdict(m) for m in modules],
        "mapping": mapping,
        "cases": [asdict(c) for c in cases],
        "results": [asdict(r) for r in results],
        "summary": summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# 自动化测试报告")
    lines.append("")
    lines.append("## 系统功能与模块分析")
    lines.append("- 后端模块数: " + str(sum(1 for m in modules if m.name.startswith("backend:"))))
    lines.append("- 前端视图数: " + str(sum(1 for m in modules if m.name.startswith("frontend:"))))
    lines.append("- 模块清单:")
    for m in modules:
        lines.append(f"- {m.name} | {m.notes}")
    lines.append("")
    lines.append("## 接口 / 页面覆盖情况")
    lines.append(f"- 前端路由发现: {len(discovery.frontend_routes)}")
    lines.append(f"- 后端接口发现: {len(discovery.api_endpoints)}")
    lines.append(f"- 前端用例执行: {sum(1 for r in results if r.name.startswith('FE '))}")
    lines.append(f"- 接口用例执行: {sum(1 for r in results if r.name.startswith('GET ') or r.name.startswith('POST ') or r.name.startswith('PUT ') or r.name.startswith('DELETE ') or r.name.startswith('PATCH '))}")
    lines.append("")
    lines.append("## 测试设计说明")
    lines.append("- 每个接口最多 3 条用例：正常 / 边界 / 异常")
    lines.append("- 非 GET 接口仅生成用例，执行阶段标记为 SKIPPED（只读约束）")
    lines.append("- 单请求超时 3 秒，无重试")
    for note in design_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## 实际执行结果")
    lines.append(f"- 总用例数: {summary['total']}")
    lines.append(f"- 通过: {summary['passed']}")
    lines.append(f"- 失败: {summary['failed']}")
    lines.append(f"- 跳过: {summary['skipped']}")
    lines.append(f"- 通过率: {summary['pass_rate']}%")
    lines.append("")
    lines.append("### 失败用例")
    if not failures:
        lines.append("- 无")
    else:
        for f in failures:
            lines.append(f"- {f.name} | {f.status} | {f.url} | {f.error or ''}")
    lines.append("")
    lines.append("### 跳过用例")
    if not skipped:
        lines.append("- 无")
    else:
        for s in skipped:
            lines.append(f"- {s.name} | {s.url} | {s.error or ''}")
    lines.append("")
    lines.append("## 失败原因与复现方式")
    if not failures:
        lines.append("- 无失败")
    else:
        for f in failures:
            lines.append(f"- 复现: {f.method} {f.url}（期望 {f.expected_status}，实际 {f.status}）")
    lines.append("")
    lines.append("## 改进与修复建议")
    lines.append("- 为关键 GET 接口补充返回结构断言与字段校验")
    lines.append("- 为前端路由添加可用性探测（如健康页）")
    lines.append("- 为 OpenAPI 文档补充参数示例以提升自动化覆盖")
    lines.append("")
    lines.append("## 缺失信息与潜在风险")
    if discovery_errors:
        for err in discovery_errors:
            lines.append(f"- {err}")
    if not allow_network:
        lines.append("- 检测到非本地目标地址，已阻止网络请求")
    if not discovery_errors and allow_network:
        lines.append("- 无")
    lines.append("")
    lines.append("## 页面 → 接口 → 数据流向（推导）")
    if not mapping:
        lines.append("- 无可用映射")
    else:
        for view, apis in mapping.items():
            if apis:
                lines.append(f"- {view} -> {', '.join(apis)}")
            else:
                lines.append(f"- {view} -> (未发现 API 引用)")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    """
    Purpose: Run full testing pipeline and generate report.
    Input: CLI args.
    Output: None.
    Side effects: Network I/O and file writes.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-network", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    inputs = resolve_inputs(root)

    discovery_errors: List[str] = []
    frontend_routes, err = discover_frontend_routes(inputs.router_file)
    if err:
        discovery_errors.append(err)
    view_files = discover_view_files(root)

    openapi: Dict[str, Any] = {}
    openapi_loaded = False
    if _is_local_url(inputs.openapi_url) and not args.no_network:
        openapi, openapi_err = load_openapi(inputs.openapi_url, timeout=3)
        if openapi_err:
            discovery_errors.append(f"openapi load failed: {openapi_err}")
        else:
            openapi_loaded = True
    else:
        discovery_errors.append("openapi url is non-local or network disabled")

    api_endpoints: List[str]
    api_tests: List[TestCase]
    if openapi_loaded:
        api_endpoints, api_tests = build_api_tests_from_openapi(openapi, inputs.backend_base)
    else:
        api_endpoints = discover_api_from_source(root)
        api_tests = []
        for endpoint in api_endpoints:
            parts = endpoint.split(" ", 1)
            if len(parts) != 2:
                continue
            method, path = parts
            api_tests.extend(build_cases_for_endpoint(method, path, inputs.backend_base, "source inferred"))

    fe_tests = build_frontend_tests(inputs.frontend_base, frontend_routes)

    allow_network = (
        _is_local_url(inputs.frontend_base)
        and _is_local_url(inputs.backend_base)
        and _is_local_url(inputs.openapi_url)
        and not args.no_network
    )

    discovery = Discovery(
        frontend_routes=frontend_routes,
        api_endpoints=api_endpoints,
        view_files=view_files,
        openapi_loaded=openapi_loaded,
        discovery_errors=discovery_errors,
    )

    modules = analyze_modules(root, view_files)
    mapping = map_page_to_api(root)

    design_notes = []
    if not openapi_loaded:
        design_notes.append("OpenAPI 不可用，接口从源码推导")

    cases = fe_tests + api_tests
    results = execute_tests(cases, allow_network=allow_network)

    write_report(
        out_dir=inputs.out_dir,
        inputs=inputs,
        discovery=discovery,
        modules=modules,
        mapping=mapping,
        cases=cases,
        results=results,
        discovery_errors=discovery_errors,
        design_notes=design_notes,
        allow_network=allow_network,
    )


if __name__ == "__main__":
    main()
