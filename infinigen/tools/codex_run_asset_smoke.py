import argparse
import csv
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ONE_SCRIPT = REPO_ROOT / "tools" / "codex_asset_smoke_one.py"


@dataclass(frozen=True)
class AssetCase:
    group: str
    kind: str
    profile: str
    pathspec: str


def load_list(path):
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line[: line.index("#")].strip()
        if line:
            rows.append(line)
    return rows


def slug(text):
    keep = []
    for ch in text.split(".")[-1]:
        keep.append(ch if ch.isalnum() else "_")
    return "".join(keep).strip("_") or "asset"


def build_cases(groups):
    specs = {
        "indoor_meshes": ("mesh", "indoor", "tests/assets/list_indoor_meshes.txt"),
        "nature_meshes": ("mesh", "nature", "tests/assets/list_nature_meshes.txt"),
        "materials": ("material", "indoor", "tests/assets/list_materials.txt"),
        "materials_deprecated": (
            "material_deprecated",
            "nature",
            "tests/assets/list_materials_deprecated_interface.txt",
        ),
        "scatters": ("scatter", "nature", "tests/assets/list_scatters.txt"),
    }
    selected = specs.keys() if not groups else groups
    cases = []
    seen = set()
    for group in selected:
        kind, profile, rel = specs[group]
        for pathspec in load_list(REPO_ROOT / rel):
            key = (group, pathspec)
            if key in seen:
                continue
            seen.add(key)
            cases.append(AssetCase(group, kind, profile, pathspec))
    return cases


def append_jsonl(path, row):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "index",
                "group",
                "kind",
                "pathspec",
                "status",
                "started_at",
                "finished_at",
                "seconds",
                "returncode",
                "out_dir",
                "log",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_status(path, row):
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")


def run_case(case, index, args, output_root, logs_dir):
    name = slug(case.pathspec)
    out_dir = output_root / case.group / f"{index:03d}_{name}"
    log_path = logs_dir / f"{index:03d}_{case.group}_{name}.log"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    status_path = out_dir / "status.json"
    started_at = datetime.now().isoformat(timespec="seconds")
    cmd = [
        sys.executable,
        str(ONE_SCRIPT),
        "--kind",
        case.kind,
        "--profile",
        case.profile,
        "--pathspec",
        case.pathspec,
        "--out-dir",
        str(out_dir),
        "--seed",
        "0",
        "--distance",
        str(args.distance),
        "--scatter-subdivisions",
        str(args.scatter_subdivisions),
        "--scatter-density",
        str(args.scatter_density),
    ]
    if args.autopack:
        cmd.append("--autopack")
    row = {
        "index": index,
        "group": case.group,
        "kind": case.kind,
        "pathspec": case.pathspec,
        "status": "running",
        "started_at": started_at,
        "finished_at": "",
        "seconds": "",
        "returncode": "",
        "out_dir": str(out_dir),
        "log": str(log_path),
    }
    write_status(status_path, row)
    case_started = time.time()
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write(f"START {started_at} {case.pathspec}\n")
        log.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=REPO_ROOT,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            returncode = proc.wait(timeout=args.timeout)
            status = "pass" if returncode == 0 else "fail"
        except subprocess.TimeoutExpired:
            proc.kill()
            returncode = "timeout"
            status = "timeout"
            log.write("\nTIMEOUT\n")
            log.flush()
    finished_at = datetime.now().isoformat(timespec="seconds")
    row.update(
        status=status,
        finished_at=finished_at,
        seconds=round(time.time() - case_started, 2),
        returncode=returncode,
    )
    write_status(status_path, row)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout", default=300, type=int)
    parser.add_argument("--workers", default=1, type=int)
    parser.add_argument("--distance", default=50, type=float)
    parser.add_argument("--scatter-subdivisions", default=160, type=int)
    parser.add_argument("--scatter-density", default=0.15, type=float)
    parser.add_argument("--autopack", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--groups", nargs="*", default=[])
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--limit", default=0, type=int)
    args = parser.parse_args()

    output_root = args.output_root.resolve()
    logs_dir = output_root / "logs"
    output_root.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_root / "progress.jsonl"
    report_path = output_root / "report.csv"
    summary_path = output_root / "summary.json"

    cases = build_cases(args.groups)
    if args.limit > 0:
        cases = cases[args.start : args.start + args.limit]
    elif args.start:
        cases = cases[args.start :]
    indexed_cases = list(enumerate(cases, start=args.start))

    if args.resume:
        filtered = []
        skipped = 0
        for index, case in indexed_cases:
            status_path = (
                output_root / case.group / f"{index:03d}_{slug(case.pathspec)}" / "status.json"
            )
            if status_path.exists():
                try:
                    status = json.loads(status_path.read_text(encoding="utf-8")).get("status")
                except Exception:
                    status = None
                if status in {"pass", "fail", "timeout"}:
                    skipped += 1
                    continue
            filtered.append((index, case))
        print(f"Resume mode skipped {skipped} completed cases", flush=True)
        indexed_cases = filtered

    counts = {"pass": 0, "fail": 0, "timeout": 0}
    rows = []
    if args.resume and report_path.exists():
        with report_path.open("r", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                rows.append(row)
                status = row.get("status")
                if status in counts:
                    counts[status] += 1
        rows.sort(key=lambda item: int(item["index"]))
    existing_rows = len(rows)
    started = time.time()
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(run_case, case, index, args, output_root, logs_dir)
            for index, case in indexed_cases
        ]
        for future in as_completed(futures):
            row = future.result()
            with lock:
                counts[row["status"]] += 1
                rows.append(row)
                rows.sort(key=lambda item: int(item["index"]))
                append_jsonl(progress_path, row)
                write_csv(report_path, rows)
                summary = {
                    "total": existing_rows + len(indexed_cases),
                    "completed": len(rows),
                    "running": len(indexed_cases) - (len(rows) - existing_rows),
                    "counts": counts,
                    "elapsed_seconds": round(time.time() - started, 2),
                    "last": row,
                }
                summary_path.write_text(
                    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(
                    f"[{len(rows)}/{existing_rows + len(indexed_cases)}] {row['status'].upper()} "
                    f"{row['group']} {row['pathspec']} ({row['seconds']}s)",
                    flush=True,
                )

    summary = {
        "total": existing_rows + len(indexed_cases),
        "completed": len(rows),
        "counts": counts,
        "elapsed_seconds": round(time.time() - started, 2),
        "report": str(report_path),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 1 if counts["fail"] or counts["timeout"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
