from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"


class SsotError(RuntimeError):
    pass


@dataclass
class ChangeSet:
    writes: list[Path] = field(default_factory=list)
    deletes: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def extend(self, other: "ChangeSet") -> None:
        self.writes.extend(other.writes)
        self.deletes.extend(other.deletes)
        self.errors.extend(other.errors)

    @property
    def has_changes(self) -> bool:
        return bool(self.writes or self.deletes)

    @property
    def ok(self) -> bool:
        return not self.errors


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ssot_platforms_root(repo_root: Path) -> Path:
    return repo_root / "ai" / "ssot" / "platforms"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _assert_no_utf8_bom(path: Path, data: bytes) -> None:
    if data.startswith(UTF8_BOM):
        raise SsotError(f"UTF-8 BOM not allowed: {path}")


def _iter_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def _mirror_tree(
    *,
    src_dir: Path,
    dst_dir: Path,
    dry_run: bool,
    allow_delete: bool,
    enforce_src_no_bom: bool,
    exclude_delete_rel: list[Path] | None = None,
) -> ChangeSet:
    changes = ChangeSet()

    if not src_dir.exists():
        changes.errors.append(f"Missing SSOT source dir: {src_dir}")
        return changes

    if src_dir.is_file():
        changes.errors.append(f"Expected directory but got file: {src_dir}")
        return changes

    if dst_dir.exists() and dst_dir.is_file():
        changes.errors.append(f"Expected directory but got file: {dst_dir}")
        return changes

    src_files: dict[Path, Path] = {}
    for src_file in _iter_files(src_dir):
        rel = src_file.relative_to(src_dir)
        src_files[rel] = src_file

    dst_files: dict[Path, Path] = {}
    if dst_dir.exists():
        for dst_file in _iter_files(dst_dir):
            rel = dst_file.relative_to(dst_dir)
            dst_files[rel] = dst_file

    # Copy/update
    for rel, src_file in sorted(src_files.items(), key=lambda x: str(x[0])):
        dst_file = dst_dir / rel
        data = _read_bytes(src_file)
        if enforce_src_no_bom:
            try:
                _assert_no_utf8_bom(src_file, data)
            except SsotError as e:
                changes.errors.append(str(e))
                continue

        dst_data = dst_file.read_bytes() if dst_file.exists() else None
        if dst_data != data:
            changes.writes.append(dst_file)
            if not dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                dst_file.write_bytes(data)

    # Delete extras
    if allow_delete and dst_dir.exists():
        exclude_delete_rel = exclude_delete_rel or []
        for rel, dst_file in sorted(dst_files.items(), key=lambda x: str(x[0])):
            if rel in src_files:
                continue
            if any(_rel_is_under(rel, prefix) for prefix in exclude_delete_rel):
                continue
            changes.deletes.append(dst_file)
            if not dry_run:
                dst_file.unlink()

        # Prune empty directories (bottom-up)
        if not dry_run:
            for p in sorted(dst_dir.rglob("*"), key=lambda x: len(x.parts), reverse=True):
                if p.is_dir():
                    try:
                        next(p.iterdir())
                    except StopIteration:
                        p.rmdir()

    return changes


def _rel_is_under(rel: Path, prefix: Path) -> bool:
    try:
        rel.relative_to(prefix)
        return True
    except ValueError:
        return False


def _copy_file(
    *,
    src_file: Path,
    dst_file: Path,
    dry_run: bool,
    enforce_src_no_bom: bool,
) -> ChangeSet:
    changes = ChangeSet()

    if not src_file.exists():
        changes.errors.append(f"Missing SSOT source file: {src_file}")
        return changes

    data = _read_bytes(src_file)
    if enforce_src_no_bom:
        try:
            _assert_no_utf8_bom(src_file, data)
        except SsotError as e:
            changes.errors.append(str(e))
            return changes

    dst_data = dst_file.read_bytes() if dst_file.exists() else None
    if dst_data != data:
        changes.writes.append(dst_file)
        if not dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            dst_file.write_bytes(data)

    return changes


def _sync_repo_outputs(*, repo_root: Path, dry_run: bool) -> ChangeSet:
    ssot = _ssot_platforms_root(repo_root)
    if not ssot.exists():
        return ChangeSet(errors=[f"SSOT root not found: {ssot}"])

    changes = ChangeSet()
    enforce_src_no_bom = True

    # Direct mirrors (SSOT -> repo outputs)
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "trae" / "rules",
            dst_dir=repo_root / ".trae" / "rules",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "trae" / "skills",
            dst_dir=repo_root / ".trae" / "skills",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "anti" / "rules",
            dst_dir=repo_root / ".lingma" / "rules",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "anti" / "workflows",
            dst_dir=repo_root / ".agent" / "workflows",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "codex" / "skills",
            dst_dir=repo_root / ".codex" / "skills",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
            exclude_delete_rel=[Path("smart_media-agent") / "references" / "workflows"],
        )
    )

    # Explicit files (SSOT -> repo outputs)
    changes.extend(
        _copy_file(
            src_file=ssot / "codex" / "agents" / "AGENTS.md",
            dst_file=repo_root / "AGENTS.md",
            dry_run=dry_run,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )

    # Derived: make sure Codex skill embeds latest workflows references
    changes.extend(
        _mirror_tree(
            src_dir=ssot / "anti" / "workflows",
            dst_dir=repo_root
            / ".codex"
            / "skills"
            / "smart_media-agent"
            / "references"
            / "workflows",
            dry_run=dry_run,
            allow_delete=True,
            enforce_src_no_bom=enforce_src_no_bom,
        )
    )

    return changes


def _managed_codex_skill_dirs(repo_root: Path) -> list[Path]:
    skills_root = repo_root / ".codex" / "skills"
    if not skills_root.exists():
        return []
    managed: list[Path] = []
    for p in sorted(skills_root.iterdir(), key=lambda x: x.name):
        if not p.is_dir():
            continue
        if (p / "SKILL.md").exists():
            managed.append(p)
    return managed


def _sync_global_codex_skills(*, repo_root: Path, dry_run: bool) -> ChangeSet:
    changes = ChangeSet()

    managed = _managed_codex_skill_dirs(repo_root)
    if not managed:
        return changes

    global_root = Path.home() / ".codex" / "skills"
    if not global_root.exists() and not dry_run:
        global_root.mkdir(parents=True, exist_ok=True)

    for skill_dir in managed:
        changes.extend(
            _mirror_tree(
                src_dir=skill_dir,
                dst_dir=global_root / skill_dir.name,
                dry_run=dry_run,
                allow_delete=True,
                enforce_src_no_bom=True,
            )
        )

    return changes


def _print_changes(changes: ChangeSet) -> None:
    if changes.errors:
        print("Errors:", file=sys.stderr)
        for e in changes.errors:
            print(f"- {e}", file=sys.stderr)

    if changes.writes:
        print("Will write:")
        for p in changes.writes:
            print(f"- {p}")

    if changes.deletes:
        print("Will delete:")
        for p in changes.deletes:
            print(f"- {p}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="smart_media SSOT sync/check tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sync = sub.add_parser("sync", help="sync SSOT to platform directories")
    p_sync.add_argument(
        "--global",
        action="store_true",
        dest="global_install",
        help="also publish Codex skills to global ~/.codex/skills",
    )

    p_check = sub.add_parser("check", help="verify SSOT outputs are in sync")
    p_check.add_argument(
        "--global",
        action="store_true",
        dest="global_install",
        help="also verify global ~/.codex/skills is in sync",
    )

    args = parser.parse_args(argv)

    repo_root = _repo_root()

    if args.cmd == "sync":
        repo_changes = _sync_repo_outputs(repo_root=repo_root, dry_run=False)
        if not repo_changes.ok:
            _print_changes(repo_changes)
            return 2

        global_changes = ChangeSet()
        if args.global_install:
            global_changes = _sync_global_codex_skills(repo_root=repo_root, dry_run=False)
            if not global_changes.ok:
                _print_changes(global_changes)
                return 2

        total = ChangeSet()
        total.extend(repo_changes)
        total.extend(global_changes)
        if total.has_changes:
            print(f"Synced. Wrote {len(total.writes)} file(s), deleted {len(total.deletes)} file(s).")
        else:
            print("Already in sync.")
        return 0

    if args.cmd == "check":
        repo_changes = _sync_repo_outputs(repo_root=repo_root, dry_run=True)
        if not repo_changes.ok:
            _print_changes(repo_changes)
            return 2

        global_changes = ChangeSet()
        if args.global_install:
            global_changes = _sync_global_codex_skills(repo_root=repo_root, dry_run=True)
            if not global_changes.ok:
                _print_changes(global_changes)
                return 2

        total = ChangeSet()
        total.extend(repo_changes)
        total.extend(global_changes)
        if total.has_changes:
            _print_changes(total)
            return 1
        print("OK: SSOT outputs are in sync.")
        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
