#!/usr/bin/env python3
# ============================================
#  scripts/check_syntax.py - local syntax guard for all .py files
#  Run before every commit. Fails (exit 1) if any file does not parse.
#  Used by CI as the first gate.
# ============================================
import ast
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    py_files = sorted(
        p for p in root.rglob("*.py")
        if "__pycache__" not in p.parts
    )
    if not py_files:
        print("[check_syntax] no .py files found under", root)
        return 1

    errors = []
    for p in py_files:
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except SyntaxError as e:
            errors.append(f"{p.relative_to(root)}: line {e.lineno}: {e.msg}")

    if errors:
        print(f"[check_syntax] FAILED ({len(errors)} file(s)):")
        for e in errors:
            print(" ", e)
        return 1

    print(f"[check_syntax] OK: {len(py_files)} .py files parsed cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
