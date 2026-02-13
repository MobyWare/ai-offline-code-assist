# Use the official Ollama image as the base
FROM ollama/ollama:latest

# Set environment variables for the API
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS="*"

# Intermediate step to pull the model during the build
# We start the server in the background, wait for it to init, pull the model, then kill it.
RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama pull deepseek-coder:6.7b && \
    pkill ollama

# Expose the REST API port
EXPOSE 11434

# Ensure the server starts when the container runs
ENTRYPOINT ["ollama", "serve"]
