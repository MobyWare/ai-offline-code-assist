c = get_config()

# Disable authentication
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.disable_check_xsrf = True

# Pre-configure Jupyter AI
# Note: Values match the internal Docker service names
c.AiExtension.default_language_model = "ollama:deepseek-coder:6.7b"
c.AiExtension.language_model_base_url = "http://ollama-gpu:11434"