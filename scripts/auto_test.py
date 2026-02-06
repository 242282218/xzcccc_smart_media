import argparse
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


@dataclass
class TestCase:
    """
    Purpose: Represent a test case.
    Input: name, url, method, expected_status, notes.
    Output: None.
    Side effects: None.
    """
    name: str
    url: str
    method: str
    expected_status: int
    notes: str = ""


@dataclass
class TestResult:
    """
    Purpose: Represent a test result.
    Input: test case and execution details.
    Output: None.
    Side effects: None.
    """
    name: str
    url: str
    method: str
    expected_status: int
    status: int
    ok: bool
    elapsed_ms: int
    error: str | None = None
    notes: str = ""


def _http_get(url: str, timeout: int = 6) -> Tuple[int, int, str | None]:
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
    except HTTPError as e:
        elapsed = int((time.time() - start) * 1000)
        return e.code, elapsed, str(e)
    except URLError as e:
        elapsed = int((time.time() - start) * 1000)
        return 0, elapsed, str(e)


def load_openapi(url: str) -> Dict[str, Any]:
    """
    Purpose: Fetch OpenAPI JSON.
    Input: OpenAPI URL.
    Output: Parsed JSON dict.
    Side effects: Network I/O.
    """
    with urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_frontend_routes(router_file: Path) -> List[str]:
    """
    Purpose: Parse frontend router file to extract routes.
    Input: Path to router file.
    Output: List of route paths.
    Side effects: Reads local file.
    """
    text = router_file.read_text(encoding="utf-8", errors="ignore")
    routes = re.findall(r"path:\s*'([^']+)'", text)
    return sorted(set(routes))


def build_api_tests(openapi: Dict[str, Any], backend_base: str) -> Tuple[List[str], List[TestCase]]:
    """
    Purpose: Build safe GET test cases from OpenAPI spec.
    Input: OpenAPI dict and backend base URL.
    Output: (endpoint list, test case list).
    Side effects: None.
    """
    endpoints = []
    cases: List[TestCase] = []
    paths = openapi.get("paths", {})
    for path, methods in paths.items():
        for method, spec in methods.items():
            method_upper = method.upper()
            endpoints.append(f"{method_upper} {path}")
            if method_upper != "GET":
                continue
            url = backend_base.rstrip("/") + path
            url = re.sub(r"\{[^}]*id[^}]*\}", "1", url, flags=re.IGNORECASE)
            url = re.sub(r"\{[^}]*parent[^}]*\}", "0", url, flags=re.IGNORECASE)
            url = re.sub(r"\{[^}]*file[^}]*\}", "0", url, flags=re.IGNORECASE)
            url = re.sub(r"\{[^}]*\}", "0", url)
            cases.append(TestCase(
                name=f"GET {path}",
                url=url,
                method="GET",
                expected_status=200,
                notes=spec.get("summary", "") or ""
            ))
    endpoints = sorted(set(endpoints))
    return endpoints, cases


def build_frontend_tests(frontend_base: str, routes: List[str]) -> List[TestCase]:
    """
    Purpose: Build GET tests for frontend routes.
    Input: Frontend base URL and route list.
    Output: Test case list.
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
            notes="frontend route"
        ))
    return cases


def run_tests(cases: List[TestCase]) -> List[TestResult]:
    """
    Purpose: Execute test cases.
    Input: List of TestCase.
    Output: List of TestResult.
    Side effects: Network I/O.
    """
    results: List[TestResult] = []
    for case in cases:
        status, elapsed_ms, error = _http_get(case.url)
        ok = status == case.expected_status
        results.append(TestResult(
            name=case.name,
            url=case.url,
            method=case.method,
            expected_status=case.expected_status,
            status=status,
            ok=ok,
            elapsed_ms=elapsed_ms,
            error=error,
            notes=case.notes
        ))
    return results


def summarize(results: List[TestResult]) -> Dict[str, Any]:
    """
    Purpose: Summarize test results.
    Input: List of TestResult.
    Output: Summary dict.
    Side effects: None.
    """
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    failed = total - passed
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round((passed / total * 100) if total else 0, 2)
    }


def write_report(results: List[TestResult], frontend_routes: List[str], api_endpoints: List[str], out_dir: Path) -> None:
    """
    Purpose: Write JSON and Markdown reports.
    Input: Results, discovery data, output directory.
    Output: None.
    Side effects: Writes files to disk.
    """
    summary = summarize(results)
    failures = [r for r in results if not r.ok]

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "auto_test_report.json"
    md_path = out_dir / "auto_test_report.md"

    json_path.write_text(json.dumps({
        "frontend_routes": frontend_routes,
        "api_endpoints": api_endpoints,
        "results": [asdict(r) for r in results],
        "summary": summary,
        "failures": [asdict(f) for f in failures]
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 自动化测试报告")
    lines.append("")
    lines.append(f"- 总用例数: {summary['total']}")
    lines.append(f"- 通过: {summary['passed']}")
    lines.append(f"- 失败: {summary['failed']}")
    lines.append(f"- 通过率: {summary['pass_rate']}%")
    lines.append("")
    lines.append("## 失败用例")
    if not failures:
        lines.append("- 无")
    else:
        for f in failures:
            lines.append(f"- {f.name} | {f.status} | {f.url} | {f.error or ''}")
    lines.append("")
    lines.append("## 覆盖概览")
    lines.append(f"- 前端路由数: {len(frontend_routes)}")
    lines.append(f"- 后端接口数: {len(api_endpoints)}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """
    Purpose: Run discovery and tests in batches, then write report.
    Input: CLI args for batch size.
    Output: None.
    Side effects: Network I/O and file writes.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()

    frontend_base = "http://localhost:3000"
    backend_openapi = "http://localhost:8000/openapi.json"
    backend_base = "http://localhost:8000"
    router_file = Path(r"C:\Users\24228\Desktop\smart_media\quark_strm\web\src\router\index.ts")
    out_dir = Path(r"C:\Users\24228\Desktop\smart_media\logs")

    frontend_routes = discover_frontend_routes(router_file)
    openapi = load_openapi(backend_openapi)
    api_endpoints, api_tests = build_api_tests(openapi, backend_base)
    fe_tests = build_frontend_tests(frontend_base, frontend_routes)

    all_tests = fe_tests + api_tests
    results: List[TestResult] = []

    for i in range(0, len(all_tests), args.batch_size):
        batch = all_tests[i:i + args.batch_size]
        results.extend(run_tests(batch))
        write_report(results, frontend_routes, api_endpoints, out_dir)


if __name__ == "__main__":
    main()
