# 3X-UI Telegram Bot Shop (WIP 🚧)
![3xui-shop](https://github.com/user-attachments/assets/d037594e-75d1-4394-a983-01e950dde278)

## Description

This project is a Telegram bot for selling VPN subscriptions. It works with 3X-UI.

### ⚠️ Attention!
Currently, the bot is under development and not fully functional. Some features are still in progress.

### 🚧 Current Tasks
- [x] Profile page
- [x] Subscription system
- [x] Telegram Stars payment
- [x] Yookassa payment
- [ ] Cryptomus payment
- [x] Promocode system
- [ ] Referral system
- [x] Support page
- [x] Apps page
- [ ] Trial subscription
- [ ] Notification
- [x] Admin panel
- [x] Subscription balancer
- [ ] Statistics

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

3. **Build the Docker image:**
   ```bash
   docker compose build
   ```

4. **Run the Docker container::**
   ```bash
   docker compose up -d
   ```

### Environment Variables Configuration

| Variable | Description |
|-|-|
| BOT_TOKEN | Telegram bot token |
| BOT_ADMINS | List of admin IDs (Telegram user IDs)
| BOT_DEV_ID | Telegram user ID of the bot developer |
| BOT_SUPPORT_ID | Telegram user ID of the support person |
| | |
| XUI_HOST | URL of the 3X-UI control panel (e.g., https://example.com/panel/) |
| XUI_USERNAME | Username for authentication in the 3X-UI control panel |
| XUI_PASSWORD | Password for authentication in the 3X-UI control panel |
| XUI_TOKEN | Token for authentication (if configured in the panel settings) |
| XUI_SUBSCRIPTION | URL for the subscription page (e.g., https://sub.example.com/user/) |
| | |
| LOG_LEVEL | Log level (e.g., INFO, DEBUG) |
| LOG_ARCHIVE_FORMAT | Log archive format (e.g., zip, gz) |

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

## 💸 Support the Project

A special thanks to the following individuals for their generous support:

- **Boto**, 
- [**@olshevskii-sergey**](https://github.com/olshevskii-sergey/)
- **Aleksey**

You can support me via the following methods:

- **Bitcoin:** `bc1ql53lcaukdv3thxcheh3cmgucwlwkr929gar0cy`
- **Ethereum:** `0xe604a10258d26c085ada79cdea9a84a5b0894b91`
- **USDT (TRC20):** `TUqDQ4mdtVJZC76789kPYBMzaLFQBDdKhE`
- **TON:** `UQDogBlLFgrxkVWvDJn6YniCwrJDro7hbk5AqDMoSzmBQ-KQ`

Any support will help me dedicate more time to development and accelerate the project!

## 👨‍💻 Contacts

- Telegram: [**@snoups**](https://t.me/snoups)
