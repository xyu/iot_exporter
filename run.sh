#!/bin/bash
set -euf -o pipefail

cd "$(dirname "$0")"

touch requirements.txt
make

if [ -f iot_exporter.pid ]
then
	if ps "$(cat iot_exporter.pid)" | grep iot_exporter.py
	then
		echo "Stopping old server... "
		kill "$(cat iot_exporter.pid)"
		sleep 30
	fi
	rm iot_exporter.pid
fi

. .venv/bin/activate
python iot_exporter.py &> iot_exporter.log &

PID="$!"
echo "$PID" > iot_exporter.pid
echo "Running in background with PID $PID"
