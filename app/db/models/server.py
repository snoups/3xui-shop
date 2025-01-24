from typing import Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from . import Base


class Server(Base):
    """
    Represents a VPN server in the database.

    Attributes:
        id (int): The unique server ID (primary key).
        name (str): The server's name.
        host (str): The server's host address or IP.
        subscription (str): The VPN subscription address.
        max_clients (int): The maximum number of clients.
        current_clients (int): The current number of connected clients.
        location (str | None): The server's location (optional).
        online (bool): The server's online status.
        users (list[User] | None): The users connected to the server (if any).
    """

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription: Mapped[str] = mapped_column(String(255), nullable=False)
    max_clients: Mapped[int] = mapped_column(Integer, nullable=False)
    current_clients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    location: Mapped[str | None] = mapped_column(String(32), nullable=True)
    online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="server")  # type: ignore

    def __repr__(self) -> str:
        """
        Represents the Server object as a string.

        Returns:
            str: A string representation of the Server object.
        """
        return (
            f"<Server(id={self.id}, name='{self.name}', host={self.host}, "
            f"subscription={self.subscription}, max_clients={self.max_clients}, "
            f"current_clients={self.current_clients}, location={self.location}, "
            f"online={self.online})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, id: str) -> Self | None:
        """
        Retrieve a server by its unique ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            id (int): The unique server ID.

        Returns:
            Server | None: The server object if found, otherwise None.

        Example:
            server = await Server.get(session, id=1)
        """
        filter = [Server.id == id]
        query = await session.execute(
            select(Server).options(selectinload(Server.users)).where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str) -> Self | None:
        """
        Retrieve a server by its unique name.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            name (str): The unique server name.

        Returns:
            Server | None: The server object if found, otherwise None.

        Example:
            server = await Server.get_by_name(session, name='server1')
        """
        filter = [Server.name == name]
        query = await session.execute(
            select(Server).options(selectinload(Server.users)).where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Self]:
        """
        Retrieve all servers.

        Arguments:
            session (AsyncSession): The SQLAlchemy session.

        Returns:
            list[Server]: A list of all servers.

        Example:
            servers = await Server.get_all(session)
        """
        query = await session.execute(select(Server).options(selectinload(Server.users)))
        return query.scalars().all()

    @classmethod
    async def create(cls, session: AsyncSession, name: str, **kwargs) -> Self | None:
        """
        Create or retrieve a server by name.

        Arguments:
            session (AsyncSession): The SQLAlchemy session.
            name (str): The server name.
            kwargs (dict): Additional server attributes.

        Returns:
            Server | None: The server if created or already exists, else None.

        Example:
            server = await Server.create(session, name='server1', max_clients=100)
        """
        server = await Server.get_by_name(session, name)

        if server is None:
            server = Server(name=name, **kwargs)
            session.add(server)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return None

        return server

    @classmethod
    async def update(cls, session: AsyncSession, server_id: int, **kwargs) -> None:
        """
        Update server attributes.

        Arguments:
            session (AsyncSession): The SQLAlchemy session.
            server_id (int): The server ID.
            kwargs (dict): Attributes to update.

        Example:
            await Server.update(session, server_id=1, max_clients=150)
        """
        filter = [Server.id == server_id]
        await session.execute(update(Server).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def delete(cls, session: AsyncSession, name: str) -> bool:
        """
        Delete a server by name.

        Arguments:
            session (AsyncSession): The SQLAlchemy session.
            name (str): The server name.

        Returns:
            bool: True if the server was deleted, else False.

        Example:
            deleted = await Server.delete(session, name='server1')
        """
        server = await Server.get_by_name(session, name)

        if server:
            await session.delete(server)
            await session.commit()
            return True
        else:
            return False

    @classmethod
    async def exists(cls, session: AsyncSession, name: str) -> bool:
        """
        Check if a server exists.

        Arguments:
            session (AsyncSession): The SQLAlchemy session.
            name (str): The server name.

        Returns:
            bool: True if the server exists, else False.

        Example:
            exists = await Server.exists(session, name='server1')
        """
        return await Server.get_by_name(session, name) is not None
