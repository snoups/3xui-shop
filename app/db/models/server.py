import logging
from typing import Any, Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from . import Base
from .user import User

logger = logging.getLogger(__name__)


class Server(Base):
    """
    Represents a VPN server in the database.

    Attributes:
        id (int): Unique identifier for the server.
        name (str): Unique server name.
        host (str): Server host address or IP.
        subscription (str): VPN subscription address.
        max_clients (int): Maximum allowed number of clients.
        location (str | None): Server location if available.
        online (bool): Indicates whether the server is online.
        users (list[User]): List of users associated with the server.
    """

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription: Mapped[str] = mapped_column(String(255), nullable=False)
    max_clients: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String(32), nullable=True)
    online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="server")  # type: ignore

    @hybrid_property
    def current_clients(self) -> int:
        return len(self.users)

    @current_clients.expression
    def current_clients(cls):
        return (
            select(func.count(User.id)).where(User.server_id == Server.id).label("current_clients")
        )

    def __repr__(self) -> str:
        return (
            f"<Server(id={self.id}, name='{self.name}', host={self.host}, "
            f"subscription={self.subscription}, max_clients={self.max_clients}, "
            f"location={self.location}, online={self.online})>"
        )

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int) -> Self | None:
        filter = [Server.id == id]
        query = await session.execute(
            select(Server).options(selectinload(Server.users)).where(*filter)
        )
        server = query.scalar_one_or_none()

        if server:
            logger.debug(f"Server {id} retrieved from the database.")
            return server

        logger.warning(f"Server {id} not found in the database.")
        return None

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str) -> Self | None:
        filter = [Server.name == name]
        query = await session.execute(
            select(Server).options(selectinload(Server.users)).where(*filter)
        )
        server = query.scalar_one_or_none()

        if server:
            logger.debug(f"Server {name} retrieved from the database.")
            return server

        logger.warning(f"Server {name} not found in the database.")
        return None

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Self]:
        query = await session.execute(select(Server).options(selectinload(Server.users)))
        servers = query.scalars().all()
        logger.debug(f"Retrieved {len(servers)} servers from the database.")
        return servers

    @classmethod
    async def get_least_loaded(cls, session: AsyncSession) -> Self | None:
        filter = [Server.online == True]
        query = await session.execute(
            select(Server)
            .options(selectinload(Server.users))
            .where(*filter)
            .order_by(Server.current_clients)
        )
        server = query.scalar_one_or_none()

        if server:
            logger.debug(f"Server with least load retrieved from the database.")
            return server

        logger.warning(f"Server with least load not found in the database.")
        return None

    @classmethod
    async def get_available(cls, session: AsyncSession) -> Self | None:
        filter = [Server.online == True, Server.current_clients < Server.max_clients]
        query = await session.execute(
            select(Server)
            .options(selectinload(Server.users))
            .where(*filter)
            .order_by(Server.current_clients)
        )
        server = query.scalar_one_or_none()

        if server:
            logger.info(
                f"Found server with free slots: {server.name} "
                f"(clients: {server.current_clients}/{server.max_clients})"
            )
            return server

        server = await Server.get_least_loaded(session)

        if server:
            logger.warning(
                f"No servers with free slots. Using least loaded server: {server.name} "
                f"(clients: {server.current_clients}/{server.max_clients})"
            )
            return server

        logger.critical("No servers found")
        return None

    @classmethod
    async def create(cls, session: AsyncSession, name: str, **kwargs: Any) -> Self | None:
        server = await Server.get_by_name(session=session, name=name)

        if server:
            logger.warning(f"Server {name} already exists.")
            return None

        server = Server(name=name, **kwargs)
        session.add(server)

        try:
            await session.commit()
            logger.info(f"Server {name} created.")
            return server
        except IntegrityError as exception:
            await session.rollback()
            logger.error(f"Error occurred while creating server {name}: {exception}")
            return None

    @classmethod
    async def update(cls, session: AsyncSession, name: str, **kwargs: Any) -> Self | None:
        server = await Server.get_by_name(session=session, name=name)

        if server:
            filter = [Server.id == server.id]
            await session.execute(update(Server).where(*filter).values(**kwargs))
            await session.commit()
            logger.info(f"Server {name} updated.")
            return server

        logger.warning(f"Server {name} not found for update.")
        return None

    @classmethod
    async def delete(cls, session: AsyncSession, name: str) -> bool:
        server = await Server.get_by_name(session=session, name=name)

        if server:
            await session.delete(server)
            await session.commit()
            logger.info(f"Server {name} deleted.")
            return True

        logger.warning(f"Server {name} not found for deletion.")
        return False
