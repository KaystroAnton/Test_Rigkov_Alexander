from database import  Model

from datetime import datetime
from sqlalchemy.orm import (Mapped, 
                            mapped_column, 
                            relationship)

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