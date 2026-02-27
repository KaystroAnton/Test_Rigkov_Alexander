from sqlalchemy.orm import declarative_base, Mapped,DeclarativeBase,mapped_column, declared_attr
from utils import camel_case_to_snake_case
class Base(DeclarativeBase):
    __abstract__ = True
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "f{camel_case_to_snake_case(cls.__name__)}+s"


    id: Mapped[int] = mapped_column(primary_key=True)


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
    
