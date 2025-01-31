#!/bin/env bash

if [ -n "$SCALINGO_API_TOKEN" ]; then
    install-scalingo-cli
    scalingo login --api-token $SCALINGO_API_TOKEN
    scalingo --app apilos-siap-integration restart worker
else
    echo "SCALINGO_API_TOKEN is not set"
fi