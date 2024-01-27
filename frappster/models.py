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
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    middle_name: Mapped[Optional[str]] = mapped_column(String(30),
                                                       nullable=True)
    last_name: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(100))
    access_role: Mapped[AccessRole] = mapped_column(SQLEnum(AccessRole))
    login_attempts: Mapped[int] = mapped_column(Integer)
    last_login: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # The cool stuff
    accounts: Mapped[List["Account"]] = relationship("Account", 
                                                     order_by="Account.id",
                                                     back_populates="user")

class Account(BaseModel):
    __tablename__ = 'accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType))
    balance: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, 
                                        ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # The cool stuff
    user: Mapped["User"] = relationship("User",
                                        back_populates="accounts")
class Transaction(BaseModel):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped["Account"] = mapped_column(Integer,
                                                  ForeignKey('accounts.id'))
    recipient_id: Mapped["Account"] = mapped_column(Integer,
                                                    ForeignKey('accounts.id'))
    type: Mapped[str] = mapped_column(String(30))
    amount: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # The cool stuff
    account: Mapped["Account"] = relationship("Account",
                                              foreign_keys=[account_id])
    recipient: Mapped["Account"] = relationship("Account", 
                                                foreign_keys=[recipient_id])
