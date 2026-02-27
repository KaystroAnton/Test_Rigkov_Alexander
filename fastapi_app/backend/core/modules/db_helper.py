from  fastapi_app.backend.core.config import settings 

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = False, # all statments logs
            echo_pool: bool = False, # connection pool logs
            pool_size: bool = 5, # number of connections to keep open inside the connection pool
            max_overflow: int = 10, # number of alowes overflow connections
            )-> None:
    
        self.engine = create_async_engine( 
        url=url,
        echo = echo,
        echo_pool =echo_pool,
        pool_size = pool_size,
        max_overflow = max_overflow,
        )

        self.sessions = async_sessionmaker( 
            autoflush = False,
            autocommit = False,
            expire_on_commit= False,
        )
    
    async def dispose(self) -> None:
        await self.engine.dispose()
    
    async def session_getter(self):
        async with self.sessions() as session:
            yield session
    

db_helper = DatabaseHelper(
    url = str(settings.db.get_url()),
    echo = settings.db.echo, 
    echo_pool = settings.db.echo_pool,
    pool_size = settings.db.pool_size,
    max_overflow = settings.db.max_overflow,
)
print(settings.db.echo)
mock_db_helper = DatabaseHelper(
    url = "sqlite+aiosqlite:///database_test.db",
    echo = settings.db.echo, 
    echo_pool = settings.db.echo_pool,
    pool_size = settings.db.pool_size,
    max_overflow = settings.db.max_overflow,
)