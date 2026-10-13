"""Run pytest against a temporary local PostgreSQL cluster, then stop and remove it."""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    pg_bin = os.getenv("PG_BIN")
    pg_ctl = shutil.which("pg_ctl", path=pg_bin) if pg_bin else shutil.which("pg_ctl")
    initdb = shutil.which("initdb", path=pg_bin) if pg_bin else shutil.which("initdb")
    if not pg_ctl or not initdb:
        print("Set PG_BIN to the PostgreSQL bin directory (containing initdb and pg_ctl).")
        return 1
    with tempfile.TemporaryDirectory(prefix="veriqo-postgres-") as folder:
        cluster = str(Path(folder) / "data")
        log = str(Path(folder) / "postgres.log")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        subprocess.run(
            [initdb, "-D", cluster, "-U", "veriqo_test", "-A", "trust", "--locale=C", "-E", "UTF8"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                pg_ctl,
                "-D",
                cluster,
                "-l",
                log,
                "-o",
                f"-h 127.0.0.1 -p {port} -k {folder}",
                "-w",
                "start",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        try:
            env = os.environ.copy()
            env["TEST_DATABASE_URL"] = f"postgresql://veriqo_test@127.0.0.1:{port}/postgres"
            return subprocess.run(
                [sys.executable, "-m", "pytest", *sys.argv[1:]], env=env
            ).returncode
        finally:
            subprocess.run(
                [pg_ctl, "-D", cluster, "-m", "fast", "-w", "stop"],
                check=True,
                stdout=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    raise SystemExit(main())
