# Multiplayer Chess with Spectator Evaluation Bar

**Multiplayer Chess** is a Python-based chess application that supports real-time gameplay between two players and allows spectators to watch the game with a live evaluation bar powered by Stockfish.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Design and Architecture](#design-and-architecture)
- [Installation](#installation)
  - [Python and Required Packages](#python-and-required-packages)
  - [Stockfish Setup](#stockfish-setup)
  - [Chess Piece Images](#chess-piece-images)
- [Usage](#usage)
  - [Running the Server](#running-the-server)
  - [Running the Client](#running-the-client)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

This project implements a **multiplayer chess game** with two main roles:

- **Players:** Join as either White or Black, make moves, and use additional controls like resigning or offering a draw.
- **Spectators:** Watch the game live with a full board view and an evaluation bar that shows Stockfish’s analysis of the current position.

The application uses **Tkinter** for the GUI, **python-chess** for chess logic, **Pillow** for image handling, and integrates **Stockfish** for position evaluation in spectator mode.

---

## Features

- **Real-Time Multiplayer:**  
  Supports two players and multiple spectators via TCP socket communication.

- **Chess Rules Enforcement:**  
  Utilizes the `python-chess` library to manage legal moves and board state.

- **Time Control:**  
  Both players have a **10-minute clock** displayed in **MM:SS** format.

- **Resign and Draw Options:**  
  Players can **resign** or **offer a draw** via GUI buttons.

- **Full-Screen Toggle:**  
  Easily switch between full-screen and windowed mode.

- **Spectator Evaluation Bar:**  
  Spectators see a live evaluation bar (green for White advantage, red for Black advantage) updated using Stockfish analysis.

---

## Design and Architecture

### GUI Design

- **Chessboard:**  
  An 8×8 grid of buttons displays the chess pieces (e.g., `wP.png`, `bK.png`).  
  - **Players:** Board orientation adapts based on the player’s color (White or Black).  
  - **Spectators:** Always see the board in standard (White’s) orientation.

- **Timer and Controls:**  
  A timer shows each player's remaining time in **MM:SS** format. Additional buttons allow players to **resign**, **offer a draw**, and toggle **full-screen** mode.

- **Evaluation Bar (Spectator Mode):**  
  A vertical evaluation bar appears on the left side for spectators. Stockfish analyzes the board every second, and the bar fills green (White advantage) or red (Black advantage), plus a numeric evaluation.

### Network Architecture

- **Server-Client Communication:**  
  The server listens for TCP connections, assigns roles, maintains the game state, and broadcasts updates (FEN strings, timer updates, game messages) to all clients.

- **Threading:**  
  The server runs separate threads for handling client connections and timer updates. The client also runs a background thread for network communication.

### Stockfish Integration

- **Engine Integration:**  
  Spectator clients launch Stockfish via the `python-chess.engine` module to evaluate the current board position and display the evaluation bar.

---

## Installation

### Python and Required Packages

1. **Python 3.x**: Make sure you have Python 3 installed.
2. **Pip**: Confirm you have the pip package manager available.
3. **Install Dependencies**:
   ```bash
   pip install python-chess Pillow
   ```
   - `python-chess` handles chess logic and engine communication.
   - `Pillow` is used for image handling in Tkinter.

### Stockfish Setup

1. **Download Stockfish**:  
   Visit [Stockfish Downloads](https://stockfishchess.org/download/) and download the appropriate binary for your operating system.

2. **Extract the Executable**:  
   Unzip the downloaded file to obtain the Stockfish executable (e.g., `stockfish_15_x64.exe`).

3. **Configure the Engine Path**:
   - **Option A**: Place the executable in your project directory and update the code with its full path.  
   - **Option B**: Add the directory containing Stockfish to your system's PATH.  

   Example in your Python code (replace the path accordingly):
   ```python
   self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\your_username\Downloads\stockfish_15_x64.exe")
   ```

4. **Unblock the File (if necessary)**:  
   If Windows blocks the executable, open PowerShell and run:
   ```powershell
   Unblock-File -Path "C:\Users\your_username\Downloads\stockfish_15_x64.exe"
   ```

### Chess Piece Images

Ensure that all chess piece images (e.g., `wP.png`, `bK.png`) are stored in the specified directory (for example, `C:\Users\thees\Pictures\Eko\Eko\eko\CN package\chesspng`). Make sure your code references this folder correctly.

---

## Usage

### Running the Server

1. **Open a terminal** in your project directory.
2. Run the server script:
   ```bash
   python server.py
   ```
   The server will start and listen on the designated IP and port.

### Running the Client

1. **Open a terminal** in your project directory.
2. Run the client script:
   ```bash
   python client.py
   ```
3. **Enter your username** and **the server IP** when prompted.
4. **Choose your role**:
   - **Player**: The board orientation adjusts based on your assigned color (White or Black).
   - **Spectator**: The evaluation bar appears on the left, showing Stockfish’s live analysis.
5. **Use the Full Screen button** to toggle between windowed and full-screen modes.

---

## Future Improvements

- **Enhanced Protocol**:  
  Implement a more robust messaging protocol (e.g., JSON-based) for better reliability and extensibility.

- **Game Logging**:  
  Save move history and game logs for later analysis.

- **Mobile Compatibility**:  
  Adapt the GUI for mobile devices or smaller screens.

- **Advanced Evaluation**:  
  Display additional Stockfish insights, such as best moves or multi-line analysis.

---

## License

Feel free to use this code

---
