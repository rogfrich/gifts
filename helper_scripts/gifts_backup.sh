#!/usr/bin/env bash
set -euo pipefail

#
# Creates timestamped Gifts backups:
# - CSV exports from exporter.py
# - SQLite database copy
#
# Intended to be executed daily on the production server.
# Assumes the production deployment layout under /srv/gifts.
#

APP_ROOT="/srv/gifts/app"
PROJECT_ROOT="/srv/gifts"
BACKUP_ROOT="${PROJECT_ROOT}/backups"

CSV_BACKUP_DIR="${BACKUP_ROOT}/csv"
SQLITE_BACKUP_DIR="${BACKUP_ROOT}/sqlite"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

log() {
  echo "[$(timestamp)] $*"
}

trap 'log "ERROR: Gifts backup failed."' ERR

TS=$(date +"%Y-%m-%d-%H%M")

log "Starting Gifts backup."

mkdir -p "$CSV_BACKUP_DIR"
mkdir -p "$SQLITE_BACKUP_DIR"

log "Activating virtual environment."
cd "$PROJECT_ROOT"
source .venv/bin/activate

log "Running CSV exporter."
python3 "$APP_ROOT/utils/exporter.py" "$CSV_BACKUP_DIR/"

log "Timestamping CSV exports as ${TS}."
mv "$CSV_BACKUP_DIR/users.csv" "$CSV_BACKUP_DIR/${TS}-users.csv"
mv "$CSV_BACKUP_DIR/wishes.csv" "$CSV_BACKUP_DIR/${TS}-wishes.csv"

log "Creating and verifying a consistent SQLite backup."
python3 - "$APP_ROOT/db.sqlite3" "$SQLITE_BACKUP_DIR/${TS}-db.sqlite3" <<'PYTHON'
import os
import sqlite3
import sys
import time
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

source = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
deadline = time.monotonic() + 60


def progress(status, remaining, total):
    if time.monotonic() > deadline:
        raise TimeoutError("SQLite backup exceeded 60 seconds")


with TemporaryDirectory(prefix=".gifts-backup-", dir=target.parent) as scratch:
    staged = Path(scratch) / "db.sqlite3"
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src:
        with closing(sqlite3.connect(staged)) as dst:
            src.backup(dst, pages=256, progress=progress, sleep=0.1)
            if dst.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise RuntimeError("SQLite backup failed its integrity check")
            if dst.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise RuntimeError("SQLite backup contains foreign-key violations")
    os.replace(staged, target)

print(f"Verified SQLite backup: {target}")
PYTHON

log "Gifts backup completed successfully."