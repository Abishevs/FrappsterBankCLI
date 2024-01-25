from typing import List
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    middle_name: Mapped[Optional[str]] = mapped_column(String(30),
                                                       nullable=True)
    last_name: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(100))
    access_role: Mapped[int] = mapped_column(String(30))
    
    # The cool stuff
    accounts: Mapped[List["Account"]] = relationship("Account", 
                                                     order_by="Account.id",
                                                     back_populates="user")

class Account(Base):
    __tablename__ = 'accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_type: Mapped[str] = mapped_column(String(30))
    balance: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, 
                                        ForeignKey('users.id'))
    # The cool stuff
    user: Mapped["User"] = relationship("User",
                                        back_populates="accounts")
class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped["Account"] = mapped_column(Integer,
                                                  ForeignKey('accounts.id'))
    recipient_id: Mapped["Account"] = mapped_column(Integer,
                                                    ForeignKey('accounts.id'))
    type: Mapped[str] = mapped_column(String(30))
    amount: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)

    # The cool stuff
    account: Mapped["Account"] = relationship("Account",
                                              foreign_keys=[account_id])
    recipient: Mapped["Account"] = relationship("Account", 
                                                foreign_keys=[recipient_id])
