#!/bin/bash
# Stop the email schedule runner service

echo "Stopping email scheduler..."

# Find and kill scheduler processes
PIDS=$(ps aux | grep "[p]ython schedule_runner.py" | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "No scheduler process found"
    exit 0
fi

for PID in $PIDS; do
    echo "Killing scheduler process $PID..."
    kill -9 $PID 2>/dev/null
done

echo "Scheduler stopped"
