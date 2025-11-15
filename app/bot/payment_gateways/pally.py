import hashlib
import logging
from typing import Any

import aiohttp
from aiogram.enums import ContentType
from aiogram.types import BufferedInputFile, LabeledPrice, Message, FSInputFile
from aiogram.utils.i18n import gettext as _
from aiohttp.web import Application, Request, Response, json_response

from app.bot.utils.constants import Currency, TransactionStatus
from app.config import Config
from app.db.models import Transaction

from ._gateway import PaymentGateway, logger

logger = logging.getLogger(__name__)


class PallyPaymentGateway(PaymentGateway):
    name = "pally"
    currency = Currency.RUB
    callback = "/pally"

    async def create_payment(self, data: SubscriptionData) -> str:
        api_token = self.config.pally.API_TOKEN
        shop_id = self.config.pally.SHOP_ID

        if not api_token or not shop_id:
            logger.error("Pally API token or shop ID is not set.")
            raise ValueError("Pally API token or shop ID is not set.")

        payment_id = data.generate_payment_id(self.name)
        amount = str(data.price)
        description = _("payment:misc:subscription_payment_description").format(
            devices=data.devices,
            duration=data.duration,
        )
        custom_data = data.pack()

        headers = {"Authorization": f"Bearer {api_token}"}
        payload = {
            "amount": amount,
            "order_id": payment_id,
            "description": description,
            "type": "normal",
            "shop_id": shop_id,
            "currency_in": self.currency.code,
            "custom": custom_data,
            "payer_pays_commission": "1",
            "name": "Платёж",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://pal24.pro/api/v1/bill/create", headers=headers, data=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()

        if result.get("success") == "true":
            link_url = result.get("link_page_url")
            if not link_url:
                raise ValueError("Pally API response did not contain link_page_url")

            async with self.session() as session:
                transaction = Transaction(
                    payment_id=payment_id,
                    user_id=data.user_id,
                    gateway=self.name,
                    amount=data.price,
                    currency=self.currency.code,
                    status=TransactionStatus.PENDING,
                    subscription=data.pack(),
                )
                await transaction.save(session)
            return link_url
        else:
            error_message = result.get("message", "Unknown error")
            logger.error(f"Pally payment creation failed: {error_message}")
            raise ValueError(f"Pally payment creation failed: {error_message}")

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        await self._on_payment_succeeded(payment_id)

    async def handle_payment_canceled(self, payment_id: str) -> None:
        await self._on_payment_canceled(payment_id)

    async def webhook(self, request: Request) -> Response:
        api_token = self.config.pally.API_TOKEN
        if not api_token:
            logger.error("Pally API token is not set for webhook validation.")
            return json_response({"status": "error", "message": "API token not configured"}, status=500)

        try:
            data = await request.post()
            logger.debug(f"Pally webhook received data: {data}")

            inv_id = data.get("InvId")
            amount = data.get("OutSum") # For success callback, Pally sends OutSum
            currency = data.get("CurrencyIn")
            status = data.get("Status") # For postback, Pally sends Status
            signature = data.get("SignatureValue")
            bill_id = data.get("TrsId") # For postback, Pally sends TrsId

            if status is None: # This is a success/fail redirect, not a postback
                # For success/fail redirect, signature is md5($OutSum . ":" . $InvId . ":" . $apiToken) 
                # For postback, signature is md5($Status . ":" . $InvId . ":" . $OutSum . ":" . $apiToken) - according to my prior search
                # Let's re-verify the signature format from the web search results carefully.
                # Websearch results say: strtoupper(md5($OutSum . ":" . $InvId . ":" . $apiToken)) for success/fail POST
                # And for Payment postback: strtoupper(md5($Status . ":" . $InvId . ":" . $OutSum . ":" . $apiToken))

                if not inv_id or not amount or not currency or not signature:
                    logger.error("Missing parameters in Pally success/fail webhook.")
                    return json_response({"status": "error", "message": "Missing parameters"}, status=400)

                # Signature validation for redirect (Success/Fail POST request)
                expected_signature = hashlib.md5(f"{amount}:{inv_id}:{api_token}".encode()).hexdigest().upper()

                if expected_signature != signature:
                    logger.warning(f"Invalid signature for Pally redirect: Expected {expected_signature}, Got {signature}")
                    return json_response({"status": "error", "message": "Invalid signature"}, status=403)

                # Pally redirects users, so we don't need to do anything here except return 200 OK
                # The actual status update should come from the postback.
                logger.info(f"Pally redirect received for {inv_id}. Waiting for postback.")
                return json_response({"status": "ok"})

            else: # This is a postback
                # Signature validation for postback (Payment postback)
                # strtoupper(md5($Status . ":" . $InvId . ":" . $OutSum . ":" . $apiToken))
                if not status or not inv_id or not amount or not signature:
                    logger.error("Missing parameters in Pally postback webhook.")
                    return json_response({"status": "error", "message": "Missing parameters"}, status=400)

                expected_signature = hashlib.md5(f"{status}:{inv_id}:{amount}:{api_token}".encode()).hexdigest().upper()

                if expected_signature != signature:
                    logger.warning(f"Invalid signature for Pally postback: Expected {expected_signature}, Got {signature}")
                    return json_response({"status": "error", "message": "Invalid signature"}, status=403)

                if status == "SUCCESS":
                    await self.handle_payment_succeeded(inv_id)
                elif status == "FAIL":
                    await self.handle_payment_canceled(inv_id)
                else:
                    logger.warning(f"Unknown Pally postback status: {status} for payment {inv_id}")
                    return json_response({"status": "error", "message": "Unknown status"}, status=400)

                return json_response({"status": "ok"})

        except Exception as e:
            logger.error(f"Error processing Pally webhook: {e}", exc_info=True)
            return json_response({"status": "error", "message": str(e)}, status=500)
