#!/bin/bash

set -e

DOCKER_IMAGE="blockmate-app"
PORT=8000
NUM_REQUESTS=120
URL="http://0.0.0.0:$PORT/check"

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
    local count_200=0
    local count_429=0
    local count_err=0

    local total_time_200=0.0
    local total_time_429=0.0
    local total_time_err=0.0


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
            ((count_200++))
        elif [ "$http_code" -eq 429 ]; then
            total_time_429=$(echo "$total_time_429 + $elapsed_time" | bc -l)
            ((count_429++))
        else
            total_time_err=$(echo "$total_time_err + $elapsed_time" | bc -l)
            ((count_err++))
        fi
    done

    echo "=================================================="
    echo "Sent $NUM_REQUESTS requests"

    if [ $count_200 -gt 0 ]; then
        local average_time_200=$(echo "scale=2; $total_time_200 / $count_200" | bc -l)
        echo "=================================================="
        echo "Number of 200 responses: $count_200 / $NUM_REQUESTS"
        echo "Average time for 200 responses: $average_time_200 ms"
    else
        echo "=================================================="
        echo "No 200 response received."
    fi

    if [ $count_429 -gt 0 ]; then
        local average_time_429=$(echo "scale=2; $total_time_429 / $count_429" | bc -l)
        echo "=================================================="
        echo "Number of 429 responses: $count_429 / $NUM_REQUESTS"
        echo "Average time for 429 responses: $average_time_429 ms"
    else
        echo "=================================================="
        echo "No 429 response received."
    fi

    if [ $count_err -gt 0 ]; then
        local average_time_err=$(echo "scale=2; $total_time_err / $count_err" | bc -l)
        echo "=================================================="
        echo "Number of error responses: $count_err / $NUM_REQUESTS"
        echo "Average time for error responses: $average_time_err ms"
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
stop_docker_container
