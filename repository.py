from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import (new_session,
                      UserTable,
                      ProductTable,
                      InventoryTable,
                      TransactionTable)
from schemas import (SUserAdd, SUser,
                     SProductAdd, SProduct,
                     SInventoryAdd, SInventory,
                     Type,
                     STransactionAdd, STransaction)



async def create_test_dataset():
    await UserRepository.add_one(SUserAdd(username="1"))
    await UserRepository.add_one(SUserAdd(username="2"))
    await UserRepository.add_one(SUserAdd(username="3"))
    await UserRepository.add_one(SUserAdd(username="4"))
    await ProductRepository.add_one(SProductAdd(name="1", type = Type.permanent))
    await ProductRepository.add_one(SProductAdd(name="2", type = Type.consumable))
    await ProductRepository.add_one(SProductAdd(name="3", type = Type.consumable))
    await ProductRepository.add_one(SProductAdd(name="4", type = Type.permanent))
    await InventoryRepository.add_one(SInventoryAdd(user_id=1, product_id=1,))
    await InventoryRepository.add_one(SInventoryAdd(user_id=1, product_id=2, quantity=3))
    await InventoryRepository.add_one(SInventoryAdd(user_id=1, product_id=3, quantity=3))
    await InventoryRepository.add_one(SInventoryAdd(user_id=2, product_id=2, quantity=3))
    await InventoryRepository.add_one(SInventoryAdd(user_id=3, product_id=4,))
    await InventoryRepository.add_one(SInventoryAdd(user_id=4, product_id=1,))




class UserRepository:
    @classmethod
    async def add_one(cls, data: SUserAdd) -> int :
        async with new_session() as session:
            user_dict = data.model_dump() # Приводим к типу словаря
            user = UserTable(**user_dict)
            session.add(user)
            await session.flush() # Добавляет поле id к user, от БД
            await session.commit() # Закрывает сессию
            await session.refresh(user)
            return user.id

    @classmethod
    async def find_all(cls) -> list[SUser]:
        async with new_session() as session:
            query = select(UserTable)
            result = await session.execute(query)
            user_tables = result.scalars().all()
            user_schemas = [SUser.model_validate(user) for user in user_tables]
            return user_schemas

    @classmethod
    async def find_all_user_inventories(cls, user_id) -> list[SInventory]:
        async with new_session() as session:
            await create_test_dataset()
            query = select(UserTable).where(UserTable.id == user_id
                                            ).options(selectinload(UserTable.inventories))
            result = await session.execute(query)
            user_tables = result.scalars().all()
            inventory_schemas = []
            for user in user_tables:
                for inventory in user.inventories:
                    inventory_schemas.append(SInventory.model_validate(inventory))
            return inventory_schemas

    @classmethod
    async def find_all_user_transactions(cls, user_id ) -> list[STransaction]:
        await create_test_dataset()
        async with new_session() as session:
            query = select(UserTable).where(UserTable.id == user_id
                                                   ).options(selectinload(UserTable.transactions))
            result = await session.execute(query)
            user_tables = result.scalars().all()
            transaction_schemas = []
            for user in user_tables:
                for transaction in user.transactions:
                    transaction_schemas.append(STransaction.model_validate(transaction))
            return transaction_schemas


class ProductRepository:

    @classmethod
    async  def add_one(cls, data: SProductAdd) -> int:
        async  with new_session() as session:
            product_dict = data.model_dump()
            product = ProductTable(**product_dict)
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product.id

    @classmethod
    async  def find_all(cls) -> list[SProduct]:
        async with new_session() as session:
            query = select(ProductTable)
            result = await session.execute(query)
            product_tables = result.scalars().all()
            product_schemas = [SProduct.model_validate(product) for product in product_tables]
            return  product_schemas

    @classmethod
    async  def find_one_by_id(cls, product_id:int) -> SProduct:
        async with new_session() as session:
            query = select(ProductTable).where(ProductTable.id == product_id)
            result = await session.execute(query)
            product_tables = result.scalars().one()
            product_schemas = SProduct.model_validate(product_tables)
            return  product_schemas

    @classmethod
    async def purchase_product(cls, product_id:int) -> SProduct:
            product = await cls.find_one_by_id(product_id)
            return product



class InventoryRepository:

    @classmethod
    async  def add_one(cls, data: SInventoryAdd) -> int:
        async with new_session() as session:
            await data.foreign_key_validator()
            await  data.quantity_validator()
            inventory_dict = data.model_dump()
            inventory = InventoryTable(**inventory_dict)
            session.add(inventory)
            await session.commit()
            await session.refresh(inventory)
            return inventory.id

    @classmethod
    async def find_all(cls) -> list[SInventory]:
        async with new_session() as session:
            query = select(InventoryTable)
            result = await session.execute(query)
            inventory_tables = result.scalars().all()
            inventory_schemas = [SInventory.model_validate(inventory) for inventory in inventory_tables]
            return inventory_schemas


class TransactionRepository:

    @classmethod
    async def add_one(cls, data: STransactionAdd) -> int:
        await data.foreign_key_validator()
        async  with new_session() as session:
            transaction_dict = data.model_dump()
            transaction = TransactionTable(**transaction_dict)
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            return transaction.id

    @classmethod
    async  def get_all(cls) -> list[STransaction]:
        async  with new_session() as session:
            query = select(TransactionTable)
            result = await session.execute(query)
            transactions_tables = result.scalars().all()
            transactions_schemas = [STransaction.model_validate(transaction) for transaction in transactions_tables]
            return transactions_schemas



