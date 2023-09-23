#!/bin/bash

DOCKER_IMAGE="blockmate-app"

if [ -z "$(docker ps -qf "ancestor=$DOCKER_IMAGE")" ]; then
    echo "Docker container with image $DOCKER_IMAGE is not running."
    make build
    docker run -d -p 8000:8000 blockmate-app

    sleep 5
    echo "Docker container with image $DOCKER_IMAGE is now running."
else
    echo "Docker container with image $DOCKER_IMAGE is already running."
fi

URL="http://0.0.0.0:8000/check?address=0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"
NUM_REQUESTS=10

for ((i=1; i<=$NUM_REQUESTS; i++)); do
    response=$(curl -s "$URL")
    echo "Response $i: $response"
done

echo "Sent $NUM_REQUESTS requests to $URL"

make stop

echo "Stopped Docker container with image $DOCKER_IMAGE"
