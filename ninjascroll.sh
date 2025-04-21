#!/bin/bash
set -euo pipefail
# Hayato the Code Ninja: A shadow in the moonlight of your monitor,
# executing with precision and minimal disruption.
#
# Purpose:
# This script supports our Code Ninja workflow with minimal API calls.
# It accepts a commit message and a list of files.
# For each file, it sends a pushover notification (with optional sound support)
# in the background. All provided non-markdown files are then added, committed, and pushed to the repository.
#
# Usage:
#   ./ninjascroll.sh [--page] "<commit-message>" <file1> [file2 ...]    
# # if you're not certain about plan or would like second optionion, page user by addeing argument:
# # ./ninjascroll.sh --page "<commit-message>" <file1> [file2 ...]
#
# Example:
#   ./ninjascroll.sh --page "Refined training results" report.md update.py notes.md
#
# Code Ninja Creed:
# • Strike with precision, only altering what must be altered.
# • Maintain minimal impact—leave no trace but your commit.
# • Document your moves and ensure each strike is surgically planned.
# • Your task is never complete; always prepare for the next challenge.

# Check for optional --page flag
PAGE=false
if [ "$1" = "--page" ]; then
    PAGE=true
    shift
fi

# Kill any running ninja_not_idle process
if [ -f /tmp/ninja_not_idle.pid ]; then
    IDLE_PID=$(cat /tmp/ninja_not_idle.pid)
    if ps -p $IDLE_PID > /dev/null; then
        echo "Killing existing ninja_not_idle process (PID: $IDLE_PID)"
        kill $IDLE_PID 2>/dev/null || true
    fi
    rm -f /tmp/ninja_not_idle.pid
fi

# Check if at least two arguments remain: a commit message and one or more files.
if [ $# -lt 2 ]; then
    echo "Usage: $0 [--page] <commit-message> <file1> [file2 ...]"
    exit 1
fi

# Capture the commit message and shift the parameters so that $@ contains only the file list.
COMMIT_MESSAGE="$1"
shift

# Initialize array for non-markdown files
NON_MD_FILES=()
MD_FILES=()

# Process each file in the list.
for FILE in "$@"; do
    if [ ! -f "$FILE" ]; then
        echo "Error: File '$FILE' not found. Halting ninja operations."
        exit 1
    fi

    # For each Markdown file, send a pushover notification with optional sound paging.
    if [[ "$FILE" == *.md ]]; then
        # Rename markdown file by prefixing timestamp to filename
        PREFIX=$(date +"%m-%d-%H%M-")
        DIR=$(dirname "$FILE")
        BASE=$(basename "$FILE")
        NEWFILE="$DIR/${PREFIX}${BASE}"
        mv "$FILE" "$NEWFILE"
        FILE="$NEWFILE"
        MD_FILES+=("$FILE")
        SUBJECT="Hayato: $COMMIT_MESSAGE"
        if [ "$PAGE" = true ]; then
            echo "Debug: Running pushover_test.py with file=$FILE, subject=$SUBJECT and --page flag"
            python3 "$(dirname "$0")/pushover_test.py" "$FILE" "$SUBJECT" --page
            echo "Ninja-alert dispatched for Markdown file: $FILE with paging (sound alert)."
        else
            echo "Debug: Running pushover_test.py with file=$FILE, subject=$SUBJECT"
            python3 "$(dirname "$0")/pushover_test.py" "$FILE" "$SUBJECT"
            echo "Ninja-alert dispatched for Markdown file: $FILE."
        fi
    else
        NON_MD_FILES+=("$FILE")
    fi
done

# Only proceed with git operations if there are non-markdown files or Markdown files
if [ ${#NON_MD_FILES[@]} -gt 0 ] || [ ${#MD_FILES[@]} -gt 0 ]; then
    # Stage all the non-markdown files and Markdown files
    git add "${NON_MD_FILES[@]}" "${MD_FILES[@]}"

    # Commit the changes with your commit message
    git commit -m "$COMMIT_MESSAGE"

    # Push the commit to the repository
    git push

    if [ "$PAGE" = true ]; then
        echo "Hayato the Code Ninja: Paging alert dispatched. Non-markdown files and Markdown files have been committed and pushed. Continue on your ninja cycle by testing the changes with ninjatest.sh."
    else
        echo "Hayato the Code Ninja: Non-markdown files and Markdown files have been committed and pushed. Remain ever vigilant—refine your techniques, move onward in the cycle by testing the changes with ninjatest.sh."
    fi
else
    if [ "$PAGE" = true ]; then
        echo "Hayato the Code Ninja: Paging alert dispatched. No non-markdown files or Markdown files to commit."
    else
        echo "Hayato the Code Ninja: No non-markdown files or Markdown files to commit. Notifications sent for all files."
    fi
fi

# Start the ninja_not_idle script
echo "Starting ninja_not_idle script to monitor agent activity..."
nohup ./ninja_not_idle.sh > /dev/null 2>&1 &
echo "If no activity occurs for 1 hour, a notification will be sent."

exit 0