Multiplayer Chess with Spectator Evaluation Bar
This project is a Python-based multiplayer chess game with a rich graphical interface using Tkinter. The game supports two roles:

Players: Can join as White or Black, make moves, and use features like resigning or offering a draw.

Spectators: Can watch the game live with an evaluation bar powered by Stockfish showing the current board's analysis.

Table of Contents
Overview

Features

Design and Architecture

Installation

Usage

Future Improvements

License

Overview
This project implements a multiplayer chess game with both player and spectator modes. The clients communicate with a central server via TCP sockets. The application supports the following functionalities:

Players choose a role (White or Black) and can make legal moves.

Spectators view the board in standard (White's) orientation and receive real-time updates.

A timer is maintained for both players (10 minutes each) and is updated in MM:SS format.

Players can resign or offer a draw, with corresponding actions on the server.

Spectators benefit from an evaluation bar powered by Stockfish, which analyzes the board position and displays a graphical representation (green for White advantage, red for Black advantage).

Features
Real-Time Multiplayer: Supports two players and multiple spectators.

Chess Rules Compliance: Uses the python-chess library to enforce legal moves.

Time Control: Both players have a 10-minute clock displayed in MM:SS format.

Resign & Draw Options: Players can resign or offer a draw via GUI buttons.

Full-Screen Toggle: Easily switch between windowed and full-screen mode.

Spectator Evaluation Bar: Spectators see a live evaluation bar calculated by Stockfish.

Cross-Platform: Built using Python, Tkinter, and standard libraries.

Design and Architecture
GUI Design
Tkinter Interface: The user interface is built with Tkinter. The main window displays:

The chessboard (an 8x8 grid of buttons). In player mode, the board is oriented based on the player’s color; spectators always see the board in White's orientation.

A timer label at the bottom shows the remaining time for both players.

Control buttons allow players to resign, offer a draw, or toggle full-screen mode.

In spectator mode, an evaluation bar appears on the left side of the board. This bar updates every second with Stockfish’s analysis.

Network Architecture
Server-Client Communication:

The server listens for incoming TCP connections.

Upon connection, clients send their username and choose a role (player or spectator).

The server assigns roles (White/Black) to players and maintains the board state.

The server broadcasts FEN strings, timer updates, and game messages (e.g., resignations, draw offers, game over messages) to all connected clients.

Threading:

The server runs a timer thread that updates player clocks only when both players are present.

The client uses a separate thread to receive network messages asynchronously.

Integration with Stockfish
Stockfish Engine:

In spectator mode, the client launches Stockfish using the python-chess engine interface.

The current board position is analyzed every second.

The evaluation is visualized via a graphical evaluation bar (green indicates White advantage and red indicates Black advantage).

Code Organization
Client Code: Handles GUI, network communication, image loading, and full-screen functionality.

Server Code: Manages game state, move validation, timers, and broadcasting messages.

Common Libraries: Uses python-chess for chess logic and Pillow for image processing.

Installation
Prerequisites
Python 3.x: Ensure you have Python 3 installed.

Pip: Package installer for Python.

Required Libraries: Install via pip:

bash
Copy
Edit
pip install python-chess Pillow
Stockfish:

Download the Stockfish executable from Stockfish Downloads.

Extract the executable.

Place the executable in a known location (or add it to your system PATH).

Update the engine path in the client code if needed (e.g., in chess.engine.SimpleEngine.popen_uci("stockfish")).

Setup
Clone or Download the Project Repository.

Place Chess Piece Images:
Ensure your chess piece images (named wP.png, wN.png, wB.png, etc.) are stored in the folder (e.g., C:\Users\thees\Pictures\Eko\Eko\eko\CN package\chesspng).

Update Configurations:
Verify the paths for images and Stockfish executable in the code.

Usage
Running the Server
Open a terminal.

Navigate to the project directory.

Run the server script:

bash
Copy
Edit
python server.py
The server will listen for incoming connections on the specified IP and port.

Running the Client
Open a terminal.

Navigate to the project directory.

Run the client script:

bash
Copy
Edit
python client.py
A dialog will prompt you for your username and server IP.

Choose your role (player or spectator).

Players: The board orientation adjusts based on your color.

Spectators: The evaluation bar appears on the left side.

Use the "Full Screen" button to toggle full-screen mode.

Future Improvements
Enhanced Protocol: Implement a more robust protocol with message framing or JSON messages.

Persistent Game History: Save game logs and moves for later analysis.

Mobile Support: Adapt the GUI for mobile devices.

Improved Evaluation: Display additional Stockfish analysis details (e.g., best move suggestions).

License
This project is open source. Feel free to modify and distribute according to your needs.

