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

log "Copying SQLite database."
cp "$APP_ROOT/db.sqlite3" "$SQLITE_BACKUP_DIR/${TS}-db.sqlite3"

log "Gifts backup completed successfully."