from typing import Annotated
from fastapi import Depends, APIRouter


from repository import UserRepository, ProductRepository, InventoryRepository, TransactionRepository
from schemas import (SUserAdd, SUser, SUserId,
                     SProductAdd, SProduct, SProductId,
                     SInventoryAdd, SInventory, SInventoryId,
                     STransactionAdd, STransaction,  STransactionId)

routers = []

router = APIRouter(tags = ["Старт"])
routers.append(router)

user_router = APIRouter(
    prefix = "/1",
    tags = ["Работа с пользователями"] # для красивого вывода в swagger
)
routers.append(user_router)

product_router = APIRouter(
    prefix = "/products",
    tags = ["Работа с продуктами"]
)
routers.append(product_router)

inventory_router = APIRouter(
    prefix = "/inventory",
    tags = ["Работа с Инвентарём"]
)
routers.append(inventory_router)

transaction_router = APIRouter(
    prefix = "/transactions",
    tags = ["Работа с Транзакциями"]
)
routers.append(transaction_router)


# Перед деплоем удалить Annotated
"""
@router.get("/", status_code = 200)
def get_start() -> dict:
    return {"Initial": "Project is created"}
"""

# User
@user_router.post("/user", status_code = 200)
async def add_user(
    user: Annotated[SUserAdd, Depends()], #Annotated добавлено только для красивого вывода
) -> SUserId:
    user_id =await UserRepository.add_one(user)
    return {"ok": True, "user_id": user_id}

@user_router.get("/users", status_code = 200)
async def get_users() -> list[SUser]:
    users =await UserRepository.find_all()
    return users

@user_router.get("/user_inventories", status_code = 200)
async def get_user_inventories(user_id: int) -> list[SInventory]:
    inventories = await UserRepository.find_all_user_inventories(user_id)
    return inventories

@user_router.get("/user_transactions", status_code = 200)
async  def get_user_transactions(user_id: int) -> list[STransaction]:
    transactions = await UserRepository.find_all_user_transactions(user_id)
    return transactions


#Product
@product_router.post("/product", status_code = 200)
async def add_product(
        product: Annotated[SProductAdd, Depends(SProductAdd)],
) -> SProductId:
    product_id = await ProductRepository.add_one(product)
    return {"ok": True, "product_id": product_id}

@product_router.get("/", status_code = 200)
async  def find_products() -> list[SProduct]:
    products = await ProductRepository.find_all()
    return  products

@product_router.post("/{product_id}/purchase", status_code = 200)
async  def purchase_product(product_id: int) -> SProduct:
    product = await ProductRepository.purchase_product(product_id)
    return product



#Inventory
@inventory_router.post("/add_inventory", status_code =200)
async def add_inventory(inventory: Annotated[SInventoryAdd,Depends(SInventoryAdd)])\
        -> SInventoryId:
    inventory_id = await InventoryRepository.add_one(inventory)
    return SInventoryId(inventory_id = inventory_id, user_id =inventory.user_id)

@inventory_router.get("/find_inventories", status_code = 200)
async def find_inventories() -> list[SInventory]:
    inventories = await InventoryRepository.find_all()
    return inventories

#Transactions
@transaction_router.post("/add_transaction", status_code = 200)
async def add_transaction(transaction: Annotated[STransactionAdd, Depends()]) -> STransactionId:
    transaction_id = await TransactionRepository.add_one(transaction)
    return {"ok": True, "transaction_id": transaction_id}

@transaction_router.get("/get_all_transactions", status_code = 200)
async def get_all_transactions() -> list[STransaction]:
    transactions = await TransactionRepository.get_all()
    return transactions