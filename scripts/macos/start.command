#!/bin/bash
PROJECT_DIR="/Users/galfano/code/open-gpx"
GH_DIR="$HOME/graphhopper-data"

echo "Starting GraphHopper..."
osascript <<EOF
tell application "Terminal"
  do script "cd $GH_DIR && java -jar graphhopper-web-10.0.jar server config.yml"
end tell
EOF

echo "Starting backend..."
osascript <<EOF
tell application "Terminal"
  do script "cd $PROJECT_DIR/backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
end tell
EOF

echo "Starting frontend..."
osascript <<EOF
tell application "Terminal"
  do script "cd $PROJECT_DIR/frontend && npm run dev"
end tell
EOF

echo "Opening browser in 5 seconds..."
sleep 5 && open http://localhost:5173
