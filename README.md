# Terminal Chat App

## Description

A terminal-based chat application made with Python sockets and threads. One server can handle multiple clients at the same time, while `prompt-toolkit` keeps incoming messages above the current input line.

The server listens on `127.0.0.1:5050`, so the chat is available on the same computer by default.

## Demo

https://github.com/user-attachments/assets/48c52d5b-a399-47a1-bba0-a4eb0a9f15b8

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
git clone https://github.com/MhmdRayanm7/terminal-chat-app.git
cd terminal-chat-app
```

Create a virtual environment:

```bash
python -m venv .venv
```

The activation and installation commands for Git Bash and PowerShell are shown below. The environment must be activated again in every new terminal.

## How to Run

The server and clients use `127.0.0.1:5050`, so they must run on the same computer.

### Git Bash

In the first terminal, clone the project, create the environment, install the dependency, and start the server:

```bash
git clone https://github.com/MhmdRayanm7/terminal-chat-app.git
cd terminal-chat-app
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python server.py
```

Keep the server running. Open a second terminal for a client:

```bash
cd terminal-chat-app
source .venv/Scripts/activate
python client.py
```

Open a third terminal and repeat the same client commands. Activate the virtual environment in every new terminal before running `client.py`.

### Windows PowerShell

In the first terminal, clone the project, create the environment, install the dependency, and start the server:

```powershell
git clone https://github.com/MhmdRayanm7/terminal-chat-app.git
cd terminal-chat-app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py server.py
```

Keep the server running. In every new client terminal, activate the same environment before starting the client:

```powershell
cd terminal-chat-app
.\.venv\Scripts\Activate.ps1
py client.py
```

Enter a unique username, then start sending messages. Press `Ctrl+C` or use `/quit` to close a client. Press `Ctrl+C` in the server terminal to stop the server.

## Commands

- `/users` — show all connected usernames.
- `/quit` — leave the chat and close the client.

Empty messages are ignored and are not sent to the server.

## Project Structure

```text
terminal-chat-app/
|-- demo/
|   |-- TCA.mp4         # short chat demonstration
|   `-- preview.png     # clickable video preview
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
