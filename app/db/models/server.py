from aiosqlite import IntegrityError
from sqlalchemy import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Server(Base):
    """
    Model representing a VPN server in the database.

    This model stores information about each VPN server, including its name, host,
    subscription, max clients, current load, and location.
    """

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription: Mapped[str] = mapped_column(String(255), nullable=False)
    max_clients: Mapped[int] = mapped_column(Integer, nullable=False)
    current_clients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    location: Mapped[str | None] = mapped_column(String(32), nullable=True)
    online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @classmethod
    async def get(cls, session: AsyncSession, name: str) -> "Server | None":
        """
        Get a server from the database based on the provided name.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            name (str): The server name to search for.

        Returns:
            Server | None: The server object if found, or None if not found.

        Example:
            server = await Server.get(session, name='server1')
        """
        filter = [Server.name == name]
        query = await session.execute(select(Server).where(*filter))
        return query.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, name: str, **kwargs) -> "Server":
        """
        Get a server from the database or create a new one if not found.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            name (str): The name of the server.
            kwargs (dict): Additional attributes for the server if creating a new one.

        Returns:
            Server: The server object.

        Example:
            server = await Server.create(session, name='server1', max_clients=100)
        """
        filter = [Server.name == name]
        query = await session.execute(select(Server).where(*filter))
        server = query.scalar_one_or_none()

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
        Update a server in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            server_id (int): The unique server ID.
            kwargs (dict): Attributes to be updated (e.g., max_clients=200).

        Example:
            await Server.update(session, server_id=1, max_clients=150)
        """
        filter = [Server.id == server_id]
        await session.execute(update(Server).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, name: str) -> bool:
        """
        Check if a server exists in the database based on the provided name.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            name (str): The server name to check.

        Returns:
            bool: True if the server exists, otherwise False.

        Example:
            exists = await Server.exists(session, name='server1')
        """
        filter = [Server.name == name]
        query = await session.execute(select(Server).where(*filter))
        return query.scalar_one_or_none() is not None

    @classmethod
    async def delete(cls, session: AsyncSession, name: str) -> bool:
        """
        Delete a server from the database based on the server's name.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            name (str): The name of the server to delete.

        Returns:
            bool: True if the server was successfully deleted, False otherwise.

        Example:
            deleted = await Server.delete(session, name='server1')
        """
        filter = [Server.name == name]
        async with session.begin():
            query = await session.execute(select(Server).where(*filter))
            server = query.scalar_one_or_none()

            if server:
                await session.delete(server)
                await session.commit()
                return True
            else:
                return False

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list["Server"]:
        """
        Retrieve all servers from the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.

        Returns:
            list[Server]: A list of all server objects.

        Example:
            servers = await Server.get_all(session)
        """
        query = await session.execute(select(Server))
        return query.scalars().all()
