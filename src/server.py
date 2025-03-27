import socket
import threading
import chess
import os
import time

# Initialize game state and timers
board = chess.Board()
lock = threading.Lock()
players = {'white': None, 'black': None}
spectators = []
current_turn = chess.WHITE
white_time = 600  # seconds
black_time = 600  # seconds
last_move_time = time.time()

def safe_send(sock, message):
    """Helper function to send a message and handle errors."""
    try:
        sock.send(message.encode())
    except Exception:
        pass

def format_time(seconds):
    """Return time in MM:SS format."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02}:{secs:02}"

def timer_thread():
    global white_time, black_time, last_move_time, current_turn
    while True:
        time.sleep(1)
        with lock:
            # Only count down if both players are connected
            if players['white'] is None or players['black'] is None:
                last_move_time = time.time()
                continue
            now = time.time()
            elapsed = now - last_move_time
            if current_turn == chess.WHITE:
                white_time -= elapsed
                if white_time <= 0:
                    for p in [players['white'], players['black']] + spectators:
                        if p:
                            safe_send(p, "Game over: Black wins by timeout")
                    print("Game over: Black wins by timeout")
                    os._exit(0)
            else:
                black_time -= elapsed
                if black_time <= 0:
                    for p in [players['white'], players['black']] + spectators:
                        if p:
                            safe_send(p, "Game over: White wins by timeout")
                    print("Game over: White wins by timeout")
                    os._exit(0)
            last_move_time = now
            timer_msg = f"timer:{format_time(white_time)},{format_time(black_time)}"
            for p in [players['white'], players['black']] + spectators:
                if p:
                    safe_send(p, timer_msg)

def handle_client(client_socket):
    global current_turn, last_move_time
    # Ask for user's name
    safe_send(client_socket, "Enter your name:")
    name = client_socket.recv(1024).decode().strip()

    # Ask for role
    safe_send(client_socket, "Are you a player or spectator? (p/s)")
    role = client_socket.recv(1024).decode().strip().lower()

    if role == 'p':
        with lock:
            if players['white'] is None:
                players['white'] = client_socket
                safe_send(client_socket, "You are white")
                print(f"{name} joined as White")
            elif players['black'] is None:
                players['black'] = client_socket
                safe_send(client_socket, "You are black")
                print(f"{name} joined as Black")
            else:
                safe_send(client_socket, "Game is full")
                client_socket.close()
                return
    elif role == 's':
        with lock:
            spectators.append(client_socket)
        safe_send(client_socket, "You are a spectator")
        print(f"{name} joined as Spectator")
    else:
        safe_send(client_socket, "Invalid choice")
        client_socket.close()
        return

    # Send initial board state
    with lock:
        safe_send(client_socket, board.fen())

    # Handle client communication
    while True:
        try:
            message = client_socket.recv(1024).decode().strip()
            if not message:
                break

            # Handle resign
            if message == "resign":
                if role == 'p':
                    if players['white'] == client_socket:
                        winner = "Black wins by resignation"
                    else:
                        winner = "White wins by resignation"
                    for p in [players['white'], players['black']] + spectators:
                        if p:
                            safe_send(p, f"Game over: {winner}")
                    print(f"Game over: {winner}")
                    os._exit(0)
            # Handle draw offer
            elif message == "offer_draw":
                opponent = players['black'] if players['white'] == client_socket else players['white']
                if opponent:
                    safe_send(opponent, "draw_offer")
            elif message == "accept_draw":
                for p in [players['white'], players['black']] + spectators:
                    if p:
                        safe_send(p, "Game over: Draw by agreement")
                print("Game over: Draw by agreement")
                os._exit(0)
            elif message == "decline_draw":
                opponent = players['black'] if players['white'] == client_socket else players['white']
                if opponent:
                    safe_send(opponent, "draw_declined")
            else:
                # Process moves for players on turn
                if role == 'p' and ((players['white'] == client_socket and current_turn == chess.WHITE) or
                                    (players['black'] == client_socket and current_turn == chess.BLACK)):
                    try:
                        move = chess.Move.from_uci(message)
                        with lock:
                            if move in board.legal_moves:
                                board.push(move)
                                current_turn = not current_turn
                                last_move_time = time.time()  # Reset timer on move
                                fen = board.fen()
                                for p in [players['white'], players['black']] + spectators:
                                    if p:
                                        safe_send(p, fen)
                                if board.is_game_over():
                                    result = board.result()
                                    if result == "1-0":
                                        winner = "White wins"
                                    elif result == "0-1":
                                        winner = "Black wins"
                                    else:
                                        winner = "Draw"
                                    for p in [players['white'], players['black']] + spectators:
                                        if p:
                                            safe_send(p, f"Game over: {winner}")
                                    print(f"Game over: {winner}")
                                    os._exit(0)
                            else:
                                safe_send(client_socket, "Invalid move")
                    except ValueError:
                        safe_send(client_socket, "Invalid move")
        except Exception:
            break

    with lock:
        if role == 'p':
            if players['white'] == client_socket:
                players['white'] = None
            elif players['black'] == client_socket:
                players['black'] = None
        elif role == 's' and client_socket in spectators:
            spectators.remove(client_socket)
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('26.235.154.238', 5555))  # Use your desired IP/port
    server.listen(5)
    print("Server started on port 5555")

    # Start the timer thread
    threading.Thread(target=timer_thread, daemon=True).start()

    try:
        while True:
            client, addr = server.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
