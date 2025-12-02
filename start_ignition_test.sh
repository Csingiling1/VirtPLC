#!/usr/bin/env bash
# Quick helper to run only the Ignition Edge container for HMI testing
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Starting Ignition Edge (testing) from ${ROOT_DIR}"

# Run only the ignition-edge service defined in docker-compose.yml
docker compose up --no-build --force-recreate ignition-edge
