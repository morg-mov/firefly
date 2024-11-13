from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy import BigInteger, String, DateTime, Text   , ForeignKey

Base = declarative_base()
class Submission(Base):
    __tablename__ = "Submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    svr_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    upvotes: Mapped[list] = relationship("Upvote", back_populates='submission')

    def __repr__(self):
        return f"Submission(id={self.id!r}, svr_id={self.svr_id!r}, user_id={self.user_id!r}, name={self.svr_name!r}, img_url={self.img_url!r})"


class Upvote(Base):
    __tablename__ = "Upvotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    svr_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_id: Mapped[str] = mapped_column(String(36), ForeignKey('Submissions.id'))
    submission = relationship('Submission', back_populates='upvotes')

    def __repr__(self):
        return f"Upvote(id={self.id!r}, user_id={self.user_id!r}, sub_id={self.sub_id})"