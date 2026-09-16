#!/usr/bin/env python
import os
import sys
from pathlib import Path


def use_project_virtualenv() -> None:
    """Re-run with the local virtualenv when global Python invoked this script."""

    if sys.prefix != sys.base_prefix:
        return

    project_root = Path(__file__).resolve().parent
    virtualenv_python = (
        project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if virtualenv_python.exists() and Path(sys.executable).resolve() != virtualenv_python.resolve():
        os.execv(
            str(virtualenv_python),
            [str(virtualenv_python), str(Path(__file__).resolve()), *sys.argv[1:]],
        )


def main() -> None:
    use_project_virtualenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "internship_tracking.settings.development")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
