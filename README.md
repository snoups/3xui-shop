<div align="center" markdown>

![3xui-shop](https://github.com/user-attachments/assets/282d10db-a355-4c65-a2cf-eb0e8ec8eed1)

**This project is a Telegram bot for selling VPN subscriptions. It works with 3X-UI.**

<p align="center">
    <a href="#Overview">Overview</a> •
    <a href="#️Installation-guide">Installation guide</a> •
    <a href="#Bugs-and-Feature-Requests">Bugs and Feature Requests</a> •
    <a href="#Support-the-Project">Support the Project</a>
</p>

![GitHub License](https://img.shields.io/github/license/snoups/3xui-shop)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/snoups/3xui-shop/total)
![GitHub Release](https://img.shields.io/github/v/release/snoups/3xui-shop)

![Static Badge](https://img.shields.io/badge/public_channel-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsn0ups)
![Static Badge](https://img.shields.io/badge/contact_me-white?style=social&logo=Telegram&logoColor=blue&logoSize=auto&labelColor=white&link=https%3A%2F%2Ft.me%2Fsnoups)
![GitHub Repo stars](https://img.shields.io/github/stars/snoups/3xui-shop)
</div>

## 📝 Overview

**3X-UI-SHOP** is a comprehensive solution designed to automate the sale of VPN subscriptions through Telegram.
The bot uses the **3X-UI** panel API for client management and supports multiple payment methods, including
**~~Cryptomus~~**, **YooKassa**, and **Telegram Stars**.

The bot enables efficient subscription sales with advanced features:

- **Server Manager**
    - Add, remove, disable, and check servers in the pool
    - Automatically distribute new clients across servers
    - Manage servers without restarting or reconfiguring the bot
    - ~~Replace a server with another one~~
- **Promocode System**
    - Create, edit, and delete promocodes
    - Promocodes for adding extra subscription time
    - ~~Promocodes with discounts~~
- **Notifications**
    - Send messages to a specific user or all users
    - Edit the last sent notification
    - Format text using HTML
    - Preview notifications before sending
    - System notifications for the developer and administrators
- **~~Referral Program~~**
    - ~~View referral statistics~~
    - ~~Reward users for inviting new members~~
- **~~Trial Period~~**
    - ~~Provide free trial subscriptions~~
    - ~~Configure and disable the trial period~~
- **Flexible Payment System**
    - Change the default currency
    - Easily extendable architecture for adding new payment gateways
    - ~~Add, edit, and delete subscription plans at any time~~
    - ~~Enable or disable payment methods~~
    - ~~Change the display order of payment options~~
- **~~User Editor~~**
    - ~~View user information~~
    - ~~View referral statistics~~
    - ~~View payment history and activated promocodes~~
    - ~~View server information~~
    - ~~Edit user subscriptions~~
    - ~~Block or unblock users~~
    - ~~Quick access to a user via forwarded messages~~
    - ~~Personal discounts for users~~

### ⚙️ Admin Panel
The bot includes a user-friendly admin panel with tools for efficient management.
Administrators do not have access to server management.

- **`Server Manager`**: Add, remove, disable, and check servers in the pool
- **`Bot Statistics`**: View usage analytics and performance data
- **`User Editor`**: Manage user accounts and subscriptions
- **`Promocode Editor`**: Create, edit, and delete promocodes
- **`Notification Sender`**: Send custom notifications to users
- **`Database Backup`**: Create and send database backups
- **`Maintenance Mode`**: Disable user access during updates or fixes


### 🚧 Current Tasks
- [ ] Cryptomus payment
- [ ] Trial period
- [ ] Referral system
- [ ] Statistics
- [ ] User editor
- [ ] Plans editor


## 🛠️ Installation guide

### Dependencies

Before starting the installation, make sure you have the installed [**Docker**](https://www.docker.com/)

### Docker Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/snoups/3xui-shop.git
   cd 3xui-shop
   ```

2. **Set up environment variables and plans:**
- Copy plans.example.json to plans.json and .env.example to .env:
    ```bash
    cp plans.example.json plans.json
    cp .env.example .env
    ```
    > Update plans.json file with your subscription plans. [(Subscription Plans Configuration)](#subscription-plans-configuration) 

    > Update .env file with your configuration. [(Environment Variables Configuration)](#environment-variables-configuration)

1. **Create acme.json file:**
   ```bash
   touch acme.json
   chmod 600 acme.json
   ```
   > This file is required for Traefik to generate certificates.

2. **Build the Docker image:**
   ```bash
   docker compose build
   ```

3. **Run the Docker container::**
   ```bash
   docker compose up -d
   ```

### Environment Variables Configuration

| Variable | Required | Default | Description |
|-|-|-|-|
| BOT_TOKEN | 🔴 | - | Telegram bot token |
| BOT_ADMINS | ⭕ | - | List of admin IDs (e.g., 123456789,987654321) |
| BOT_DEV_ID | 🔴 | - | ID of the bot developer |
| BOT_SUPPORT_ID | 🔴 | - | ID of the support person |
| BOT_DOMAIN | 🔴 | - | Domain of the bot (e.g., 3xui-shop.com) |
| BOT_PORT | ⭕ | 8080 | Port of the bot |
| | | |
| SHOP_EMAIL | ⭕ | support@3xui-shop.com | Email for receipts |
| SHOP_CURRENCY | ⭕ | RUB | Currency for buttons (e.g., RUB, USD, XTR) |
| ~~SHOP_TRIAL_ENABLED~~ | ⭕ | ~~True~~ | ~~Enable trial subscription~~ |
| ~~SHOP_TRIAL_PERIOD~~ | ⭕ | ~~3~~ | ~~Period of the trial subscription in days~~ |
| SHOP_PAYMENT_STARS_ENABLED | ⭕ | True | Enable Telegram stars payment |
| ~~SHOP_PAYMENT_CRYPTOMUS_ENABLED~~ | ⭕ | ~~False~~ | ~~Enable Cryptomus payment~~ |
| SHOP_PAYMENT_YOOKASSA_ENABLED | ⭕ | False | Enable Yookassa payment |
| | | |
| XUI_USERNAME | 🔴 | - | Username for authentication in the 3X-UI panel |
| XUI_PASSWORD | 🔴 | - | Password for authentication in the 3X-UI panel |
| XUI_TOKEN | ⭕ | - | Token for authentication (if configured in the panel) |
| | | |
| YOOKASSA_TOKEN | ⭕ | - | Token for YooKassa payment |
| YOOKASSA_SHOP_ID | ⭕ | - | Shop ID for YooKassa payment |
| | | |
| REDIS_HOST | ⭕ | 3xui-shop-redis | Host of the Redis server |
| REDIS_PORT | ⭕ | 6379 | Port of the Redis server |
| REDIS_DB_NAME | ⭕ | 0 | Name of the Redis database |
| REDIS_USERNAME | ⭕ | - | Username for authentication in the Redis server |
| REDIS_PASSWORD | ⭕ | - | Password for authentication in the Redis server |
| | | |
| LOG_LEVEL | ⭕ | DEBUG | Log level (e.g., INFO, DEBUG) |
| LOG_FORMAT | ⭕ | %(asctime)s \| %(name)s \| %(levelname)s \| %(message)s | Log format |
| LOG_ARCHIVE_FORMAT | ⭕ | zip | Log archive format (e.g., zip, gz) |
| | | |
| CF_API_KEY | 🔴 | - | Cloudflare API key |
| CF_API_EMAIL | 🔴 | - | Cloudflare API email |

### Subscription Plans Configuration

```json
{
    "durations": [30, 60, 180, 365],  // Available subscription durations in days

    "plans": 
    [
        {
            "devices": 1,  // Number of devices supported by the plan
            "prices": {
                "RUB": {  // Prices for Russian rubles (RUB)
                    "30": 70,   // Price for 30 days
                    "60": 120,  // Price for 60 days
                    "180": 300, // Price for 180 days
                    "365": 600  // Price for 365 days
                },
                "USD": {  // Prices for US dollars (USD)
                    "30": 0.7,  // Price for 30 days
                    "60": 1.2,  // Price for 60 days
                    "180": 3,   // Price for 180 days
                    "365": 6    // Price for 365 days
                },
                "XTR": {  // Prices for Telegram stars (XTR)
                    "30": 60,   // Price for 30 days
                    "60": 100,  // Price for 60 days
                    "180": 250, // Price for 180 days
                    "365": 500  // Price for 365 days
                }
            }
        },
        {
            // Next plan
        }
    ]
}
```

### Cloudflare Configuration

To ensure Cloudflare works correctly:

- Set `CF_API_KEY` and `CF_API_EMAIL` in the environment variables.
- Configure Cloudflare:
    - Add the bot’s domain.
    - Enable **Full (strict)** SSL/TLS mode.
    - Disable Proxy for the domain.
- `CF_API_KEY` can be found in the Cloudflare dashboard under API Tokens → Global API Key.
- Certificates are automatically configured when the container starts with Traefik, which also proxies requests to the bot.

### YooKassa Configuration

For YooKassa to work correctly:

- Specify the bot’s domain in the notification URL with `/yookassa` at the end (e.g., `https://3xui-shop.com/yookassa`).
- Select the following events:
    - `payment.succeeded`
    - `payment.waiting_for_capture`
    - `payment.canceled`


### 3X-UI Configuration

To ensure the bot functions correctly, you must configure the 3X-UI panel:

- Set up an Inbound **(the first one will be used)** for adding clients.
- Enable the subscription service with port `2096` and path `/user/`.
    > **Don’t forget to specify certificates for the subscription.**
- It is recommended to disable configuration encryption.

## 🐛 Bugs and Feature Requests

If you find a bug or have a feature request, please open an issue on the GitHub repository.
You're also welcome to contribute to the project by opening a pull request.

## 💸 Support the Project

A special thanks to the following individuals for their generous support:

- **Boto**
- [**@olshevskii-sergey**](https://github.com/olshevskii-sergey/)
- **Aleksey**

You can support me via the following methods:

- **Bitcoin:** `bc1ql53lcaukdv3thxcheh3cmgucwlwkr929gar0cy`
- **Ethereum:** `0xe604a10258d26c085ada79cdea9a84a5b0894b91`
- **USDT (TRC20):** `TUqDQ4mdtVJZC76789kPYBMzaLFQBDdKhE`
- **TON:** `UQDogBlLFgrxkVWvDJn6YniCwrJDro7hbk5AqDMoSzmBQ-KQ`

Any support will help me dedicate more time to development and accelerate the project!