build:
	docker build -t blockmate-app .

run:
	docker run -p 8000:8000 blockmate-app

stop:
	docker stop blockmate-container

remove:
	docker rm blockmate-container

dockerize: build run

help:
	@echo "Usage: make [COMMAND]"
	@echo "Commands:"
	@echo "  build        Build the Docker image"
	@echo "  run          Run the Docker container"
	@echo "  stop         Stop the Docker container"
	@echo "  remove       Remove the Docker container"
	@echo "  dockerize    Build and run the Docker container"

.PHONY: build run stop remove dockerize help
