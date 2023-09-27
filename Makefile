build:
	docker build -t blockmate-app .

unit-test:
	python -m unittest discover -s app/__tests__ -p "*_test.py" -v

run:
	docker run -p 8000:8000 blockmate-app

stop:
	CONTAINER_IDS=$$(docker ps -q --filter ancestor=blockmate-app); \
    for container_id in $${CONTAINER_IDS}; do \
        docker stop $${container_id}; \
    done

dockerize: build run

help:
	@echo "Usage: make [COMMAND]"
	@echo "Commands:"
	@echo "  build        Build the Docker image"
	@echo "  run          Run the Docker container"
	@echo "  stop         Stop the Docker container"
	@echo "  dockerize    Build and run the Docker container"

.PHONY: build run stop remove dockerize help
