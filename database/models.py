from typing import List

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import ForeignKey, String, UniqueConstraint, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .service import Model


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128))
    name: Mapped[str | None] = mapped_column(String(30))

    __table_args__ = (
        UniqueConstraint("username", name="unique_username"),
    )

    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="author",
        cascade="all"
    )

    likes: Mapped[List["Like"]] = relationship(
        "Like",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    following: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )

    followers: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )

    @classmethod
    def hash_username(cls, username: str) -> str:
        salt = gensalt()
        return hashpw(username.encode('utf-8'), salt).decode('utf-8')

    @classmethod
    def compare_username(cls, username: str, hashed_username: str) -> bool:
        return checkpw(username.encode('utf-8'), hashed_username.encode('utf-8'))

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username={self.username}, "
            f"name={self.name})>"
        )


class Tweet(Model):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(280))
    media_ids: Mapped[List[int] | None] = mapped_column(ARRAY(Integer))

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="joined")

    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Tweet(id={self.id}, author_id={self.author_id}, content={self.content[:30]}...)>"


class Media(Model):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"<Media(id={self.id}, link={self.link})>"


class Like(Model):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    author: Mapped["User"] = relationship(back_populates="likes", lazy="joined")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")

    def __repr__(self) -> str:
        return (
            f"<Like(id={self.id}, author_id={self.author_id}, tweet_id={self.tweet_id})>"
        )


class Follow(Model):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        "User", foreign_keys=[followed_id], back_populates="followers"
    )

    def __repr__(self) -> str:
        return (
            f"<Follow(id={self.id}, follower_id={self.follower_id}, "
            f"followed_id={self.followed_id})>"
        )
