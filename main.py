import os
import dotenv

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/", status_code = 200)
def get_start():
    return {"Initial": "Project is created"}

if __name__ == "__main__":
    dotenv.load_dotenv()
    is_docker = os.getenv("DOCKER") # String
    if is_docker == "Fasle":
        host = "127.0.0.0"
    elif is_docker == "True":
        host = "0.0.0.0"
    else:
        host = os.getenv("PROD")
        try:
            uvicorn.run("main:app", host = "127.0.0.1")
        except ValueError:
            print(" Неверный IP или порт хоста")
