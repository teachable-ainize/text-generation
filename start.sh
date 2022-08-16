#!/bin/bash
service redis-server start

. /app/.venv/bin/activate

uvicorn server:app --host=0.0.0.0