image:
	docker build -t ai-code-server:latest .

clean/system:
	docker system prune -f --volumes
