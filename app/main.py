"""Main module for the FastAPI application."""
import uvicorn
from fastapi import FastAPI

from app.routes import check

app = FastAPI()

# include the router from the check_route module.
app.include_router(check.router, tags=["check"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
