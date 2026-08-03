# Terminal Chat App

## Description

A terminal-based chat application made with Python sockets and threads. One server can handle multiple clients at the same time, while `prompt-toolkit` keeps incoming messages above the current input line.

The server listens on `127.0.0.1:5050`, so the chat is available on the same computer by default.

## Features

- Multiple clients can chat at the same time.
- Every username must be unique and cannot be empty.
- Join, leave, and server-disconnect messages.
- Colored messages with usernames and timestamps.
- Incoming messages do not break the current input line.
- `/users` shows all online users.
- `/quit` closes the client normally.
- Safe handling for sudden client or server disconnections.
- Support for long, fast, and Unicode messages.

## Requirements

- Python 3.9 or newer.
- Windows Terminal, PowerShell, Command Prompt, or Git Bash.
- The package listed in `requirements.txt`.

## Installation

Clone the project and enter its folder:

```bash
git clone <repository-url>
cd terminal-chat-app
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

Install the only external dependency:

```bash
python -m pip install -r requirements.txt
```

## How to Run

Open one terminal and start the server:

```bash
python server.py
```

Keep the server running. Open a new terminal for each client and run:

```bash
python client.py
```

Enter a unique username, then start sending messages. Press `Ctrl+C` or use `/quit` to close a client. Press `Ctrl+C` in the server terminal to stop the server.

## Commands

- `/users` — show all connected usernames.
- `/quit` — leave the chat and close the client.

Empty messages are ignored and are not sent to the server.

## Project Structure

```text
terminal-chat-app/
|-- client.py           # connects user and displays terminal chat UI
|-- server.py           # accepts clients and broadcasts chat data
|-- terminal_colors.py  # shared ANSI colors and color helper
|-- requirements.txt    # external Python packages
`-- README.md            # setup and usage guide
```

## How It Works

The server creates a TCP socket and starts one thread for every connected client. It stores active sockets in `clients` and maps each socket to a username in `usernames`. A lock protects these shared values, and another lock keeps fast broadcasts in the correct order.

Messages use UTF-8 and end with a newline. This lets both sides rebuild complete messages even when a long message arrives in multiple network chunks. The server sends plain text only; terminal colors are added locally when each side displays a message.

The client uses one thread to receive messages while the main thread reads input. `PromptSession` and `patch_stdout` redraw incoming messages above `Message ›` without deleting text that is already being typed.
