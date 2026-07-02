#!/bin/sh
# Stop the stack (keeps the database volume).
set -e
docker compose down
