build:
	docker build -t blockmate-app .

run:
	docker run -p 8000:8000 blockmate-app

stop:
	CONTAINER_IDS=$$(docker ps -q --filter ancestor=blockmate-app); \
    for container_id in $${CONTAINER_IDS}; do \
        docker stop $${container_id}; \
    done

dockerize:
	build run

api-test:
	@sh api_test.sh

load-test:
	@sh load_test.sh


help:
	@echo "Usage: make [COMMAND]"
	@echo "Commands:"
	@echo "  build        Build the Docker image"
	@echo "  run          Run the Docker container"
	@echo "  stop         Stop the Docker container"
	@echo "  dockerize    Build and run the Docker container"
	@echo "  api-test     Perform api test using shell script"
	@echo "  load-test    Perform load test using shell script"

.PHONY: build run stop remove dockerize help
