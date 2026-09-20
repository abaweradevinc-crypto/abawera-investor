# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///abawera.db', echo=False)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    name = Column(String)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True)
    name = Column(String)
    price = Column(Float)

class Holding(Base):
    __tablename__ = 'holdings'
    id = Column(Integer, primary_key=True)
    user_phone = Column(String)
    symbol = Column(String)
    shares = Column(Float)
    buy_price = Column(Float)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_phone = Column(String)
    type = Column(String)  # deposit, withdraw, buy, sell
    amount = Column(Float)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    s = Session()
    if s.query(Stock).count() == 0:
        stocks = [
            Stock(symbol="SCOM", name="Safaricom PLC", price=18.50),
            Stock(symbol="EQTY", name="Equity Group", price=42.75),
            Stock(symbol="KCB",  name="KCB Group", price=38.20),
            Stock(symbol="EABL", name="East African Breweries", price=145.00),
            Stock(symbol="COOP", name="Co-operative Bank", price=13.80),
            Stock(symbol="ABSA", name="Absa Bank Kenya", price=15.45),
        ]
        s.add_all(stocks)
        s.commit()
    s.close()

