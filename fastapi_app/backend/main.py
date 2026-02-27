import sys
import os
sys.path.append(os.path.abspath("."))

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings

from database import reload_db
from core.modules import db_helper

from router import routers
#from api import routers #TODO


@asynccontextmanager
async  def lifespan(app: FastAPI):
    #startup
    #await reload_db()
    print("Старт приложения")
    yield
    #shutdown
    print("dispose engine")
    await db_helper.dispose()
    print("Выключение")


main_app = FastAPI(title = "Test_Rigkov",
              description = "test task",
              docs_url = "/",
              lifespan = lifespan)

for rout in routers:
    main_app.include_router(rout, prefix = settings.api.prefix)

if __name__ == "__main__":
    try:
        uvicorn.run("main:main_app", 
                    host = settings.run.host, 
                    port = settings.run.port, 
                    reload = True)
    except:
        print("При запуске приложения, произошла ошибка")
