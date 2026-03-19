#!/bin/bash
# Run the Finance Agentic System API
cd "$(dirname "$0")/src"
exec uvicorn main:app --reload --host 0.0.0.0 --port 8000
