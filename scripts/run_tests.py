from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("ai/test_config.yaml")
DEFAULT_LOGS_DIR = Path("logs/test")


class TestRunnerError(RuntimeError):
    """
    测试运行器异常基类。

    用途: 统一表示测试运行器的配置/环境错误。
    输入: 无。
    输出: 无。
    副作用: 无。
    """


def _read_text(path: Path) -> str:
    """
    读取文本文件（兼容 UTF-8 BOM）。

    用途: 读取配置与日志文本。
    输入:
        - path (Path): 文件路径。
    输出:
        - str: 文件内容。
    副作用:
        - 无。
    """

    return path.read_text(encoding="utf-8-sig")


def _load_yaml(path: Path) -> dict[str, Any]:
    """
    读取 YAML 配置。

    用途: 加载测试套件配置。
    输入:
        - path (Path): 配置文件路径。
    输出:
        - dict[str, Any]: 配置字典。
    副作用:
        - 无。
    """

    try:
        import yaml
    except ModuleNotFoundError as error:
        raise TestRunnerError("缺少依赖 pyyaml，无法读取 ai/test_config.yaml") from error

    if not path.exists():
        raise TestRunnerError(f"配置文件不存在: {path}")

    data = yaml.safe_load(_read_text(path))
    if not isinstance(data, dict):
        raise TestRunnerError("配置文件内容无效")
    return data


def _is_container() -> bool:
    """
    判断是否运行在容器内。

    用途: 限制测试仅在 Dev Container/CI 内执行。
    输入:
        - 无。
    输出:
        - bool: 是否在容器中。
    副作用:
        - 无。
    """

    if Path("/.dockerenv").exists():
        return True
    if os.environ.get("CODESPACES", "").lower() == "true":
        return True
    if os.environ.get("REMOTE_CONTAINERS", "").lower() == "true":
        return True
    if os.environ.get("DEVCONTAINER", "").lower() == "true":
        return True
    return False


def _normalize_command(command: Any) -> list[str]:
    """
    规范化测试命令列表并绑定当前 Python 解释器。

    用途: 统一命令格式，避免调用错误解释器。
    输入:
        - command (Any): 原始命令配置。
    输出:
        - list[str]: 规范化后的命令列表。
    副作用:
        - 无。
    """

    if not isinstance(command, list) or not command:
        raise TestRunnerError("command 必须是非空列表")

    normalized = [str(item) for item in command]
    if normalized[0].lower() in {"python", "python3", "py"}:
        normalized[0] = sys.executable
    return normalized


def _read_last_duration(history_path: Path) -> float | None:
    """
    读取上一轮测试耗时。

    用途: 为动态超时计算提供历史基线。
    输入:
        - history_path (Path): summary.json 路径。
    输出:
        - float | None: 上次耗时（秒），无则返回 None。
    副作用:
        - 无。
    """

    if not history_path.exists():
        return None
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    duration = data.get("duration_sec")
    try:
        return float(duration)
    except (TypeError, ValueError):
        return None


def _compute_timeout_sec(
    suite_config: dict[str, Any],
    history_path: Path,
) -> float:
    """
    计算测试超时（D2 动态策略）。

    用途: 根据历史耗时动态调整超时。
    输入:
        - suite_config (dict): suite 配置。
        - history_path (Path): summary.json 路径。
    输出:
        - float: 超时秒数。
    副作用:
        - 无。
    """

    timeout_mode = str(suite_config.get("timeout_mode", "D2")).upper()
    timeout_min = float(suite_config.get("timeout_min_sec", 60))
    timeout_max = suite_config.get("timeout_max_sec", None)
    timeout_max_value = float(timeout_max) if timeout_max is not None else None

    base_timeout = timeout_min
    if timeout_mode == "D2":
        last_duration = _read_last_duration(history_path)
        if last_duration is not None:
            base_timeout = last_duration * 2

    timeout_sec = max(timeout_min, base_timeout)
    if timeout_max_value is not None:
        timeout_sec = min(timeout_sec, timeout_max_value)
    return timeout_sec


def _strip_namespace(tag_name: str) -> str:
    """
    去除 XML 命名空间前缀。

    用途: 兼容带命名空间的 junit.xml。
    输入:
        - tag_name (str): 原始标签名。
    输出:
        - str: 去除命名空间后的标签名。
    副作用:
        - 无。
    """

    if "}" in tag_name:
        return tag_name.split("}", 1)[1]
    return tag_name


def _is_xpass(element: ElementTree.Element) -> bool:
    """
    判断 junit 元素是否代表 XPASS。

    用途: 识别 XPASS 用例并纳入失败列表。
    输入:
        - element (ElementTree.Element): junit 子节点。
    输出:
        - bool: 是否 XPASS。
    副作用:
        - 无。
    """

    text_parts = [
        element.get("type", ""),
        element.get("message", ""),
        element.text or "",
    ]
    combined = " ".join(text_parts).lower()
    return "xpass" in combined or "xpassed" in combined


def _collect_failed_cases(junit_path: Path) -> list[str]:
    """
    从 junit.xml 汇总失败/错误/XPASS 用例。

    用途: 生成失败用例列表。
    输入:
        - junit_path (Path): junit.xml 路径。
    输出:
        - list[str]: 失败用例标识列表。
    副作用:
        - 无。
    """

    if not junit_path.exists():
        return []

    try:
        tree = ElementTree.parse(junit_path)
    except ElementTree.ParseError:
        return []

    root = tree.getroot()
    failed_cases: list[str] = []

    for testcase in root.iter():
        if _strip_namespace(testcase.tag) != "testcase":
            continue
        name = testcase.attrib.get("name", "unknown")
        class_name = testcase.attrib.get("classname", "")
        case_label = f"{class_name}::{name}" if class_name else name

        for child in list(testcase):
            tag_name = _strip_namespace(child.tag).lower()
            if tag_name in {"failure", "error"}:
                failed_cases.append(case_label)
                break
            if tag_name == "skipped" and _is_xpass(child):
                failed_cases.append(case_label)
                break

    return failed_cases


def _write_summary(summary_path: Path, summary: dict[str, Any]) -> None:
    """
    写入 summary.json。

    用途: 输出结构化测试摘要。
    输入:
        - summary_path (Path): summary.json 路径。
        - summary (dict): 摘要内容。
    输出:
        - 无。
    副作用:
        - 写入 summary.json 文件。
    """

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _ensure_logs_dir(logs_dir: Path) -> None:
    """
    确保日志目录存在。

    用途: 创建日志目录。
    输入:
        - logs_dir (Path): 日志目录。
    输出:
        - 无。
    副作用:
        - 创建目录（若不存在）。
    """

    logs_dir.mkdir(parents=True, exist_ok=True)


def _append_error(log_path: Path, message: str) -> None:
    """
    追加错误信息到日志。

    用途: 记录配置/环境/超时错误。
    输入:
        - log_path (Path): 日志路径。
        - message (str): 错误信息。
    输出:
        - 无。
    副作用:
        - 追加写入日志文件。
    """

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def main(argv: list[str]) -> int:
    """
    统一测试入口。

    用途: 按配置执行测试并产生日志/摘要。
    输入:
        - argv (list[str]): 命令行参数。
    输出:
        - int: 进程退出码。
    副作用:
        - 执行测试命令并写入日志与 summary.json。
    """

    parser = argparse.ArgumentParser(description="Unified test runner")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--suite", default=None)
    parser.add_argument("--logs-dir", default=None)
    parser.add_argument("--allow-host", action="store_true")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    initial_logs_dir = Path(args.logs_dir) if args.logs_dir else DEFAULT_LOGS_DIR
    _ensure_logs_dir(initial_logs_dir)

    summary_path = initial_logs_dir / "summary.json"
    stdout_path = initial_logs_dir / "stdout.log"
    stderr_path = initial_logs_dir / "stderr.log"

    try:
        config = _load_yaml(config_path)
    except TestRunnerError as error:
        _append_error(stderr_path, str(error))
        _write_summary(
            summary_path,
            {
                "suite": None,
                "status": "CONFIG_ERROR",
                "duration_sec": 0,
                "timeout_sec": 0,
                "exit_code": 2,
                "failed_cases": [],
                "message": str(error),
            },
        )
        return 2

    if not args.logs_dir:
        initial_logs_dir = Path(config.get("logs_dir", initial_logs_dir))
    logs_dir = initial_logs_dir
    _ensure_logs_dir(logs_dir)

    summary_path = logs_dir / "summary.json"
    stdout_path = logs_dir / "stdout.log"
    stderr_path = logs_dir / "stderr.log"

    require_container = bool(config.get("require_container", False))
    is_ci = os.environ.get("CI", "").lower() == "true"
    if require_container and not args.allow_host and not _is_container() and not is_ci:
        message = "禁止在宿主机运行测试，请在 Dev Container 内执行。"
        _append_error(stderr_path, message)
        _write_summary(
            summary_path,
            {
                "suite": None,
                "status": "ENV_ERROR",
                "duration_sec": 0,
                "timeout_sec": 0,
                "exit_code": 2,
                "failed_cases": [],
                "message": message,
            },
        )
        return 2

    suites = config.get("suites", {})
    default_suite = config.get("default_suite")
    suite_name = args.suite or default_suite
    if not suite_name or suite_name not in suites:
        message = f"未知 suite: {suite_name}"
        _append_error(stderr_path, message)
        _write_summary(
            summary_path,
            {
                "suite": suite_name,
                "status": "CONFIG_ERROR",
                "duration_sec": 0,
                "timeout_sec": 0,
                "exit_code": 2,
                "failed_cases": [],
                "message": message,
            },
        )
        return 2

    suite_config = suites[suite_name]
    command = _normalize_command(suite_config.get("command"))
    working_dir = Path(suite_config.get("working_dir", ".")).resolve()
    if not working_dir.exists():
        message = f"working_dir 不存在: {working_dir}"
        _append_error(stderr_path, message)
        _write_summary(
            summary_path,
            {
                "suite": suite_name,
                "status": "CONFIG_ERROR",
                "duration_sec": 0,
                "timeout_sec": 0,
                "exit_code": 2,
                "failed_cases": [],
                "message": message,
            },
        )
        return 2

    history_file = Path(config.get("history_file", summary_path))
    timeout_sec = _compute_timeout_sec(suite_config, history_file)

    junit_path = logs_dir / "junit.xml"
    if suite_config.get("junit_path"):
        junit_path = Path(suite_config["junit_path"])

    start_time = time.monotonic()
    status = "FAIL"
    exit_code = 1

    with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        try:
            result = subprocess.run(
                command,
                cwd=str(working_dir),
                stdout=stdout_handle,
                stderr=stderr_handle,
                stdin=subprocess.DEVNULL,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            exit_code = result.returncode
            status = "PASS" if result.returncode == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            exit_code = 2

    duration_sec = time.monotonic() - start_time
    failed_cases = _collect_failed_cases(junit_path)

    _write_summary(
        summary_path,
        {
            "suite": suite_name,
            "status": status,
            "duration_sec": round(duration_sec, 2),
            "timeout_sec": round(timeout_sec, 2),
            "exit_code": exit_code,
            "failed_cases": failed_cases,
        },
    )

    if status == "TIMEOUT":
        _append_error(stderr_path, f"测试超时({timeout_sec:.2f}s)")

    if status == "PASS":
        return 0
    if status == "FAIL":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
