from sqlalchemy import Column, Integer, String, Float, DateTime
from ARertesito.db.database import Base
from datetime import datetime,UTC

class WatchedProduct(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    name = Column(String, nullable=True)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float)
    last_checked = Column(DateTime, default=datetime.now(UTC))
    notify_interval_minutes = Column(Integer, default=1440)  
    last_notified = Column(DateTime, nullable=True)
    useremail = Column(String, nullable=True)