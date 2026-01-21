#!/usr/bin/env bash

# Local folders
SRC_DIR="/home/olimpinf/django5.1/obi2025/media/files_to_send_to_grader"
DEST_DIR="/home/olimpinf/django5.1/obi2025/media/files_sent_to_grader"

# Remote destination
REMOTE_USER="olimpinf"
REMOTE_HOST="scangrader.com"
REMOTE_FLAGS=""
REMOTE_PATH="/home/olimpinf/files_obi"

# Ensure "sent" folder exists
#mkdir -p "$DEST_DIR"

# Iterate over all .zip files in SRC_DIR
for zipfile in "$SRC_DIR"/*.zip; do
    # Skip if no .zip files exist
    [[ -e "$zipfile" ]] || continue

    filename=$(basename "$zipfile")
    lockfile="${zipfile%.zip}.lock"

    echo "Processing $filename ..."

    # Create empty .lock file
    touch "$lockfile"

    # Copy .zip file
    rsync -avz ${REMOTE_FLAGS} "$zipfile" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"
    status_zip=$?

    # Copy .lock file
    rsync -avz ${REMOTE_FLAGS} "$lockfile" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"
    status_lock=$?

    # Remove local .lock file regardless
    rm -f "$lockfile"

    # If both transfers succeeded, move .zip file to "sent"
    if [[ $status_zip -eq 0 && $status_lock -eq 0 ]]; then
        mv "$zipfile" "$DEST_DIR/"
        echo "✅ $filename sent and moved to $DEST_DIR/"
    else
        echo "❌ Failed to send $filename, keeping it in $SRC_DIR"
    fi
done
