import os
from dotenv import load_dotenv

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from database import create_tables, delete_tables
from router import routers


# Удаление и создание таблиц при запуске приложения
async  def reload_db():
    await delete_tables()
    print("Таблицы удалены")
    await create_tables()
    print("Таблицы созданы")

@asynccontextmanager
async  def lifespan(app: FastAPI):
    #await reload_db() # Применить при первом запуске
    yield
    print("Выключение")


app = FastAPI(title = "Test_Rigkov",
              description = "test task",
              docs_url = "/",
              lifespan = lifespan)


for rout in routers:
    app.include_router(rout)

if __name__ == "__main__":
    load_dotenv()
    host = os.getenv("IP")
    port = int(os.getenv("PORT"))
    try:
        uvicorn.run("main:app", host = host, port = port, reload = True)
    finally:
        print("Приложение было запущено на хосте ", host)