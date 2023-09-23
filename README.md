# blockmate.io

## Task

Do an API, with this endpoints:

- GET /check?address=0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67 where address is an ethereum address, and which gets the risk details via https://docs.blockmate.io/reference/getaddressriskscoredetails, and returns a deduplicated list of category names from the response (from both own_categories, own_categories).

- To acquire a project token, use portal.blockmate.io, where you can create a new project. This token will be passed to the app via ENV.

- To acquire JWT token, use https://docs.blockmate.io/reference/userapi-authenticateproject. Reuse the JWT for more requests. Keep in mind, that JWT has expiration, and needs to be refreshed.

- Please do a rate-limit into the application for 100req/minute. Implement it in-memory, no need for external database like Redis.

- Create a Docker file, which builds the app and outputs a small Docker image.

# Usage

## Pre-requisites

- [Docker](https://www.docker.com/)
- [Make](https://www.gnu.org/software/make/manual/make.html)

## Limitations

The current setup with 1 unicorn worker and in-memory rate limiting is not suitable for production. It is only meant to be used for development and testing purposes. To make it production ready, we need to use a proper rate limiting solution like [redis](https://redis.io/).
