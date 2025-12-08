#!/bin/sh
# init-ollama.sh
# Waits for Ollama to be ready and pulls the requested model

set -e

echo "Waiting for Ollama service at $OLLAMA_HOST..."

# Wait for Ollama API to be responsive
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null; do
    echo "Waiting for Ollama..."
    sleep 5
done

echo "Ollama is ready."

if [ -z "$OLLAMA_MODEL" ]; then
    echo "No OLLAMA_MODEL environment variable set. Skipping pull."
    exit 0
fi

echo "Checking if model '$OLLAMA_MODEL' exists..."

# Check if model already exists
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"$OLLAMA_MODEL\""; then
    echo "Model '$OLLAMA_MODEL' already exists. Skipping pull."
else
    echo "Model '$OLLAMA_MODEL' not found. Pulling..."
    # Pull the model
    curl -X POST "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$OLLAMA_MODEL\"}"
    echo "Model '$OLLAMA_MODEL' pulled successfully."
fi

echo "Ollama initialization complete."
