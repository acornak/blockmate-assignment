#!/bin/bash

set -e

DOCKER_IMAGE="blockmate-app"
PORT=8000
NUM_REQUESTS=200
URL="http://0.0.0.0:$PORT/check?address=0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67"

function start_docker_container {
    if [ -z "$(docker ps -qf "ancestor=$DOCKER_IMAGE")" ]; then
        echo "Starting Docker container with image $DOCKER_IMAGE..."
        make build
        docker run -d -p $PORT:$PORT $DOCKER_IMAGE
        sleep 5
    else
        echo "Docker container with image $DOCKER_IMAGE is already running."
    fi
}

function make_requests {
    local total_time_200=0.0
    local count_200_responses=0
    local total_time_429=0.0
    local count_429_responses=0
    local total_time_non_200=0.0
    local count_non_200_responses=0

    for ((i=1; i<=$NUM_REQUESTS; i++)); do
        local random_eth_address="0x$(LC_ALL=C < /dev/urandom tr -dc 'a-f0-9' | fold -w 40 | head -n 1)"
        local output=$(curl -s -w "\nHTTP_CODE:%{http_code}\n%{time_total}" "${URL}?address=${random_eth_address}")
        local response=$(echo "$output" | sed '$d' | sed '$d')
        local http_code=$(echo "$output" | grep 'HTTP_CODE' | cut -d':' -f2)
        local elapsed_time=$(echo "$(echo "$output" | tail -n 1) * 1000" | bc -l)

        echo "Response $i for address $random_eth_address: $response"
        echo "Elapsed time: ${elapsed_time} ms"

        if [ "$http_code" -eq 200 ]; then
            total_time_200=$(echo "$total_time_200 + $elapsed_time" | bc -l)
            ((count_200_responses++))
        elif [ "$http_code" -eq 429 ]; then
            total_time_429=$(echo "$total_time_429 + $elapsed_time" | bc -l)
            ((count_429_responses++))
        else
            total_time_non_200=$(echo "$total_time_non_200 + $elapsed_time" | bc -l)
            ((count_non_200_responses++))
        fi
    done

    echo "Sent $NUM_REQUESTS requests"

    if [ $count_200_responses -gt 0 ]; then
        local average_time_200=$(echo "scale=2; $total_time_200 / $count_200_responses" | bc -l)
        echo "=================================================="
        echo "Average time for 200 responses: $average_time_200 ms"
    else
        echo "=================================================="
        echo "No 200 response received."
    fi

    if [ $count_429_responses -gt 0 ]; then
        local average_time_429=$(echo "scale=2; $total_time_429 / $count_429_responses" | bc -l)
        echo "=================================================="
        echo "Average time for 429 responses: $average_time_429 ms"
    else
        echo "=================================================="
        echo "No 429 response received."
    fi

    if [ $count_non_200_responses -gt 0 ]; then
        local average_time_non_200=$(echo "scale=2; $total_time_non_200 / $count_non_200_responses" | bc -l)
        echo "=================================================="
        echo "Average time for error responses: $average_time_non_200 ms"
        echo "=================================================="
    else
        echo "=================================================="
        echo "No error response received."
        echo "=================================================="
    fi
}

function stop_docker_container {
    make stop
    echo "Stopped Docker container with image $DOCKER_IMAGE"
}

start_docker_container
make_requests
# stop_docker_container
