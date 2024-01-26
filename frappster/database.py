from typing import Type, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frappster.models import Account, Base, Transaction, User

class DatabaseManager:
    def __init__(self, db_url="sqlite:///test.db"):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine) 
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
        """Takes instance of an model & creates new record"""
        self.session.add(record)

    def delete(self, record):
        self.session.delete(record)

    def get_one(self,
                model: Type[User] 
                | Type[Account] 
                | Type[Transaction],
                record_id: int
                ) -> Union[User, Account, Transaction, None]:
        """Reads db table given model & primary key"""
        return self.session.query(model).get(record_id)

    def get_all(self,
                model: Type[User] 
                | Type[Account] 
                | Type[Transaction],
                ):
        """Reads db table and gets all records"""
        return self.session.query(model).all()
