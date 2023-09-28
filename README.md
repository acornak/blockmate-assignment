# Blockmate.io Risk Assessment API

## Task

Do an API, with this endpoints:

- GET /check?address=0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67 where address is an ethereum address, and which gets the risk details via https://docs.blockmate.io/reference/getaddressriskscoredetails, and returns a deduplicated list of category names from the response (from both own_categories, own_categories).

- To acquire a project token, use portal.blockmate.io, where you can create a new project. This token will be passed to the app via ENV.

- To acquire JWT token, use https://docs.blockmate.io/reference/userapi-authenticateproject. Reuse the JWT for more requests. Keep in mind, that JWT has expiration, and needs to be refreshed.

- Please do a rate-limit into the application for 100req/minute. Implement it in-memory, no need for external database like Redis.

- Create a Docker file, which builds the app and outputs a small Docker image.


# Solution
## Introduction

This API service is designed to fetch and analyze the risk data of Ethereum addresses using Blockmate.io's API. It is developed in Python with FastAPI and incorporates rate-limiting features. The application is Dockerized for easy deployment and scalability.

## Endpoints

- ```GET /check?address=<Ethereum_Address>``` - Returns deduplicated risk categories associated with a given Ethereum address. It queries data from Blockmate.io and processes the received response to deduplicate the risk categories from both own_categories and source_of_funds_categories.

## Features

- **JWT Token Management**: Acquires and reuses JWT from Blockmate.io. Refreshes JWT upon expiration.
- **Rate Limiting**: 100 requests per minute (potentially per IP), implemented in-memory.
- **Dockerized**: Lightweight Docker image (~330 MB) for easy deployment.

## Pre-requisites

- [Docker](https://www.docker.com/)
- [Make](https://www.gnu.org/software/make/manual/make.html)

## Quickstart

- ```make dockerize``` to build and run the docker image
- ```make stop``` to stop the docker container
- ```make api-test``` to perform API test
- ```make load-test``` to perform load test

**API test** will perform 120 requests non-concurrently on randomly generated ETH addresses, logs every response and calculates average times.

**Load test** will perform 120 requests in 12 batches per 10 concurrent requests, logs every response and response time.

## API Documentation

FastAPI provides a Swagger UI for API documentation. It can be accessed at ```http://localhost:8000/docs```

## Testing and Coverage

- Run unit tests: ```poetry run coverage run -m pytest app/__tests__ -v```
- Generate coverage report: ```poetry run coverage report```
- Generate HTML coverage report: ```poetry run coverage html``` (HTML report will be generated in ```htmlcov``` folder)

## Limitations

- **In-memory Rate Limiting** The current rate-limiting mechanism is in-memory, making it unsuitable for production-level, distributed systems.

- **Single Worker** The current setup uses a single worker. This is not suitable for production-level, distributed systems.

## Future Improvements

- **Redis Rate Limiting** To make the application production-ready, we need to use a proper rate-limiting solution like [Redis](https://redis.io/). This is prerequisite for horizontal scaling.

- **Multiple Workers** To make the application production-ready, we need to use multiple workers. Currently, due to the in-memory rate-limiting mechanism, we can only use a single worker, as multiple workers will not share the same memory space.

- **Caching** To improve performance, we can cache the responses from Blockmate.io. This will reduce the number of requests to Blockmate.io and improve response times. Caching in-memory is not suitable for production-level, distributed systems. We can use a distributed cache like [Redis](https://redis.io/) or [Memcached](https://memcached.org/) for this purpose.
