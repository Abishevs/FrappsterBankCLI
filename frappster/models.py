from typing import List
from typing import Optional
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from frappster.types import AccessRole, AccountType

class BaseModel(DeclarativeBase):
    pass

class User(BaseModel):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True) # used as Internal ID
    login_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(30))
    middle_name: Mapped[Optional[str]] = mapped_column(String(30),
                                                       nullable=True)
    last_name: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(100))
    access_role: Mapped[AccessRole] = mapped_column(SQLEnum(AccessRole))
    login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    login_timeout: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # The cool stuff
    accounts: Mapped[List["Account"]] = relationship("Account", 
                                                     order_by="Account.id",
                                                     back_populates="user")
    def to_dict(self):
        data = {
            'id': self.id,
            'login_id': self.login_id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'address': self.address,
            'email': self.email,
            'phone_number': self.phone_number,
            'access_role': self.access_role
        }
        return data

class UserData:
    def __init__(self, 
                 id,
                 login_id,
                 first_name,
                 middle_name,
                 last_name,
                 address,
                 email,
                 phone_number,
                 access_role
                 ) -> None:

        self.id = id
        self.login_id = login_id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.phone_number = phone_number
        self.access_role = access_role

class Account(BaseModel):
    __tablename__ = 'accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    clearings_number: Mapped[int] = mapped_column(Integer, nullable=False)
    account_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0.0)
    user_id: Mapped[int] = mapped_column(Integer, 
                                        ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # The cool stuff
    user: Mapped["User"] = relationship("User",
                                        back_populates="accounts")

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'clearings_number': self.clearings_number,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'balance': self.balance,
        }
        return data

class AccountData:
    def __init__(self,
                 id: int,
                 user_id: int,
                 clearings_number: int,
                 account_number: int,
                 account_type: AccountType,
                 balance: int,
                 ) -> None:
        self.id = id
        self.user_id = user_id
        self.clearings_number = clearings_number
        self.account_number = account_number
        self.account_type = account_type
        self.balance = balance


class Transaction(BaseModel):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    senders_account_id: Mapped["Account"] = mapped_column(Integer,
                                                  ForeignKey('accounts.id'))
    recipients_account_id: Mapped["Account"] = mapped_column(Integer,
                                                    ForeignKey('accounts.id'))
    type: Mapped[str] = mapped_column(String(30))
    amount: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # The cool stuff
    account: Mapped["Account"] = relationship("Account",
                                              foreign_keys=[senders_account_id])
    recipient: Mapped["Account"] = relationship("Account", 
                                                foreign_keys=[recipients_account_id])
