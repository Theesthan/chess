# Multiplayer Chess with Spectator Evaluation Bar

**Multiplayer Chess** is a Python-based chess application that supports real-time gameplay between two players and allows spectators to watch the game with a live evaluation bar powered by Stockfish.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Design and Architecture](#design-and-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

This project implements a multiplayer chess game with two main roles:

- **Players:** Join as either White or Black, make moves, and use additional controls like resigning or offering a draw.
- **Spectators:** Watch the game live with a full board view and an evaluation bar that shows Stockfish's analysis of the current position.

The application uses **Tkinter** for the GUI, **python-chess** for chess logic, and **Pillow** for image handling.

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

- **Spectator Evaluation Bar:**  
  Spectators see a live evaluation bar (green for White advantage, red for Black advantage) updated using Stockfish analysis.

---

## Design and Architecture

### GUI Design

- **Chessboard:**  
  An 8x8 grid of buttons displays the chess pieces using PNG images (e.g., `wP.png`, `bK.png`).  
  - **Players:** Board orientation adapts to player color (White or Black).  
  - **Spectators:** Always see the board in standard (White’s) orientation.

- **Timer and Controls:**  
  A timer shows each player's remaining time. Additional buttons allow players to **resign**, **offer a draw**, and toggle **full-screen mode**.

- **Evaluation Bar:**  
  Spectators see a vertical evaluation bar on the left, which updates every second using Stockfish to analyze the current board.

### Network Architecture

- **Server-Client Communication:**  
  The server listens for TCP connections, assigns roles, maintains the game state, and broadcasts updates (FEN strings, timer updates, game messages) to all clients.

- **Threading:**  
  The server runs separate threads for handling clients and for timer updates. The client also runs a background thread for network communication.

### Stockfish Integration

- **Engine Integration:**  
  Spectator clients launch Stockfish via the `python-chess.engine` module to evaluate the board position and display a graphical evaluation bar.

---

## Installation

### Prerequisites

- **Python 3.x**
- **Pip**

### Required Packages

Install the necessary Python modules using pip:

```bash
pip install python-chess Pillow
