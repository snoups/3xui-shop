import logging

from aiogram import F, Router
from aiogram.utils.i18n import gettext as _

from . import payment, promocode, subscription

logger = logging.getLogger(__name__)
router = Router(name=__name__)

router.include_router(payment.router)
router.include_router(promocode.router)
router.include_router(subscription.router)
