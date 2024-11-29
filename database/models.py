from typing import List, Optional, Dict, Any

from sqlalchemy import ForeignKey, String, UniqueConstraint, ARRAY, Integer, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from scr.functions import exception_handler

from .service import Model
from .schemas import NewTweet, UserSchema


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128), index=True)
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

    followings: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )

    followers: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan"
    )

    @classmethod
    async def get_user_id_by_username(cls, username: str, session: AsyncSession) -> Optional["User"]:
        query = select(cls.id).where(cls.username == username)
        request = await session.execute(query)
        user_id = request.scalars().one_or_none()

        return user_id if user_id else None

    @classmethod
    async def get_user_with_followers_and_following(cls, session: AsyncSession, username: str = None,
                                                    user_id: int = None) -> Dict[str, Any]:
        if not (username or user_id):
            return exception_handler("ValueError", "Missing one of argument (username or user_id)")

        query = (
            select(cls)
            .options(selectinload(cls.followers), selectinload(cls.followings))
        )
        if username:
            query = query.where(cls.username == username)
        elif user_id:
            query = query.where(cls.id == user_id)
        result = await session.execute(query)

        user = result.scalars().one_or_none()
        if not user:
            return exception_handler("ValueError", "User not found")

        followers_ids = [follow.follower_id for follow in user.followers]
        followers_query = select(cls).where(cls.id.in_(followers_ids))
        followers_request = await session.execute(followers_query)
        followers = followers_request.scalars().all()

        following_ids = [follow.following_id for follow in user.followings]
        following_query = select(cls).where(cls.id.in_(following_ids))
        following_request = await session.execute(following_query)
        followings = following_request.scalars().all()

        return {
            "result": "true",
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [UserSchema.model_validate(follower) for follower in followers],
                "following": [UserSchema.model_validate(follow) for follow in followings],
            },
        }

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username={self.username}, "
            f"name={self.name})>"
        )


class Tweet(Model):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_data: Mapped[str] = mapped_column(String(280))
    tweet_media_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer))

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="joined")

    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    @classmethod
    async def add_tweet(cls, username: str, tweet: NewTweet, session: AsyncSession) -> Dict[str, Any]:
        try:
            user_id = await User.get_user_id_by_username(username=username, session=session)
            if not user_id:
                return exception_handler(
                    error_type="ValueError",
                    error_message="There are no users with this ID"
                )

            tweet_dict = tweet.model_dump()
            tweet_dict["author_id"] = user_id
            new_tweet = cls(**tweet_dict)
            session.add(new_tweet)

            await session.flush()
            await session.commit()
            return {"result": True, "tweet_id": new_tweet.id}

        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(
                error_type=exc.__class__.__name__,
                error_message=str(exc)
            )

    def __repr__(self) -> str:
        return f"<Tweet(id={self.id}, author_id={self.author_id}, content={self.tweet_data[:30]}...)>"


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
            return exception_handler(
                error_type=exc.__class__.__name__,
                error_message=str(exc)
            )


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
