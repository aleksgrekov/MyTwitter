from typing import List, Optional, Dict, Any

from sqlalchemy import (
    ForeignKey, String, ARRAY, Integer, select, delete, exists
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from logger.logger_setup import get_logger
from scr.functions import exception_handler

from .service import Model
from .schemas import NewTweet, UserSchema

models_logger = get_logger(__name__)


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(30))

    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet", back_populates="author", cascade="all"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", back_populates="author", cascade="all, delete-orphan"
    )
    followings: Mapped[List["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan"
    )
    followers: Mapped[List["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, name={self.name})>"

    @classmethod
    async def get_user_id_by_username(cls, username: str, session: AsyncSession) -> Optional[int]:
        query = select(cls.id).where(cls.username == username)
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def get_user_with_followers_and_following(
            cls, session: AsyncSession, username: Optional[str] = None, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        if username is None and user_id is None:
            return exception_handler(models_logger, "ValueError", "Missing one of argument (username or user_id)")

        query = select(cls).options(selectinload(cls.followers), selectinload(cls.followings))
        if username:
            query = query.where(cls.username == username)
        if user_id:
            query = query.where(cls.id == user_id)

        result = await session.execute(query)
        user = result.scalars().one_or_none()

        if not user:
            return exception_handler(models_logger, "ValueError", "User not found")

        followers_ids = [follow.follower_id for follow in user.followers]
        followers_query = select(cls).where(cls.id.in_(followers_ids))
        followers_request = await session.execute(followers_query)
        followers = followers_request.scalars().all()

        following_ids = [follow.following_id for follow in user.followings]
        following_query = select(cls).where(cls.id.in_(following_ids))
        following_request = await session.execute(following_query)
        followings = following_request.scalars().all()

        return {
            "result": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [UserSchema.model_validate(follower) for follower in followers],
                "following": [UserSchema.model_validate(follow) for follow in followings],
            },
        }


class Tweet(Model):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_data: Mapped[str] = mapped_column(String(280))
    tweet_media_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer))

    author: Mapped["User"] = relationship("User", back_populates="tweets", lazy="joined")
    likes: Mapped[List["Like"]] = relationship("Like", back_populates="tweet", cascade="all, delete-orphan",
                                               lazy="joined")

    def __repr__(self) -> str:
        return f"<Tweet(id={self.id}, author_id={self.author_id}, content={self.tweet_data[:30]}...)>"

    @classmethod
    async def is_tweet_exist(cls, tweet_id: int, session: AsyncSession) -> bool:
        query = select(exists().where(cls.id == tweet_id))
        request = await session.execute(query)
        return request.scalar()

    @classmethod
    async def add_tweet(cls, username: str, tweet: NewTweet, session: AsyncSession) -> Dict[str, Any]:
        try:
            user_id = await User.get_user_id_by_username(username=username, session=session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            tweet_dict = tweet.model_dump()
            tweet_dict["author_id"] = user_id
            new_tweet = cls(**tweet_dict)

            session.add(new_tweet)
            await session.flush()
            await session.commit()

            return {"result": True, "tweet_id": new_tweet.id}
        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def delete_tweet(cls, username: str, tweet_id: int, session: AsyncSession) -> Dict[str, Any]:
        try:
            user_id = await User.get_user_id_by_username(username=username, session=session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            query = delete(cls).returning(cls.id).where(cls.id == tweet_id, cls.author_id == user_id)
            request = await session.execute(query)

            if not request.fetchone():
                return exception_handler(models_logger, "ValueError", "Tweet with this ID does not exist")

            await session.commit()
            return {"result": True}

        except SQLAlchemyError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Media(Model):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"<Media(id={self.id}, link={self.link})>"

    @classmethod
    async def add_media(cls, link: str, session: AsyncSession) -> Dict[str, Any]:
        try:
            new_media = cls(link=link)
            session.add(new_media)
            await session.flush()
            await session.commit()
            return {"result": True, "media_id": new_media.id}
        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Like(Model):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    author: Mapped["User"] = relationship("User", back_populates="likes", lazy="joined")
    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")

    def __repr__(self) -> str:
        return (
            f"<Like(id={self.id}, author_id={self.author_id}, tweet_id={self.tweet_id})>"
        )

    @classmethod
    async def like(cls, username: str, tweet_id: int, session: AsyncSession) -> Dict[str, Any]:
        try:
            user_id = await User.get_user_id_by_username(username=username, session=session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            if not await Tweet.is_tweet_exist(tweet_id, session):
                return exception_handler(models_logger, "ValueError", "Tweet with this tweet_id does not exist")
            like = cls(author_id=user_id, tweet_id=tweet_id)
            session.add(like)
            await session.commit()

            return {"result": True}

        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def delete_like(cls, username: str, tweet_id: int, session: AsyncSession) -> Dict[str, Any]:
        try:
            user_id = await User.get_user_id_by_username(username=username, session=session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            tweet_exists = await Tweet.is_tweet_exist(tweet_id, session)
            if not tweet_exists:
                return exception_handler(models_logger, "ValueError", "Tweet with this ID does not exist")

            query = delete(cls).returning(cls.id).where(cls.tweet_id == tweet_id, cls.author_id == user_id)
            result = await session.execute(query)

            if not result.fetchone():
                return exception_handler(models_logger, "ValueError", "No like entry found for this user and tweet")

            await session.commit()
            return {"result": True}

        except SQLAlchemyError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Follow(Model):
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="followings"
    )
    following: Mapped["User"] = relationship(
        "User", foreign_keys=[following_id], back_populates="followers"
    )

    def __repr__(self) -> str:
        return (
            f"<Follow(follower_id={self.follower_id}, "
            f"followed_id={self.following_id})>"
        )
