import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
GENERATED_PY_DIR = BASE_DIR / "more_realistic_generated_py"
GENERATED_DATA_DIR = BASE_DIR / "generated_data"
GENERATED_PLOTS_DIR = BASE_DIR / "generated_plots"


def main() -> int:
    GENERATED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not GENERATED_PY_DIR.exists():
        print(f"Directory not found: {GENERATED_PY_DIR}", file=sys.stderr)
        return 1

    py_files = sorted(GENERATED_PY_DIR.glob("*.py"))
    if not py_files:
        print(f"No .py files found in {GENERATED_PY_DIR}", file=sys.stderr)
        return 1

    success = 0
    failed = 0

    for py_file in py_files:
        print(f"Running {py_file.name}...")

        try:
            result = subprocess.run(
                [sys.executable, str(py_file)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout.strip():
                print(result.stdout.strip())

            if result.returncode == 0:
                print(f"[OK] {py_file.name} completed successfully")
                success += 1
            else:
                print(f"[ERROR] {py_file.name} failed with code {result.returncode}", file=sys.stderr)
                if result.stderr.strip():
                    print(result.stderr.strip(), file=sys.stderr)
                failed += 1

        except Exception as exc:
            print(f"Exception while running {py_file.name}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nDone. Success={success}, Failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())