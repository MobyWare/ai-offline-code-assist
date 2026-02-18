image:
	docker build -t ai-code-server:latest .

image/ides:
	docker build -f Dockerfile.jupyter -t ai-jupyter-ide:latest .
	docker build -f Dockerfile.vscode -t ai-vscode-ide:latest .

image/jupyter:
	docker build -f Dockerfile.jupyter -t ai-jupyter-ide:latest .

image/vscode:
	docker build -f Dockerfile.vscode -t ai-vscode-ide:latest .

up:
	docker compose up -d

down:
	docker compose down -v

clean/system:
	docker system prune -f --volumes
