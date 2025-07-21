import uvicorn
from fastapi import FastAPI

from routes.app_route import router


app = FastAPI()

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8100)
