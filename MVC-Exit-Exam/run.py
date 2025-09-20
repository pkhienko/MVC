#!/usr/bin/env python

"""
- Works on Windows & macOS/Linux
- Creates .venv, installs deps, seeds CSV, sets SESSION_SECRET, starts Uvicorn
"""

import os
import sys
import subprocess
from pathlib import Path
import secrets
import shutil

REQUIREMENTS_LINES = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "jinja2>=3.1",
    "python-multipart>=0.0.9",
    "itsdangerous>=2.2",
]
APP_IMPORT = "app.main:app"
RELOAD = True
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = os.environ.get("PORT", "8000")
SESSION_ENV_KEY = "SESSION_SECRET"

def print_step(msg):
    print(f"\n==> {msg}")

def project_root() -> Path:
    return Path(__file__).resolve().parent

def venv_dir(root: Path) -> Path:
    return root / ".venv"

def venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    else:
        return venv / "bin" / "python"

def in_venv(python_path: Path) -> bool:
    try:
        return Path(sys.executable).resolve() == python_path.resolve()
    except Exception:
        return False

def ensure_requirements_txt(root: Path) -> Path:
    req = root / "requirements.txt"
    if not req.exists():
        req.write_text("\n".join(REQUIREMENTS_LINES) + "\n", encoding="utf-8")
    return req

def run(cmd, env=None):
    if isinstance(cmd, (list, tuple)):
        printable = " ".join(map(str, cmd))
    else:
        printable = str(cmd)
    print_step(f"Run: {printable}")
    subprocess.check_call(cmd, env=env)

def main():
    root = project_root()
    os.chdir(root)

    venv = venv_dir(root)
    if not venv.exists():
        print_step("Creating virtual environment (.venv)")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)])

    py = venv_python(venv)
    if not py.exists():
        raise SystemExit("Cannot find venv python at: " + str(py))

    if not in_venv(py):
        run([str(py), str(Path(__file__).resolve())])
        return

    req = ensure_requirements_txt(root)
    run([str(py), "-m", "pip", "install", "-U", "pip", "wheel", "setuptools"])
    run([str(py), "-m", "pip", "install", "-r", str(req)])

    seed_script = root / "scripts" / "seed.py"
    if seed_script.exists():
        run([str(py), str(seed_script)])
    else:
        print_step("Skip seeding: scripts/seed.py not found")

    env = os.environ.copy()
    if not env.get(SESSION_ENV_KEY):
        env[SESSION_ENV_KEY] = secrets.token_urlsafe(32)
        print_step(f"Set {SESSION_ENV_KEY} (dev)")

    uvicorn_cmd = [str(py), "-m", "uvicorn", APP_IMPORT, "--host", HOST, "--port", str(PORT)]
    if RELOAD:
        uvicorn_cmd.append("--reload")
    print_step(f"Server: http://{HOST}:{PORT}  (CTRL+C to stop)")
    subprocess.call(uvicorn_cmd, env=env)

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
