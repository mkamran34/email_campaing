#!/bin/bash
# Start the email schedule runner service

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Check if scheduler is already running
if ps aux | grep "[p]ython schedule_runner.py" > /dev/null; then
    echo "Scheduler is already running"
    ps aux | grep "[p]ython schedule_runner.py"
    exit 0
fi

# Start scheduler in background
echo "Starting email scheduler..."
nohup python schedule_runner.py > scheduler.log 2>&1 &
SCHEDULER_PID=$!

echo "Scheduler started with PID: $SCHEDULER_PID"
echo "Logs are being written to scheduler.log"
echo ""
echo "To monitor logs: tail -f scheduler.log"
echo "To stop scheduler: kill $SCHEDULER_PID"
