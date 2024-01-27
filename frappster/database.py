from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from frappster.models import Account, BaseModel, Transaction, User

class AbstractDatabaseManager(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def open_session(self) -> Session:
        pass

    @abstractmethod
    def close_session(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def create(self,
               record: Union[User,
                                  Account,
                                  Transaction
                                  ]
               ):
        """Takes instance of an model & creates new record"""
        pass

    @abstractmethod
    def delete(self, 
               record: Union[User,
                                    Account,
                                    Transaction
                                    ]
               ):
        pass

    @abstractmethod
    def get_one(self,
                model: Type[Union[User,
                                  Account,
                                  Transaction
                                  ]],
                record_id: int
                ) -> Optional[Union[User, Account, Transaction]]:
        """Reads db table given model & primary key"""
        pass
    
    @abstractmethod
    def get_all(self,
                model: Type[Union[User,
                                  Account,
                                  Transaction
                                  ]],
                ) -> List[Union[User, Account, Transaction]]:
        """Reads db table and gets all records"""
        pass

class DatabaseManager(AbstractDatabaseManager):
    def __init__(self, db_url="sqlite:///test.db"):
        self.engine = create_engine(db_url, echo=True)
        BaseModel.metadata.create_all(self.engine) 
        self.Session = sessionmaker(bind=self.engine)

    def open_session(self):
        self.session = self.Session()
        return self.session

    def close_session(self):
        if self.session is not None:
            self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def create(self, record):
        self.session.add(record)

    def delete(self, record):
        self.session.delete(record)

    def get_one(self, model, record_id):
        return self.session.query(model).get(record_id)

    def get_all(self, model):
        return self.session.query(model).all()
