#!/bin/bash

# Start Ollama in background
apt-get update && apt-get install -y curl

ollama serve &

# Wait for Ollama API to become ready
until curl -s http://localhost:11434; do
  echo "Waiting for Ollama to be ready..."
  sleep 2
done

# Pull the models
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3:8b"}'
curl -X POST http://localhost:11434/api/pull -d '{"name": "nomic-embed-text:v1.5"}'

# Keep foreground process to hold container open
wait
