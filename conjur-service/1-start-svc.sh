#!/bin/bash
poetry run uvicorn conjur-service:app	\
        --host 0.0.0.0 --port 9000	\
        --workers 2               	\
        --log-level info
