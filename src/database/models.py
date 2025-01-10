from typing import List, Optional, Sequence, Union

from sqlalchemy import (
    ForeignKey, String, ARRAY, Integer, select, delete, exists
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.logger_setup import get_logger
from src.functions import exception_handler

from src.database.schemas import NewTweetDataSchema, UserSchema, NewTweetResponseSchema, UserWithFollowSchema, \
    UserResponseSchema, \
    NewMediaResponseSchema, TweetResponseSchema, TweetSchema, LikeSchema, SuccessSchema, ErrorResponseSchema

models_logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the user")
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, doc="Unique username")
    name: Mapped[str] = mapped_column(String(30), doc="Full name of user")

    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet", back_populates="author", cascade="all", doc="List of tweets authored by the user"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", back_populates="author", cascade="all, delete-orphan", doc="List of likes by the user"
    )
    followings: Mapped[List["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan",
        doc="List of followings (users this user follows)"
    )
    followers: Mapped[List["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan",
        doc="List of followers (users following this user)"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, name={self.name})>"

    @classmethod
    async def is_user_exist(cls, user_id: int, session: AsyncSession) -> bool:
        """Check if a user exists by their ID."""
        return await session.scalar(select(exists().where(cls.id == user_id)))

    @classmethod
    async def get_user_id_by(cls, username: str, session: AsyncSession) -> Optional[int]:
        """Get the user ID by their username."""
        return await session.scalar(select(cls.id).where(cls.username == username))

    @classmethod
    async def get_user_followers(cls, user_id: int, session: AsyncSession) -> Sequence["User"]:
        """Get the followers of a user."""
        query = select(cls).join(Follow, Follow.follower_id == cls.id).where(Follow.following_id == user_id)
        return (await session.scalars(query)).all()

    @classmethod
    async def get_user_following(cls, user_id: int, session: AsyncSession) -> Sequence["User"]:
        """Get the users a user is following."""
        query = select(cls).join(Follow, Follow.following_id == cls.id).where(Follow.follower_id == user_id)
        return (await session.scalars(query)).all()

    @classmethod
    async def get_user_with_followers_and_following(
            cls, session: AsyncSession, username: Optional[str] = None, user_id: Optional[int] = None
    ) -> Union[UserResponseSchema, ErrorResponseSchema]:
        """Get user with their followers and following list."""
        if not username and not user_id:
            return exception_handler(models_logger, "ValueError", "Missing one of argument (username or user_id)")

        query = select(cls)
        if username:
            query = query.where(cls.username == username)
        elif user_id:
            query = query.where(cls.id == user_id)

        user = (await session.scalars(query)).one_or_none()
        if not user:
            return exception_handler(models_logger, "ValueError", "User not found")

        followers = await cls.get_user_followers(user.id, session)
        followings = await cls.get_user_following(user.id, session)

        return UserResponseSchema(
            user=UserWithFollowSchema(
                **UserSchema.model_validate(user).model_dump(),
                followers=[UserSchema.model_validate(follow) for follow in followers],
                following=[UserSchema.model_validate(follow) for follow in followings]
            )
        )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the tweet")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), doc="ID of the tweet's author")
    tweet_data: Mapped[str] = mapped_column(String(280), doc="Content of the tweet, max 280 characters")
    tweet_media_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), doc="List of associated media IDs")

    author: Mapped["User"] = relationship(
        "User", back_populates="tweets", lazy="joined", doc="Relation to the tweet's author"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like",
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="joined",
        doc="List of likes for this tweet"
    )

    def __repr__(self) -> str:
        return f"<Tweet(id={self.id}, author_id={self.author_id}, content={self.tweet_data[:30]}...)>"

    @classmethod
    async def collect_tweet_data(cls, tweet: "Tweet", session: AsyncSession) -> TweetSchema:
        """Collect detailed tweet data including attachments and likes."""
        attachments = [await Media.get_media_link_by(media_id, session) for media_id in tweet.tweet_media_ids]
        author_data = UserSchema.model_validate(tweet.author).model_dump()
        likes_data = [LikeSchema.model_validate(like).model_dump() for like in tweet.likes]

        return TweetSchema(
            id=tweet.id,
            content=tweet.tweet_data,
            attachments=attachments,
            author=author_data,
            likes=likes_data
        )

    @classmethod
    async def is_tweet_exist(cls, tweet_id: int, session: AsyncSession) -> bool:
        """Check if a tweet exists by its ID."""
        return await session.scalar(select(exists().where(cls.id == tweet_id)))

    @classmethod
    async def get_tweets_selection(cls, username: str, session: AsyncSession) -> Union[
        TweetResponseSchema, ErrorResponseSchema]:
        """Get all tweets for a user."""
        try:
            user_id = await User.get_user_id_by(username, session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            query = (select(cls).join(Follow, Follow.following_id == cls.author_id)
                     .where(Follow.follower_id == user_id))
            tweets = (await session.scalars(query)).unique().all()

            tweet_schema = [await cls.collect_tweet_data(tweet, session) for tweet in tweets]

            return TweetResponseSchema(tweets=tweet_schema)
        except Exception as exc:
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def add_tweet(cls, username: str, tweet: NewTweetDataSchema, session: AsyncSession) -> Union[
        NewTweetResponseSchema, ErrorResponseSchema]:
        """Add a new tweet."""
        try:
            user_id = await User.get_user_id_by(username, session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            tweet_dict = tweet.model_dump()
            tweet_dict["author_id"] = user_id
            new_tweet = cls(**tweet_dict)

            session.add(new_tweet)
            await session.flush()
            await session.commit()
            return NewTweetResponseSchema(tweet_id=new_tweet.id)
        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def delete_tweet(cls, username: str, tweet_id: int, session: AsyncSession) -> Union[
        SuccessSchema, ErrorResponseSchema]:
        """Delete a tweet."""
        try:
            user_id = await User.get_user_id_by(username, session)
            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            query = delete(cls).returning(cls.id).where(cls.id == tweet_id, cls.author_id == user_id)
            request = await session.execute(query)
            if not request.fetchone():
                return exception_handler(models_logger, "ValueError", "Tweet with this ID does not exist")

            await session.commit()
            return SuccessSchema()

        except SQLAlchemyError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the media")
    link: Mapped[str] = mapped_column(String(100), doc="Path link to the media")

    def __repr__(self) -> str:
        return f"<Media(id={self.id}, link={self.link})>"

    @classmethod
    async def get_media_link_by(cls, media_id: int, session: AsyncSession) -> str:
        """Get media link by ID"""
        query = select(cls.link).where(cls.id == media_id)
        link = (await session.scalars(query)).one()
        return link

    @classmethod
    async def add_media(cls, link: str, session: AsyncSession) -> Union[NewMediaResponseSchema, ErrorResponseSchema]:
        """Add new media"""
        try:
            new_media = cls(link=link)
            session.add(new_media)
            await session.flush()
            await session.commit()
            return NewMediaResponseSchema(media_id=new_media.id)

        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, doc="The unique identifier of the like.")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), doc="The ID of the user who liked the tweet.")
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), doc="The ID of the tweet that was liked.")

    author: Mapped["User"] = relationship("User", back_populates="likes", doc="The user who liked the tweet.",
                                          lazy="joined")
    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="likes", doc="The tweet that was liked.")

    name: AssociationProxy[str] = association_proxy('author', 'name')

    def __repr__(self) -> str:
        return f"<Like(id={self.id}, author_id={self.user_id}, tweet_id={self.tweet_id})>"

    @classmethod
    async def is_like_exist(cls, user_id: int, tweet_id: int, session: AsyncSession) -> bool:
        """Check if a like exists for a tweet by a user."""
        return await session.scalar(select(exists().where(cls.user_id == user_id, cls.tweet_id == tweet_id)))

    @classmethod
    async def add_like(cls, username: str, tweet_id: int, session: AsyncSession) -> Union[
        SuccessSchema, ErrorResponseSchema]:
        """Add a like for a tweet."""
        try:
            user_id = await User.get_user_id_by(username, session)

            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")
            elif not await Tweet.is_tweet_exist(tweet_id, session):
                return exception_handler(models_logger, "ValueError", "Tweet with this tweet_id does not exist")
            elif await cls.is_like_exist(user_id, tweet_id, session):
                return exception_handler(models_logger, "ValueError", "Like already exists")

            session.add(cls(user_id=user_id, tweet_id=tweet_id))
            await session.commit()

            return SuccessSchema()

        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def remove_like(cls, username: str, tweet_id: int, session: AsyncSession) -> Union[
        SuccessSchema, ErrorResponseSchema]:
        """Remove a like from a tweet."""
        try:
            user_id = await User.get_user_id_by(username, session)

            if not user_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            if not await Tweet.is_tweet_exist(tweet_id, session):
                return exception_handler(models_logger, "ValueError", "Tweet with this ID does not exist")

            query = delete(cls).returning(cls.id).where(cls.tweet_id == tweet_id, cls.user_id == user_id)
            request = await session.execute(query)

            if not request.fetchone():
                return exception_handler(models_logger, "ValueError", "No like entry found for this user and tweet")

            await session.commit()
            return SuccessSchema()

        except SQLAlchemyError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))


class Follow(Base):
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, doc="The ID of the user who follows another user."
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, doc="The ID of the user who is being followed."
    )

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="followings", doc="The user who follows another user."
    )
    following: Mapped["User"] = relationship(
        "User", foreign_keys=[following_id], back_populates="followers", doc="The user who is being followed."
    )

    def __repr__(self) -> str:
        return (
            f"<Follow(follower_id={self.follower_id}, "
            f"followed_id={self.following_id})>"
        )

    @classmethod
    async def get_following_by(cls, username: str, session: AsyncSession) -> Sequence[int]:
        """Get following by username"""
        user_id = await User.get_user_id_by(username, session)

        if not user_id:
            return exception_handler(models_logger, "ValueError", "User with this username does not exist")

        query = select(cls.following_id).where(cls.follower_id == user_id)
        return (await session.scalars(query)).all()

    @classmethod
    async def follow(cls, username: str, following_id: int, session: AsyncSession) -> Union[
        SuccessSchema, ErrorResponseSchema]:
        """Add a follow relationship."""
        try:
            follower_id = await User.get_user_id_by(username, session)

            if not follower_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")
            elif not await User.is_user_exist(following_id, session):
                return exception_handler(models_logger, "ValueError", "User with this ID does not exist")

            session.add(cls(follower_id=follower_id, following_id=following_id))
            await session.commit()

            return SuccessSchema()

        except IntegrityError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))

    @classmethod
    async def remove_follow(cls, username: str, following_id: int, session: AsyncSession) -> Union[
        SuccessSchema, ErrorResponseSchema]:
        """Remove a follow relationship."""
        try:
            follower_id = await User.get_user_id_by(username, session)

            if not follower_id:
                return exception_handler(models_logger, "ValueError", "User with this username does not exist")

            if not await User.is_user_exist(following_id, session):
                return exception_handler(models_logger, "ValueError", "User with this ID does not exist")

            query = delete(cls).returning(cls.following_id, cls.follower_id).where(cls.follower_id == follower_id,
                                                                                   cls.following_id == following_id)
            request = await session.execute(query)

            if not request.fetchone():
                return exception_handler(models_logger, "ValueError",
                                         "No follow entry found for this follower ID and following ID")

            await session.commit()
            return SuccessSchema()

        except SQLAlchemyError as exc:
            await session.rollback()
            return exception_handler(models_logger, exc.__class__.__name__, str(exc))
