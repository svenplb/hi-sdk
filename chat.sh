#!/bin/bash

# Start all services in detached mode
docker compose up -d

# Wait a moment for services to initialize
sleep 5

# Attach to the CLI container
docker attach plam_cli 