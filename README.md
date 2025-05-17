# Page-Bot

**Page-Bot** is an advanced Facebook Messenger bot built with Flask, SQLite, and the Facebook Graph API. It is designed for robust message handling, persistent user context, command execution, media processing, and admin error reporting. This bot is suitable for both personal and organizational use, offering extensibility and transparency through its database-backed memory and modular command handler.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Database Schema](#database-schema)
- [Endpoints](#endpoints)
- [Core Functionalities](#core-functionalities)
  - [Message Handling](#message-handling)
  - [Command Processing](#command-processing)
  - [Image & Attachment Handling](#image--attachment-handling)
  - [Persistent Conversation History](#persistent-conversation-history)
  - [Admin Error Reporting](#admin-error-reporting)
  - [API Integration](#api-integration)
  - [Status & Uptime](#status--uptime)
- [Logging](#logging)
- [Extending Page-Bot](#extending-page-bot)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Webhook Integration** with Facebook Messenger.
- **Command Parsing** with customizable prefix.
- **Persistent Conversation Memory** per user.
- **Image Upload and Processing**.
- **Extensible Command Handler** via external `messageHandler`.
- **Admin Error Reporting** on all exceptions.
- **Rich Logging** to file and console for debugging.
- **CORS-Enabled** REST API for custom integrations.
- **Uptime and Health Status Endpoint**.
- **SQLite Database** for memory and logging.

---

## Architecture Overview

```
+-------------------+       +---------------------+
| Facebook Messenger|<----->| Flask Webhook       |
+-------------------+       |  (app.py)           |
                            +----------+----------+
                                       |
                                       v
                            +---------------------+
                            | SQLite Database     |
                            +---------------------+
                                       |
                                       v
                            +---------------------+
                            | messageHandler      |
                            +---------------------+
```

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- Facebook Page and App for Messenger API access
- Facebook Page Access Token and Verify Token.

### Installation Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Sman12345678/Page-Bot.git
   cd Page-Bot
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**  
   Copy `.env.example` to `.env` and fill in required values (see [Environment Variables](#environment-variables)).

4. **Run the bot:**
   ```sh
   python app.py
   ```
   The server runs on `0.0.0.0:3000` by default.

5. **Set up Facebook Webhook:**  
   - Register your webhook endpoint (`/webhook`) in the Facebook App Dashboard.
   - Use your `VERIFY_TOKEN` for verification.

---

## Environment Variables

The bot loads configuration from `.env` using `python-dotenv`. Required variables:

| Name              | Description                                 | Example                      |
|-------------------|---------------------------------------------|------------------------------|
| `PAGE_ACCESS_TOKEN`| Facebook Page Access Token                  | `EAAG...ZDZD`                |
| `VERIFY_TOKEN`     | Token for webhook verification              | `my_secret_token`            |
| `ADMIN_ID`         | Facebook User ID for admin notifications    | `1234567890123456`           |
| `PREFIX`           | Command prefix (default: `/`)               | `/`                          |

---

## Database Schema

**SQLite file:** `bot_memory.db`

- **conversations:**  
  Stores all messages exchanged, including sender and type.

  | id | user_id | timestamp | message | sender | message_type | metadata |
  |----|---------|-----------|---------|--------|-------------|----------|

- **user_context:**  
  Tracks conversation state and history for each user.

  | user_id | last_interaction | conversation_state | user_preferences | conversation_history |

- **message_logs:**  
  Logs status of all sent messages for debugging and analytics.

  | id | timestamp | sender_id | message_type | status | error_message | metadata |

---

## Endpoints

### `GET /webhook`

- Facebook Messenger verification endpoint.

### `POST /webhook`

- Main webhook for receiving Messenger events (messages, attachments).
- Handles:
  - User text messages
  - Image attachments
  - Command processing
  - Error handling and admin notification

### `GET /api?query=<text>&uid=<optional id>`

- REST API for programmatic access.
- Simulates a user message, stores it, gets a response, and returns JSON.

  **Example:**
  ```
  GET /api?query=Hello+world&uid=api_test_user
  ```

### `GET /status`

- Returns JSON with bot's status, uptime, and initialization state.

### `GET /`

- Home route. Renders `index.html` (static page).

---

## Core Functionalities

### Message Handling

- Receives messages from Messenger or API.
- All messages are stored in the database with metadata.
- Supports both text and image messages.

### Command Processing

- Messages starting with the `PREFIX` (default: `/`) are parsed as commands.
- Commands are routed to the `messageHandler.handle_text_command()` function.
- Supports both single and multi-response commands.

### Image & Attachment Handling

- Image attachments from Messenger are downloaded and stored.
- Images are uploaded to Facebook Graph API for re-sending.
- Image analysis is performed via `messageHandler.handle_attachment()` with conversation history.

### Persistent Conversation History

- Each user has a rolling conversation history (last 20 messages).
- Used for context in command and message handling.

### Admin Error Reporting

- All exceptions in message handling or webhook processing trigger the `report()` function.
- Admin receives a Messenger alert with timestamp and error details.

### API Integration

- `/api` endpoint enables external apps to interact with the bot as a user.
- Stores messages, updates history, and returns bot response as JSON.

### Status & Uptime

- `/status` endpoint returns:
  - Online status
  - Uptime in hours/minutes/seconds
  - Initialization state
  - Current server UTC timestamp

---

## Logging

- Logs are written to `app_debug.log` and streamed to the console.
- Logs include:
  - Incoming requests
  - Message and command processing
  - Facebook API interactions
  - Errors and stack traces

---

## Extending Page-Bot

- **Command logic** is handled by `messageHandler` (external module).
- Add or customize commands by editing `messageHandler.py`.
- Add new message types or integrations by expanding `send_message`, `process_command_response`, or `handle_command_message`.

---

## Troubleshooting

- **Bot not responding:**  
  - Check `app_debug.log` for errors.
  - Ensure Facebook Page Access Token and Verify Token are correct.
  - Confirm webhook is properly registered with Facebook.
  - Ensure admin has previously interacted with the bot (for reporting).

- **Admin not receiving reports:**  
  - Ensure `ADMIN_ID` in `.env` is a valid Facebook user ID (string).
  - Check logs for Messenger API errors.

- **Database errors:**  
  - Delete or move `bot_memory.db` to reset if schema is corrupted.
  - Ensure the app has write permissions to the directory.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Credits

Developed by Suleiman (https://github.com/Sman12345678).

---
