#!/bin/bash
echo "Stopping all open-gpx services..."

lsof -ti:8989 | xargs kill -9 2>/dev/null && echo "GraphHopper stopped (port 8989)" || echo "GraphHopper was not running"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "Backend stopped (port 8000)" || echo "Backend was not running"
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "Frontend stopped (port 5173)" || echo "Frontend was not running"

echo "Done."
