from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.orm.session import Session

from frappster.models import Account, BaseModel, Transaction, User
from frappster.types import AccessRole
from frappster.utils import hash_password

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
    def __init__(self, db_url="sqlite:///test.db", echo=False):
        self.engine = create_engine(db_url, echo=echo)
        BaseModel.metadata.create_all(self.engine) 
        self.Session = sessionmaker(bind=self.engine)

    def create_super_admin(self):
        self.open_session()
        admin_count = self.session.query(User).filter_by(access_role=AccessRole.ADMIN).count()

        if admin_count == 0:
            super_admin = User(
                login_id=42069,  
                first_name="Anorak",
                last_name="Watts",
                email="superadmin@cli-banksystem.se",
                phone_number="4324134232",
                address="FERTISILE 32 st",
                password=hash_password("secure"),
                access_role=AccessRole.ADMIN
            )
            self.session.add(super_admin)
            try:
                self.commit()
                print("Super admin account created.")
            except Exception as e:
                print(f"Error creating super admin: {e}")
                self.rollback()
            finally:
                self.close_session()
        else:
            print("Super admin account already exists.")

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
        return self.session.query(model).options(joinedload('*')).filter_by(login_id=record_id).first()

    def get_all(self, model):
        return self.session.query(model).all()
