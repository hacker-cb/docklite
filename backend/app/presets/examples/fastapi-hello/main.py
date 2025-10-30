from fastapi import FastAPI

app = FastAPI(title="FastAPI Hello World")

@app.get("/")
def hello():
    return {
        "message": "Hello World from FastAPI!",
        "framework": "FastAPI"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

