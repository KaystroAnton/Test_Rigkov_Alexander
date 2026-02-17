from email.policy import default
from typing import Optional

from sqlalchemy import select

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from pydantic_async_validation import async_field_validator, AsyncValidationModelMixin
from enum import Enum

from database import new_session, UserTable, ProductTable


# User models
#from typing import Literal

class SUserAdd(BaseModel):
    username: str
    email: Optional[EmailStr | None] = Field(default = None,pattern=r".+@example\.com$")
    balance: Optional[int] = Field(default =0)
    created_at: Optional[datetime] = Field(default = datetime.now())

class SUser(SUserAdd):
    id: int

    model_config = ConfigDict(from_attributes=True) # Добавлен лоя корректной конвертации model_validate


#Product models
class Type(str,Enum):
    consumable= "consumable"
    permanent= "permanent"

class SProductAdd(BaseModel):
    name: str
    description: str = "Описание отсутствует"
    price: int = 5
    type: Type = Field(default = Type.consumable)
    #type: #Literal["consumable","permanent"] # Либо с помощью Enum либо с помощью Literal
    is_active:bool = False

class SProduct(SProductAdd):
    id: int

    model_config = ConfigDict(from_attributes = True)


# Inventory models
class SInventoryAdd(AsyncValidationModelMixin,BaseModel):
    user_id: int
    product_id: int
    quantity: int | None = Field(default = None, description = "None for permanent product, int for consumable")
    purchase_at: datetime = datetime.now()

    @async_field_validator('user_id','product_id', mode = "after")
    async def foreign_key_validator(self) -> list[int]:
        if not await get_user_by_id(self.user_id):
            raise ValueError(f"User id {self.user_id} is not exists")
        if not await get_product_by_id(self.product_id):
            raise ValueError(f"Product id {self.product_id} is not exists")
        return [self.user_id, self.product_id]

    @async_field_validator('quantity',mode= "after")
    async  def quantity_validator(self):
        product = await get_product_by_id(product_id=self.product_id)
        if product.type == "consumable":
            print("consumable")
            if self.quantity is None:
                raise TypeError(f"For consumable products quantity must be a Integer not {type(self.quantity)}")
            if self.quantity < 0:
                raise ValueError(f"For consumable products quantity must be not negative, you entered {self.quantity}")
        elif product.type == "permanent":
            print("permanent")
            if self.quantity is not None:
                raise TypeError("For permanent products quantity must be only None")

class SInventory(SInventoryAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Transaction model
class Status(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class STransactionAdd(AsyncValidationModelMixin,BaseModel):
    user_id: int
    product_id: int
    amount: float = Field(default = 0.00)
    status: Status = Field(default = Status.pending)


    @async_field_validator('user_id', 'product_id', mode="after")
    async def foreign_key_validator(self) -> list[int]:
        if not await get_user_by_id(self.user_id):
            raise ValueError(f"User id {self.user_id} is not exists")
        if not await get_product_by_id(self.product_id):
            raise ValueError(f"Product id {self.product_id} is not exists")
        return [self.user_id, self.product_id]

    @field_validator('amount', mode = 'before')
    @classmethod
    def money_digits_validation(cls,value,digits_after_point: int = 2, max_value_of_transaction: float = 100000) -> float:
        if value* pow(10,digits_after_point)%1 > 0: # Вычисляет остаток числа после digits_after_point знаков
            raise ValueError(f"amount must be only {digits_after_point} digits after point")
        if value >= max_value_of_transaction:
            raise ValueError(f"amount must be lesser then {max_value_of_transaction}")
        return value


class STransaction(STransactionAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Классы для вывода
class SUserId(BaseModel):
    ok: bool = True
    user_id: int

class SInventoryId(BaseModel):
    ok:bool = True
    inventory_id: int
    user_id: int

class SProductId(BaseModel):
    ok: bool = True
    product_id: int

class STransactionId(BaseModel):
    ok: bool = True
    transaction_id: int


#help functions
async  def get_user_by_id(user_id) -> SUser | None:
    async  with new_session() as session:
        query = select(UserTable).where(UserTable.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()
        if not user:
            return user
        return SUser.model_validate(user)

async def get_product_by_id(product_id) -> SProduct | None:
    async  with new_session() as session:
        query = select(ProductTable).where(ProductTable.id == product_id)
        result = await session.execute(query)
        product = result.scalars().first()
        if not product:
            return product
        return SProduct.model_validate(product)