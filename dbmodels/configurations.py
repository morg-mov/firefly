from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import Integer, BigInteger, String, DateTime, Text, LargeBinary

Base = declarative_base()

class IconContestConfig(Base):
    __tablename__ = "iconcontest"

    