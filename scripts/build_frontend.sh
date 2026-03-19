#!/bin/bash
# Build React frontend and copy to src/static for FastAPI serving.
set -e
cd "$(dirname "$0")/.."
echo "Building frontend..."
cd frontend
npm install
npm run build
echo "Copying build to src/static..."
mkdir -p ../src/static
cp -r dist/* ../src/static/
echo "Done. Frontend is in src/static/"
