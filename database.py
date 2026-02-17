import os
from dotenv import load_dotenv
from datetime import datetime
from email.policy import default
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey,Float

# Создание engine и session_maker
def create_path():
    load_dotenv()
    database, user,password, name ,db_domen_name,db_port = (
    os.getenv("DATABASE"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD"),
    os.getenv("DB_NAME"),os.getenv("DB_DOMEN_NAME"),os.getenv("DB_PORT"))
    server_ip = f"{db_domen_name}:{db_port}"
    return f"{database}://{user}:{password}@{server_ip}/{name}"

DATABASE_URL = create_path()

engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(bind = engine, expire_on_commit=False)

# Таблицы в базе данных

class Base:
    __tablename__ = "model"

    repr_cols_num = 4
    repr_cols = tuple()

    def __repr__(self): # Вывод на печать модель
        """ Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам """
        cols = []
        for idx,col in enumerate(self.__table__.columns.keys()): # Вывод первых  {repr_cols_num} полей,
                                                                 # либо тех что содержаться в repr_cols
                                                                 #repr_cols_num, repr_cols = tuple() можно задавать в наследуемых моделях
            if cols in self.repr_cols or idx<self.repr_cols_num:
                cols.append(f"{col}={getattr(self,col)}")

        return f"<{self.__class__.__tablename__} {','.join(cols)}>"

Model = declarative_base(cls = Base)


class UserTable(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True)
    username:  Mapped[str]
    email: Mapped[str | None]
    balance: Mapped[int]
    created_at: Mapped[datetime]

    # relationships
    inventories: Mapped[list["InventoryTable"]] = relationship(back_populates ="user")
    transactions: Mapped[list["TransactionTable"]] = relationship(back_populates = "user")

class ProductTable(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key = True)
    name:  Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    type: Mapped[str]
    is_active: Mapped[bool]

    #relationships
    inventories: Mapped[list["InventoryTable"]] = relationship(back_populates = "product")
    transactions: Mapped[list["TransactionTable"]] = relationship(back_populates="product")

class InventoryTable(Model):
    __tablename__= "inventory"
    id: Mapped[int] = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int| None]
    purchase_at: Mapped[datetime]

    # relationships
    user: Mapped["UserTable"] = relationship(back_populates ="inventories")
    product: Mapped["ProductTable"] = relationship(back_populates ="inventories")

class TransactionTable(Model):
    __tablename__= "transaction"
    id: Mapped[int] = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    amount: Mapped[float] # Как я понял это деньги, которые проходят в транзакции
    status: Mapped[str]

    #relationships
    user: Mapped["UserTable"] = relationship(back_populates ="transactions")
    product: Mapped["ProductTable"] = relationship(back_populates ="transactions")


# Создание и удаление таблиц

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)