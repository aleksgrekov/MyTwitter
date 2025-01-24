from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DELETE_CASCADE = "all, delete"
USER_ID_FK = "users.id"


class Base(DeclarativeBase):
    pass


class User(Base):
    """Model representing a user."""

    __tablename__ = "users"

    username_length = 128
    name_length = 30

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the user")
    username: Mapped[str] = mapped_column(
        String(username_length), unique=True, index=True, doc="Unique username"
    )
    name: Mapped[str] = mapped_column(String(name_length), doc="Full name of user")

    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="author",
        cascade="all",
        doc="List of tweets authored by the user",
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like",
        back_populates="author",
        cascade=DELETE_CASCADE,
        doc="List of likes by the user",
    )
    followings: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade=DELETE_CASCADE,
        doc="List of followings (users this user follows)",
    )
    followers: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade=DELETE_CASCADE,
        doc="List of followers (users following this user)",
    )

    def __repr__(self) -> str:
        """Return a string representation of the user."""
        user_id = self.id
        username = self.username
        name = self.name
        return f"User({user_id=}, {username=}, {name=})"


class Tweet(Base):
    """Model representing a tweet."""

    __tablename__ = "tweets"

    max_tweet_length = 280

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the tweet")
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(USER_ID_FK, ondelete="set null"), doc="ID of the tweet's author"
    )
    tweet_data: Mapped[str] = mapped_column(
        String(max_tweet_length), doc="Content of the tweet, max 280 characters"
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="tweets",
        lazy="joined",
        doc="Relation to the tweet's author",
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like",
        back_populates="tweet",
        cascade=DELETE_CASCADE,
        lazy="joined",
        doc="List of likes for this tweet",
    )

    media: Mapped[List["Media"]] = relationship(
        "Media",
        back_populates="tweet",
        cascade=DELETE_CASCADE,
        lazy="joined",
        doc="List of media for this tweet",
    )

    def __repr__(self) -> str:
        """Return a string representation of the tweet."""
        tweet_preview_length = 30
        tweet_id = self.id
        author_id = self.author_id
        tweet_data = self.tweet_data[:tweet_preview_length]
        return f"Tweet({tweet_id=}, {author_id=}, {tweet_data=}...)"


class Media(Base):
    """Model representing a media."""

    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, doc="Primary key of the media")
    link: Mapped[str] = mapped_column(String(100), doc="Path link to the media")
    tweet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tweets.id", ondelete="cascade"),
        doc="Tweet ID to which the media was attached",
    )

    tweet: Mapped["Tweet"] = relationship(
        "Tweet",
        back_populates="media",
        doc="The tweet to which the media was attached.",
    )

    def __repr__(self) -> str:
        """Return a string representation of the media."""
        media_id = self.id
        link = self.link
        tweet_id = self.tweet_id
        return f"Media({media_id=}, {link=}, {tweet_id=})"


class Like(Base):
    """Model representing a like."""

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(
        primary_key=True, doc="The unique identifier of the like."
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(USER_ID_FK, ondelete="set null"),
        doc="The ID of the user who liked the tweet.",
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id", ondelete="cascade"),
        doc="The ID of the tweet that was liked.",
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="likes",
        doc="The user who liked the tweet.",
        lazy="joined",
    )
    tweet: Mapped["Tweet"] = relationship(
        "Tweet", back_populates="likes", doc="The tweet that was liked."
    )

    name: AssociationProxy[str] = association_proxy("author", "name")

    def __repr__(self) -> str:
        """Return a string representation of the like."""
        like_id = self.id
        user_id = self.user_id
        tweet_id = self.tweet_id
        return f"Like({like_id=}, {user_id=}, {tweet_id=})"


class Follow(Base):
    """Model representing a follow relationship between users."""

    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(
        ForeignKey(USER_ID_FK, ondelete="cascade"),
        primary_key=True,
        doc="The ID of the user who follows another user.",
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey(USER_ID_FK, ondelete="cascade"),
        primary_key=True,
        doc="The ID of the user who is being followed.",
    )

    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="followings",
        doc="The user who follows another user.",
    )
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
        doc="The user who is being followed.",
    )

    def __repr__(self) -> str:
        """Return a string representation of the follow relationship."""
        return f"Follow({self.follower_id=}, {self.following_id=})"
