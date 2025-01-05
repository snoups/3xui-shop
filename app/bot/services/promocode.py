import logging
import uuid

from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Promocode

logger = logging.getLogger(__name__)


class PromocodeService:
    """
    Service for managing promocodes, including creation, retrieval, deletion, and activation.

    Provides methods for handling promocodes, such as generating new promocodes,
    retrieving them by code, deleting, and activating them.

    Attributes:
        session (AsyncSession): Database session for operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes the PromocodeService.

        Arguments:
            session (AsyncSession): The database session to interact with the database.
        """
        self.session = session
        logger.info("PromocodeService initialized.")

    async def get_promocode(self, code: str) -> Promocode | None:
        """
        Retrieves a promocode from the database.

        Arguments:
            code (str): The promocode to retrieve.

        Returns:
            Promocode | None: The promocode if found, otherwise None.
        """
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)
            logger.debug(
                f"Promocode {code} {'retrieved' if promocode else 'not found'} in the database."
            )
            return promocode

    async def create_promocode(self, duration: int) -> Promocode:
        """
        Creates a new promocode with the given duration.

        Arguments:
            duration (int): The duration in days for the promocode.

        Returns:
            Promocode: The created promocode.
        """
        async with self.session() as session:
            while True:
                code = self._generate_code()
                if not await Promocode.exists(session, code=code):
                    break
                logger.debug(f"Promocode {code} already exists. Retrying code generation.")

            promocode = await Promocode.create(session, code=code, duration=duration)
            logger.info(f"Promocode {code} created with a duration of {duration} days.")
            return promocode

    async def delete_promocode(self, code: str) -> bool:
        """
        Deletes a promocode by its code.

        Arguments:
            code (str): The promocode to delete.

        Returns:
            bool: True if the promocode was deleted, False if not found.
        """
        async with self.session() as session:
            if await Promocode.delete(session, code=code):
                logger.info(f"Promocode {code} deleted successfully.")
                return True

            logger.debug(f"Promocode {code} not found for deletion.")
            return False

    async def update_promocode(self, code: str, new_duration: int) -> Promocode | None:
        """
        Updates the duration of an inactive promocode.

        If the promocode is active, the duration cannot be updated.

        Arguments:
            code (str): The promocode to update.
            new_duration (int): The new duration in days.

        Returns:
            Promocode | None: The updated promocode if successful, otherwise None.
        """
        session: AsyncSession
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)

            if not promocode:
                logger.debug(f"Promocode {code} not found for update.")
                return None

            if promocode.is_activated:
                logger.debug(f"Promocode {code} is active and cannot be updated.")
                return None

            promocode.duration = new_duration
            await session.commit()
            logger.info(f"Promocode {code} updated to {new_duration} days.")
            return promocode

    async def activate_promocode(self, code: str, user_id: int) -> bool:
        """
        Activates a promocode for a user.

        Marks the promocode as activated and assigns it to the specified user.

        Arguments:
            code (str): The promocode to activate.
            user_id (int): The ID of the user activating the promocode.

        Returns:
            bool: True if successfully activated, False if not found or already activated.
        """
        session: AsyncSession
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)

            if not promocode:
                logger.debug(f"Promocode {code} not found for activation.")
                return False

            if promocode.is_activated:
                logger.debug(f"Promocode {code} is already activated.")
                return False

            promocode.is_activated = True
            promocode.activated_by = user_id
            await session.commit()
            logger.info(f"Promocode {code} successfully activated by user {user_id}.")
            return True

    async def deactivate_promocode(self, code: str) -> bool:
        """
        Deactivates a promocode.

        Marks the promocode as not activated and clears the user who activated it.

        Arguments:
            code (str): The promocode to deactivate.

        Returns:
            bool: True if successfully deactivated, False if not found or already deactivated.
        """
        session: AsyncSession
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)

            if not promocode:
                logger.debug(f"Promocode {code} not found for deactivation.")
                return False

            if not promocode.is_activated:
                logger.debug(f"Promocode {code} is already deactivated.")
                return False

            promocode.is_activated = False
            promocode.activated_by = None
            await session.commit()
            logger.debug(f"Promocode {code} successfully deactivated.")
            return True

    def _generate_code(self) -> str:
        """
        Generates a unique promocode code.

        Returns:
            str: The generated promocode code.
        """
        code = str(uuid.uuid4()).replace("-", "").upper()[:8]
        logger.debug(f"Generated promocode: {code}")
        return code
