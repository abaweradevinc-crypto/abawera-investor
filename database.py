# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
import os as _os

def _find_writable_dir():
    candidates = []
    # 1. Android's app private dir (set by p4a at runtime)
    env = _os.environ.get("ANDROID_PRIVATE")
    if env:
        candidates.append(env)
    # 2. Kivy's app user_data_dir (available after app starts)
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and app.user_data_dir:
            candidates.append(app.user_data_dir)
    except Exception:
        pass
    # 3. HOME env var
    home = _os.environ.get("HOME")
    if home:
        candidates.append(home)
    # 4. Standard Android app files dir for our package
    candidates.append("/data/data/org.abaweradevsinc.abawerainvestor/files")
    candidates.append("/data/data/com.abaweradevsinc.abawerainvestor/files")
    # 5. Shared storage (may fail without permissions)
    candidates.append("/sdcard/AbaweraInvestor")
    # 6. Home expansion and /tmp as final fallbacks
    candidates.append(_os.path.expanduser("~"))
    candidates.append("/tmp")

    for path in candidates:
        if not path:
            continue
        try:
            _os.makedirs(path, exist_ok=True)
            testfile = _os.path.join(path, ".write_test_tmp")
            with open(testfile, "w") as f:
                f.write("ok")
            _os.remove(testfile)
            return path
        except Exception:
            continue
    return "/tmp"

DB_DIR = _find_writable_dir()
DB_PATH = _os.path.join(DB_DIR, "abawera.db")
engine = create_engine("sqlite:///" + DB_PATH, echo=False)
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

