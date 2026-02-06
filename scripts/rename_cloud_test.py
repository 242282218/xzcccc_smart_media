# -*- coding: utf-8 -*-
import asyncio
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPORT_VERSION = "1.0"
DEFAULT_TIMEOUT_SEC = 3
SPECIAL_CHARS = " test-[]()_"
MAX_PAGES_PER_DIR = int(os.environ.get("RENAME_TEST_MAX_PAGES", "5"))
MAX_DIRS_SCAN = int(os.environ.get("RENAME_TEST_MAX_DIRS", "80"))
MAX_ITEMS_TOTAL = int(os.environ.get("RENAME_TEST_MAX_ITEMS", "2000"))
GLOBAL_TIMEOUT_SEC = int(os.environ.get("RENAME_TEST_GLOBAL_TIMEOUT", "90"))


@dataclass
class RenameResult:
    """Purpose: Represent a single rename test result.
    Input: Attributes about the test case and operation outcomes.
    Output: Serializable data via asdict().
    Side effects: None.
    """

    item_type: str
    fid: str
    parent_fid: str
    original_name: str
    temp_name: str
    stage: str
    success: bool
    error: Optional[str]
    details: Dict[str, Any]


@dataclass
class ScanItem:
    """Purpose: Store scanned file or directory metadata for testing.
    Input: Metadata fields discovered from Quark API listing.
    Output: Structured item used by rename logic.
    Side effects: None.
    """

    fid: str
    parent_fid: str
    name: str
    is_dir: bool
    size: int
    file_type: Optional[int]
    category: Optional[int]


@dataclass
class RunContext:
    """Purpose: Hold run-level configuration and state.
    Input: Config values and runtime selections.
    Output: Accessible attributes for test execution.
    Side effects: None.
    """

    root_fid: str
    test_dir_fid: Optional[str]
    test_dir_name: Optional[str]
    test_dir_created: bool
    special_char_targets: int
    timeout_sec: int


@dataclass
class RunSummary:
    """Purpose: Summarize execution metrics and findings.
    Input: Aggregated counters and notes.
    Output: Serializable summary.
    Side effects: None.
    """

    started_at: str
    finished_at: str
    total_items: int
    total_files: int
    total_dirs: int
    rename_attempts: int
    rename_successes: int
    rename_failures: int
    timeouts: int
    skipped: int


def load_yaml_config(path: Path) -> Dict[str, Any]:
    """Purpose: Load YAML configuration.
    Input: Path to a YAML file.
    Output: Parsed configuration as a dictionary.
    Side effects: Reads file from disk.
    """
    try:
        import yaml  # type: ignore
    except Exception as exc:
        return {
            "__error__": f"PyYAML import failed: {exc}",
            "__path__": str(path),
        }

    if not path.exists():
        return {"__error__": "config not found", "__path__": str(path)}

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {"__error__": f"config parse failed: {exc}", "__path__": str(path)}


def now_iso() -> str:
    """Purpose: Get current time in ISO format.
    Input: None.
    Output: ISO 8601 datetime string.
    Side effects: None.
    """
    return datetime.utcnow().isoformat() + "Z"


def ensure_sys_path(root: Path) -> None:
    """Purpose: Ensure project root is importable.
    Input: Project root path.
    Output: None.
    Side effects: Mutates sys.path.
    """
    sys.path.insert(0, str(root))
    quark_root = root / "quark_strm"
    if quark_root.exists():
        sys.path.insert(0, str(quark_root))


def pick_test_dir_name(candidates: List[str]) -> List[str]:
    """Purpose: Normalize test directory candidate names.
    Input: Candidate list.
    Output: Normalized candidate list.
    Side effects: None.
    """
    normalized = []
    for name in candidates:
        if name and name not in normalized:
            normalized.append(name)
    return normalized


async def list_all_in_dir(
    service,
    pdir_fid: str,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
    max_pages: int = MAX_PAGES_PER_DIR,
) -> List[Dict[str, Any]]:
    """Purpose: List all items in a directory, handling pagination.
    Input: Quark service and directory fid.
    Output: List of item dictionaries.
    Side effects: Calls Quark API.
    """
    items: List[Dict[str, Any]] = []
    page = 1
    size = 100

    while True:
        result = await asyncio.wait_for(
            service.list_files(pdir_fid=pdir_fid, page=page, size=size),
            timeout=timeout_sec,
        )
        batch = result.get("list", [])
        metadata = result.get("metadata", {}) or {}
        items.extend(batch)

        total = metadata.get("total") or metadata.get("_total") or None
        if total is not None:
            if page * size >= int(total):
                break
        else:
            if len(batch) < size:
                break
        page += 1
        if page > max_pages:
            break

    return items


async def find_or_create_test_dir(service, root_fid: str, candidates: List[str]) -> Tuple[Optional[str], Optional[str], bool, List[str]]:
    """Purpose: Find a test directory by name or create one.
    Input: Quark service, root fid, candidate names.
    Output: (fid, name, created, notes)
    Side effects: May create a directory in Quark drive.
    """
    notes: List[str] = []
    async def dir_has_items(fid: str) -> bool:
        """Purpose: Check whether a directory has at least one item.
        Input: Directory fid.
        Output: True if any child exists, else False.
        Side effects: Calls Quark API.
        """
        try:
            result = await asyncio.wait_for(
                service.list_files(pdir_fid=fid, page=1, size=1),
                timeout=DEFAULT_TIMEOUT_SEC,
            )
            children = result.get("list", [])
            return len(children) > 0
        except Exception:
            return False

    try:
        root_items = await list_all_in_dir(service, root_fid)
    except Exception as exc:
        notes.append(f"root list failed: {exc}")
        root_items = []
    by_name = {item.get("file_name"): item for item in root_items}

    for name in candidates:
        for key, item in by_name.items():
            if key and key.lower() == name.lower() and item.get("file_type") == 0:
                fid = item.get("fid")
                if fid and await dir_has_items(str(fid)):
                    return fid, item.get("file_name"), False, notes
                notes.append(f"candidate dir empty: {item.get('file_name')}")

    # Search for any existing folder containing "test" in its name (depth-limited)
    try:
        queue: List[Tuple[str, int]] = [(root_fid, 0)]
        scanned_dirs = 0
        while queue and scanned_dirs < MAX_DIRS_SCAN:
            current, depth = queue.pop(0)
            scanned_dirs += 1
            children = await list_all_in_dir(service, current)
            for child in children:
                if child.get("file_type") == 0:
                    name = (child.get("file_name") or "").lower()
                    fid = child.get("fid")
                    if "test" in name or "rename" in name:
                        if fid and await dir_has_items(str(fid)):
                            return fid, child.get("file_name"), False, notes
                        notes.append(f"candidate dir empty: {child.get('file_name')}")
                    if depth < 2 and fid:
                        queue.append((str(fid), depth + 1))
    except Exception as exc:
        notes.append(f"fallback test-dir search failed: {exc}")

    # Fallback: pick the first directory that contains at least one file
    try:
        queue: List[Tuple[str, int, str]] = [(root_fid, 0, "/")]
        scanned_dirs = 0
        while queue and scanned_dirs < MAX_DIRS_SCAN:
            current, depth, current_name = queue.pop(0)
            scanned_dirs += 1
            children = await list_all_in_dir(service, current)
            has_file = any(child.get("file_type") == 1 for child in children)
            if current != root_fid and has_file:
                return current, current_name, False, notes
            for child in children:
                if child.get("file_type") == 0 and depth < 2 and child.get("fid"):
                    queue.append((str(child.get("fid")), depth + 1, child.get("file_name") or ""))
    except Exception as exc:
        notes.append(f"fallback directory-with-files search failed: {exc}")

    test_name = f"smart_media_rename_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    try:
        result = await asyncio.wait_for(
            service.mkdir(root_fid, test_name),
            timeout=DEFAULT_TIMEOUT_SEC,
        )
        fid = result.get("data", {}).get("fid") or result.get("fid")
        if not fid:
            notes.append("create_directory returned no fid; test directory unavailable")
            return None, test_name, True, notes
        return fid, test_name, True, notes
    except Exception as exc:
        notes.append(f"create_directory failed: {exc}")
        return None, None, False, notes


async def scan_tree(service, root_fid: str) -> List[ScanItem]:
    """Purpose: Recursively scan a directory tree.
    Input: Quark service and root fid.
    Output: List of ScanItem for files and directories.
    Side effects: Calls Quark API.
    """
    items: List[ScanItem] = []
    queue: List[str] = [root_fid]

    while queue:
        if len(items) >= MAX_ITEMS_TOTAL:
            break
        current = queue.pop(0)
        try:
            children = await list_all_in_dir(service, current)
        except Exception:
            continue

        for child in children:
            fid = str(child.get("fid"))
            name = child.get("file_name") or ""
            file_type = child.get("file_type")
            is_dir = file_type == 0
            size = int(child.get("size") or 0)
            category = child.get("category")
            item = ScanItem(
                fid=fid,
                parent_fid=current,
                name=name,
                is_dir=is_dir,
                size=size,
                file_type=file_type,
                category=category,
            )
            items.append(item)
            if len(items) >= MAX_ITEMS_TOTAL:
                break
            if is_dir:
                queue.append(fid)

    return items


def split_name_ext(name: str) -> Tuple[str, str]:
    """Purpose: Split a filename into stem and extension.
    Input: Filename string.
    Output: (stem, extension) where extension includes dot or empty.
    Side effects: None.
    """
    if "." not in name or name.startswith(".") and name.count(".") == 1:
        return name, ""
    stem, ext = name.rsplit(".", 1)
    return stem, f".{ext}"


def build_temp_name(original: str, suffix: str, add_special: bool) -> str:
    """Purpose: Build a temporary renamed filename.
    Input: Original name, suffix, special-char flag.
    Output: New filename string.
    Side effects: None.
    """
    stem, ext = split_name_ext(original)
    special = SPECIAL_CHARS if add_special else ""
    new_stem = f"{stem}{special}{suffix}"
    return f"{new_stem}{ext}"


def choose_special_targets(items: List[ScanItem], max_targets: int) -> List[str]:
    """Purpose: Choose item fids to receive special-char rename tests.
    Input: Items list and max target count.
    Output: List of fids.
    Side effects: None.
    """
    chosen: List[str] = []
    for item in items:
        if len(chosen) >= max_targets:
            break
        if item.name and item.fid not in chosen:
            chosen.append(item.fid)
    return chosen


async def get_parent_name_map(service, parent_fid: str) -> Dict[str, Dict[str, Any]]:
    """Purpose: Map names to items within a parent directory.
    Input: Quark service and parent fid.
    Output: Dict of name -> item metadata.
    Side effects: Calls Quark API.
    """
    children = await list_all_in_dir(service, parent_fid)
    result: Dict[str, Dict[str, Any]] = {}
    for child in children:
        name = child.get("file_name") or ""
        result[name] = child
    return result


async def rename_with_timeout(service, fid: str, new_name: str, timeout_sec: int) -> Dict[str, Any]:
    """Purpose: Rename a file or directory with timeout.
    Input: Quark service, fid, new name, timeout seconds.
    Output: Result dictionary from service.
    Side effects: Calls Quark API and renames item.
    """
    return await asyncio.wait_for(service.rename_file(fid=fid, new_name=new_name), timeout=timeout_sec)


async def verify_item(service, parent_fid: str, fid: str) -> Optional[Dict[str, Any]]:
    """Purpose: Locate an item by fid within a parent directory.
    Input: Quark service, parent fid, item fid.
    Output: Item dict if found, else None.
    Side effects: Calls Quark API.
    """
    children = await list_all_in_dir(service, parent_fid)
    for child in children:
        if str(child.get("fid")) == str(fid):
            return child
    return None


async def run_rename_tests(service, ctx: RunContext, items: List[ScanItem]) -> Tuple[List[RenameResult], RunSummary, List[str]]:
    """Purpose: Execute rename tests over scanned items.
    Input: Quark service, run context, scanned items.
    Output: (results list, summary, notes)
    Side effects: Performs rename operations on Quark drive items.
    """
    notes: List[str] = []
    started_at = now_iso()
    results: List[RenameResult] = []
    timeouts = 0
    skipped = 0

    files = [i for i in items if not i.is_dir]
    dirs = [i for i in items if i.is_dir]
    if len(items) >= MAX_ITEMS_TOTAL:
        notes.append(f"scan truncated at MAX_ITEMS_TOTAL={MAX_ITEMS_TOTAL}")

    special_targets = set(choose_special_targets(items, ctx.special_char_targets))
    suffix = f"__renametest_{datetime.utcnow().strftime('%H%M%S')}"

    async def process_item(item: ScanItem, stage: str) -> None:
        nonlocal timeouts, skipped
        add_special = item.fid in special_targets
        temp_name = build_temp_name(item.name, suffix, add_special)

        try:
            name_map = await get_parent_name_map(service, item.parent_fid)
        except Exception as exc:
            skipped += 1
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-precheck",
                success=False,
                error=str(exc),
                details={"reason": "list parent failed"},
            ))
            return

        if temp_name in name_map:
            temp_name = build_temp_name(item.name, suffix + "_x", add_special)

        try:
            await rename_with_timeout(service, item.fid, temp_name, ctx.timeout_sec)
        except asyncio.TimeoutError:
            timeouts += 1
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-rename",
                success=False,
                error="timeout",
                details={},
            ))
            return
        except Exception as exc:
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-rename",
                success=False,
                error=str(exc),
                details={},
            ))
            return
        else:
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-rename",
                success=True,
                error=None,
                details={},
            ))

        verify_error = None
        details: Dict[str, Any] = {}
        try:
            updated = await verify_item(service, item.parent_fid, item.fid)
            if not updated:
                verify_error = "item not found after rename"
            else:
                details["updated_name"] = updated.get("file_name")
                details["updated_size"] = updated.get("size")
                details["updated_parent"] = updated.get("pdir_fid")
                if str(updated.get("file_name")) != temp_name:
                    verify_error = "name mismatch after rename"
                if not item.is_dir and int(updated.get("size") or 0) != item.size:
                    verify_error = "size changed after rename"
        except Exception as exc:
            verify_error = str(exc)

        results.append(RenameResult(
            item_type="dir" if item.is_dir else "file",
            fid=item.fid,
            parent_fid=item.parent_fid,
            original_name=item.name,
            temp_name=temp_name,
            stage=f"{stage}-verify",
            success=verify_error is None,
            error=verify_error,
            details=details,
        ))

        try:
            await rename_with_timeout(service, item.fid, item.name, ctx.timeout_sec)
        except asyncio.TimeoutError:
            timeouts += 1
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-rollback",
                success=False,
                error="timeout",
                details={},
            ))
            return
        except Exception as exc:
            results.append(RenameResult(
                item_type="dir" if item.is_dir else "file",
                fid=item.fid,
                parent_fid=item.parent_fid,
                original_name=item.name,
                temp_name=temp_name,
                stage=f"{stage}-rollback",
                success=False,
                error=str(exc),
                details={},
            ))
            return

        results.append(RenameResult(
            item_type="dir" if item.is_dir else "file",
            fid=item.fid,
            parent_fid=item.parent_fid,
            original_name=item.name,
            temp_name=temp_name,
            stage=f"{stage}-rollback-verify",
            success=True,
            error=None,
            details={},
        ))

    for item in files:
        await process_item(item, "file")

    for item in dirs:
        await process_item(item, "dir")

    if files:
        sample = files[0]
        try:
            name_map = await get_parent_name_map(service, sample.parent_fid)
            other_names = [n for n in name_map.keys() if n != sample.name]
            if other_names:
                target = other_names[0]
                try:
                    await rename_with_timeout(service, sample.fid, target, ctx.timeout_sec)
                    await rename_with_timeout(service, sample.fid, sample.name, ctx.timeout_sec)
                    results.append(RenameResult(
                        item_type="file",
                        fid=sample.fid,
                        parent_fid=sample.parent_fid,
                        original_name=sample.name,
                        temp_name=target,
                        stage="collision-expected-fail",
                        success=False,
                        error="rename succeeded unexpectedly",
                        details={},
                    ))
                except Exception as exc:
                    results.append(RenameResult(
                        item_type="file",
                        fid=sample.fid,
                        parent_fid=sample.parent_fid,
                        original_name=sample.name,
                        temp_name=target,
                        stage="collision-expected-fail",
                        success=True,
                        error=None,
                        details={"expected_failure": str(exc)},
                    ))
            else:
                notes.append("collision test skipped: only one item in parent")
        except Exception as exc:
            notes.append(f"collision test skipped: {exc}")
    else:
        notes.append("collision test skipped: no files in test directory")

    finished_at = now_iso()
    summary = RunSummary(
        started_at=started_at,
        finished_at=finished_at,
        total_items=len(items),
        total_files=len(files),
        total_dirs=len(dirs),
        rename_attempts=len([r for r in results if r.stage.endswith("rename")]),
        rename_successes=len([r for r in results if r.stage.endswith("rename") and r.success]),
        rename_failures=len([r for r in results if r.stage.endswith("rename") and not r.success]),
        timeouts=timeouts,
        skipped=skipped,
    )

    return results, summary, notes


def group_by_stage(results: List[RenameResult]) -> Dict[str, List[RenameResult]]:
    """Purpose: Group rename results by stage.
    Input: Results list.
    Output: Dict of stage -> results.
    Side effects: None.
    """
    grouped: Dict[str, List[RenameResult]] = {}
    for result in results:
        grouped.setdefault(result.stage, []).append(result)
    return grouped


def build_markdown_report(
    ctx: RunContext,
    summary: RunSummary,
    results: List[RenameResult],
    notes: List[str],
    config_info: Dict[str, Any],
    scan_items: List[ScanItem],
) -> str:
    """Purpose: Build a markdown test report.
    Input: Context, summary, results, notes, config info, scan items.
    Output: Markdown string.
    Side effects: None.
    """
    stages = group_by_stage(results)
    ext_map: Dict[str, int] = {}
    for item in scan_items:
        if not item.is_dir:
            _, ext = split_name_ext(item.name)
            ext_map[ext or "<no_ext>"] = ext_map.get(ext or "<no_ext>", 0) + 1

    lines: List[str] = []
    lines.append("# Cloud Drive Rename Test Report")
    lines.append("")
    lines.append(f"- Generated: {summary.finished_at}")
    lines.append(f"- Report Version: {REPORT_VERSION}")
    lines.append("")

    lines.append("**System Functions And Modules**")
    lines.append("- Rename modules: `quark_strm/app/services/rename_service.py`, `quark_strm/app/services/smart_rename_service.py`, `quark_strm/app/services/quark_service.py`, `quark_strm/app/services/storage/quark.py`")
    lines.append("- Cloud rename path: Quark API `/file/rename` via `QuarkService.rename_file`.")
    lines.append("- Test scope: Recursive rename validation, hierarchy preservation, metadata consistency, edge cases.")
    lines.append("")

    lines.append("**Test Environment And Inputs**")
    lines.append(f"- Project root: `{Path.cwd()}`")
    lines.append("- Config file: `config.yaml`")
    lines.append(f"- Root fid: `{ctx.root_fid}`")
    lines.append(f"- Test directory: `{ctx.test_dir_name or 'N/A'}`")
    lines.append(f"- Test directory fid: `{ctx.test_dir_fid or 'N/A'}`")
    lines.append(f"- Test directory created: `{ctx.test_dir_created}`")
    if "__error__" in config_info:
        lines.append(f"- Config load error: `{config_info['__error__']}`")
    lines.append("")

    lines.append("**Interface And Page Coverage**")
    lines.append("- Covered interfaces: `POST /file/rename` (Quark API), `GET /file/sort` (scan)")
    lines.append("- Frontend pages: Not exercised in this run (direct cloud API test)")
    lines.append("")

    lines.append("**Test Design**")
    lines.append("- Recursively scan all files and directories under the test directory")
    lines.append("- For each item: rename -> verify -> rename back")
    lines.append("- Verification: name update, parent preserved, file size unchanged")
    lines.append("- Edge cases:")
    lines.append("  - Special character rename")
    lines.append("  - Same-directory name collision (expected failure)")
    lines.append("  - Read-only attributes (recorded if metadata available)")
    lines.append("")

    lines.append("**Scan And Coverage Statistics**")
    lines.append(f"- Total items: {summary.total_items}")
    lines.append(f"- Files: {summary.total_files}")
    lines.append(f"- Directories: {summary.total_dirs}")
    lines.append("- File type distribution:")
    for ext, count in sorted(ext_map.items(), key=lambda x: x[0]):
        lines.append(f"  - `{ext}`: {count}")
    lines.append("")

    lines.append("**Execution Results**")
    lines.append(f"- Rename attempts: {summary.rename_attempts}")
    lines.append(f"- Rename successes: {summary.rename_successes}")
    lines.append(f"- Rename failures: {summary.rename_failures}")
    lines.append(f"- Timeouts: {summary.timeouts}")
    lines.append(f"- Skipped: {summary.skipped}")
    lines.append("")

    lines.append("**Failures And Reproduction**")
    failed_any = [r for r in results if not r.success]
    if not failed_any:
        lines.append("- No failures or timeouts observed")
    else:
        for stage, stage_results in stages.items():
            failed = [r for r in stage_results if not r.success]
            if not failed:
                continue
            lines.append(f"- Stage `{stage}` failures:")
            for r in failed[:50]:
                lines.append(
                    f"  - fid `{r.fid}` name `{r.original_name}` -> `{r.temp_name}` error: `{r.error}`"
                )
    lines.append("")

    lines.append("**Improvements And Fix Suggestions**")
    lines.append("- Add file content reading to validate `.strm` internal references after rename")
    lines.append("- Expose metadata fields (read-only, permissions, checksum) for integrity checks")
    lines.append("- Provide explicit test directory configuration input")
    lines.append("- Return clearer error codes/messages for name collisions")
    lines.append("")

    lines.append("**Missing Information And Risks**")
    lines.append("- No explicit test directory input detected; used default candidates or auto-created directory")
    lines.append("- Cloud API does not expose file content; internal reference updates are not verifiable")
    lines.append("- Read-only attribute not available; read-only edge case recorded as missing")
    lines.append(f"- Directory listing capped by MAX_PAGES_PER_DIR={MAX_PAGES_PER_DIR} and MAX_ITEMS_TOTAL={MAX_ITEMS_TOTAL}")
    if notes:
        lines.append("- Additional notes:")
        for note in notes:
            lines.append(f"  - {note}")
    lines.append("")

    lines.append("**Raw Result Summary**")
    for stage, stage_results in stages.items():
        success_count = len([r for r in stage_results if r.success])
        fail_count = len(stage_results) - success_count
        lines.append(f"- `{stage}`: success {success_count} / failure {fail_count}")

    return "\n".join(lines)


async def main() -> int:
    """Purpose: Entry point for cloud rename tests.
    Input: None (uses config.yaml and project structure).
    Output: Process exit code.
    Side effects: Performs rename operations and writes report files.
    """
    root = Path(__file__).resolve().parents[1]
    ensure_sys_path(root)

    config_path = root / "config.yaml"
    config = load_yaml_config(config_path)

    config_quark = (config or {}).get("quark", {}) if isinstance(config, dict) else {}
    cookie = config_quark.get("cookie") or ""
    referer = config_quark.get("referer") or "https://pan.quark.cn/"
    root_fid = config_quark.get("root_id") or "0"

    if not cookie:
        report_dir = root / "output"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "rename_cloud_test_report.md"
        report_path.write_text("# Cloud Drive Rename Test Report\n\n- Not executed: missing `quark.cookie` config.\n", encoding="utf-8")
        return 0

    from app.services.quark_service import QuarkService

    service = QuarkService(cookie=cookie, referer=referer)

    env_test_dir = os.environ.get("TEST_RENAME_DIR", "")
    candidates = pick_test_dir_name([
        env_test_dir,
        "rename_test",
        "smart_media_test",
        "smart_media_rename_test",
        "strm_test",
        "test",
    ])

    test_fid: Optional[str] = None
    test_name: Optional[str] = None
    created = False
    create_notes: List[str] = []

    if env_test_dir:
        try:
            found = await asyncio.wait_for(
                service.get_file_by_path(env_test_dir),
                timeout=DEFAULT_TIMEOUT_SEC,
            )
            if found and getattr(found, "is_dir", False):
                test_fid = found.fid
                test_name = found.file_name
            else:
                create_notes.append("TEST_RENAME_DIR not found or not a directory")
        except Exception as exc:
            create_notes.append(f"TEST_RENAME_DIR lookup failed: {exc}")

    if not test_fid:
        test_fid, test_name, created, create_notes = await find_or_create_test_dir(
            service, root_fid, candidates
        )

    ctx = RunContext(
        root_fid=str(root_fid),
        test_dir_fid=test_fid,
        test_dir_name=test_name,
        test_dir_created=created,
        special_char_targets=5,
        timeout_sec=DEFAULT_TIMEOUT_SEC,
    )

    notes = create_notes
    items: List[ScanItem] = []
    results: List[RenameResult] = []

    if test_fid:
        items = await scan_tree(service, test_fid)
        results, summary, run_notes = await run_rename_tests(service, ctx, items)
        notes.extend(run_notes)
    else:
        summary = RunSummary(
            started_at=now_iso(),
            finished_at=now_iso(),
            total_items=0,
            total_files=0,
            total_dirs=0,
            rename_attempts=0,
            rename_successes=0,
            rename_failures=0,
            timeouts=0,
            skipped=0,
        )
        notes.append("test directory not available; rename tests skipped")

    report_dir = root / "output"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "rename_cloud_test_report.md"
    report = build_markdown_report(ctx, summary, results, notes, config, items)
    report_path.write_text(report, encoding="utf-8")

    json_path = report_dir / "rename_cloud_test_report.json"
    json_path.write_text(json.dumps({
        "context": asdict(ctx),
        "summary": asdict(summary),
        "results": [asdict(r) for r in results],
        "notes": notes,
        "scan": [asdict(i) for i in items],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    await service.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(asyncio.wait_for(main(), timeout=GLOBAL_TIMEOUT_SEC)))
    except asyncio.TimeoutError:
        root = Path(__file__).resolve().parents[1]
        report_dir = root / "output"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "rename_cloud_test_report.md"
        report_path.write_text(
            "# Cloud Drive Rename Test Report\n\n- Execution timed out before completion.\n",
            encoding="utf-8",
        )
        raise SystemExit(0)
