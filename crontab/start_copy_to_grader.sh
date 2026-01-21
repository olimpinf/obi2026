#!/bin/bash


#!/bin/bash
# Wrapper for cron: ensures environment and prevents multiple runs

LOCKFILE="/tmp/copy_to_grader.lock"
SCRIPT="/home/olimpinf/django5.1/obi2025/crontab/copy_to_grader.sh"
LOGFILE="/home/olimpinf/django5.1/obi2025/crontab/LOG_COPY_TO_GRADER"

# Define a safe environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/home/olimpinf
export SHELL=/bin/bash

(
  flock -n 9 || { echo "=== $(date): already running ===" >> "$LOGFILE"; exit 1; }

  {
    echo "=== $(date): starting copy_to_grader ==="
    bash "$SCRIPT"
    echo "=== $(date): finished copy_to_grader ==="
  } >> "$LOGFILE" 2>&1

) 9>"$LOCKFILE"

