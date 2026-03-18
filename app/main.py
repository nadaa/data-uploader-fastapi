from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routers import file




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This method runs at the beginning and end of the FastAPI app.
    """
    print("App starting up...")
    await init_db()
    yield
    print("App shutting down...")    



app = FastAPI(lifespan=lifespan)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     )

app.include_router(file.router)



# Ensures FastAPI is up and running
@app.get("/healthcheck")
def root():
    return {"message": "FastAPI is running."}