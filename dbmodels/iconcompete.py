from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import Integer, BigInteger, String, DateTime, Text, LargeBinary

Base = declarative_base()

class Submission(Base):
    __tablename__ = "submissions"

    sub_id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    svr_name: Mapped[str] = mapped_column(Text, nullable=False)
    svr_img: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    def __repr__(self):
        return f"Submission(id={self.sub_id!r}, user_id={self.user_id!r}, timestamp={self.timestamp.isoformat()!r}, svr_name={self.svr_name!r})"


class Upvote(Base):
    __tablename__ = "upvotes"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    sub_id: Mapped[str] = mapped_column(String(36), nullable=False)

    def __repr__(self):
        return f"Upvote(user_id={self.user_id!r}, sub_id={self.sub_id!r})"