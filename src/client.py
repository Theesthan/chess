import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import chess
import chess.engine
import queue
from PIL import Image, ImageTk  # Pillow for image resizing
import time

class ChessGUI:
    def __init__(self, root, server_ip, username):
        self.root = root
        self.username = username
        self.root.title(f"Multiplayer Chess - {username}")
        self.board = chess.Board()
        self.selected_square = None
        self.is_player = None  # True for player, False for spectator
        self.color = None     # 'white' or 'black' for players; spectators have no color
        self.message_queue = queue.Queue()
        self.flip_board = False  # For player's perspective (only if playing)
        self.piece_images = {}
        self.blank_image = None
        self.engine = None    # For evaluation in spectator mode
        self.col_offset = 0   # 0 for players; 1 for spectators (board shifted right)

        # Load images (common to all roles)
        self.load_images()

        # Connect to server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((server_ip, 5555))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            root.quit()
            return

        # Protocol: Server asks for name, then for role.
        prompt = self.socket.recv(1024).decode().strip()  # Expected: "Enter your name:"
        if prompt != "Enter your name:":
            messagebox.showerror("Protocol Error", "Did not receive name prompt from server")
            self.root.quit()
            return
        self.socket.send(self.username.encode())

        # Consume the role prompt from the server (to avoid asking twice)
        role_prompt = self.socket.recv(1024).decode().strip()  # Expected: "Are you a player or spectator? (p/s)"
        
        # Ask for role via dialog
        role = messagebox.askquestion("Role", "Do you want to be a player? (yes for player, no for spectator)")
        if role == 'yes':
            self.socket.send('p'.encode())
            response = self.socket.recv(1024).decode().strip()
            if response == "You are white":
                self.is_player = True
                self.color = 'white'
            elif response == "You are black":
                self.is_player = True
                self.color = 'black'
                self.flip_board = True  # Flip board for black's POV
            else:
                messagebox.showinfo("Info", response)
                self.root.quit()
                return
            self.col_offset = 0  # For players, board starts at col 0
        else:
            self.socket.send('s'.encode())
            response = self.socket.recv(1024).decode().strip()
            messagebox.showinfo("Info", response)
            self.is_player = False
            self.col_offset = 1  # Spectators: board shifted right to make room for eval bar
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci("C:/Users/thees/Pictures/Eko/Eko/eko/CN package/stockfish/stockfish-windows-x86-64-avx2.exe")
            except Exception as e:
                messagebox.showerror("Engine Error", f"Could not start Stockfish engine: {e}")

        # If spectator, create an evaluation canvas on the left side.
        if not self.is_player:
            self.eval_canvas = tk.Canvas(self.root, width=50, height=400, bg="lightgray")
            self.eval_canvas.grid(row=0, column=0, rowspan=8, padx=5, pady=5)
            self.root.after(1000, self.update_evaluation_bar)

        # Create board with grid offset (players: col0, spectators: col1)
        self.create_board(col_offset=self.col_offset)

        # Timer label and control buttons below the board.
        timer_col = self.col_offset
        timer_colspan = 8
        self.timer_label = tk.Label(self.root, text="White: 10:00   Black: 10:00", font=("Helvetica", 14))
        self.timer_label.grid(row=8, column=timer_col, columnspan=timer_colspan, pady=5)
        self.resign_button = tk.Button(self.root, text="Resign", command=self.resign)
        self.resign_button.grid(row=9, column=timer_col, columnspan=timer_colspan//2, sticky="nsew", padx=5, pady=5)
        self.draw_button = tk.Button(self.root, text="Offer Draw", command=self.offer_draw)
        self.draw_button.grid(row=9, column=timer_col + timer_colspan//2, columnspan=timer_colspan//2, sticky="nsew", padx=5, pady=5)

        # Receive initial board state from server.
        initial_fen = self.socket.recv(1024).decode().strip()
        self.update_board(initial_fen)

        # Start network thread.
        self.running = True
        self.network_thread = threading.Thread(target=self.network_loop, daemon=True)
        self.network_thread.start()

        self.root.after(100, self.check_for_updates)

    def load_images(self):
        """Load and scale piece images using Pillow."""
        size = (50, 50)
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        base_path = r"C:\Users\thees\Pictures\Eko\Eko\eko\CN package\chesspng"
        for piece in pieces:
            prefix = "w" if piece.isupper() else "b"
            file_path = f"{base_path}\\{prefix}{piece.upper()}.png"
            try:
                img = Image.open(file_path)
                img = img.resize(size, Image.LANCZOS)
                self.piece_images[piece] = ImageTk.PhotoImage(img)
            except Exception as e:
                messagebox.showerror("Image Error", f"Error loading {file_path}:\n{e}")
                self.root.quit()
        self.blank_image = tk.PhotoImage(width=size[0], height=size[1])

    def get_square(self, grid_row, grid_col):
        """
        Map grid coordinates (row, col) to a chess square index.
        For players: white's view (row0=rank8) or black's view (if flip_board is True).
        Spectators always see white's orientation.
        """
        if self.is_player:
            if not self.flip_board:
                return chess.square(grid_col, 7 - grid_row)
            else:
                return chess.square(7 - grid_col, grid_row)
        else:
            return chess.square(grid_col, 7 - grid_row)

    def create_board(self, col_offset=0):
        """Create an 8x8 grid of buttons. col_offset shifts board to the right if needed."""
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        colors = ['white', 'gray']
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                button = tk.Button(self.root, bg=color, relief="ridge", borderwidth=1,
                                   command=lambda r=row, c=col: self.square_clicked(self.get_square(r, c)))
                button.grid(row=row, column=col + col_offset)
                self.buttons[row][col] = button
        self.update_board(self.board.fen())

    def square_clicked(self, square):
        """Handle a click on a square; send move if legal (players only)."""
        if not self.is_player or (self.color == 'white' and self.board.turn != chess.WHITE) or \
           (self.color == 'black' and self.board.turn != chess.BLACK):
            return
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == (self.color == 'white'):
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                try:
                    self.socket.send(move.uci().encode())
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send move: {e}")
            self.selected_square = None

    def update_board(self, fen):
        """Update board state and refresh button images."""
        self.board.set_fen(fen)
        for row in range(8):
            for col in range(8):
                square = self.get_square(row, col)
                piece = self.board.piece_at(square)
                image = self.piece_images.get(piece.symbol(), self.blank_image) if piece else self.blank_image
                self.buttons[row][col].config(image=image, text="")
                self.buttons[row][col].image = image

    def resign(self):
        """Send resign command to the server."""
        if self.is_player:
            try:
                self.socket.send("resign".encode())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send resign: {e}")

    def offer_draw(self):
        """Send draw offer to the server."""
        if self.is_player:
            try:
                self.socket.send("offer_draw".encode())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send draw offer: {e}")

    def update_evaluation_bar(self):
        """For spectators: use Stockfish to evaluate the board and update the evaluation bar."""
        if not self.is_player and self.engine:
            try:
                info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
                score_obj = info["score"].white()
                if score_obj.is_mate():
                    score = 10000 if score_obj.mate() > 0 else -10000
                else:
                    score = score_obj.score()
            except Exception:
                score = 0
            max_val = 500
            height = int(self.eval_canvas['height'])
            center = height // 2
            self.eval_canvas.delete("all")
            self.eval_canvas.create_rectangle(0, 0, 50, height, fill="lightgray", outline="")
            if score > max_val:
                score = max_val
            if score < -max_val:
                score = -max_val
            if score >= 0:
                fill_height = int((score / max_val) * (height / 2))
                self.eval_canvas.create_rectangle(0, center - fill_height, 50, center, fill="green", outline="")
            else:
                fill_height = int((abs(score) / max_val) * (height / 2))
                self.eval_canvas.create_rectangle(0, center, 50, center + fill_height, fill="red", outline="")
            eval_text = f"{score/100:.2f}"
            self.eval_canvas.create_text(25, center, text=eval_text, fill="black", font=("Helvetica", 12))
        self.root.after(1000, self.update_evaluation_bar)

    def network_loop(self):
        while self.running:
            try:
                message = self.socket.recv(1024).decode().strip()
                if not message:
                    self.message_queue.put(('msg', "Connection lost"))
                    break
                if message.startswith("timer:"):
                    self.message_queue.put(('timer', message))
                elif message == "draw_offer":
                    self.message_queue.put(('draw_offer', message))
                elif message.startswith("Game over:"):
                    self.message_queue.put(('gameover', message))
                elif ' ' in message and '/' in message:  # Rough FEN check
                    self.message_queue.put(('fen', message))
                else:
                    self.message_queue.put(('msg', message))
            except Exception:
                self.message_queue.put(('msg', "Connection lost"))
                break

    def check_for_updates(self):
        while not self.message_queue.empty():
            msg_type, message = self.message_queue.get()
            if msg_type == 'fen':
                self.update_board(message)
            elif msg_type == 'timer':
                try:
                    _, times = message.split(":", 1)
                    white_time, black_time = times.split(",")
                    self.timer_label.config(text=f"White: {white_time}   Black: {black_time}")
                except Exception:
                    pass
            elif msg_type == 'draw_offer':
                answer = messagebox.askyesno("Draw Offer", "Your opponent offers a draw. Accept?")
                if answer:
                    try:
                        self.socket.send("accept_draw".encode())
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to send accept draw: {e}")
                else:
                    try:
                        self.socket.send("decline_draw".encode())
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to send decline draw: {e}")
            elif msg_type == 'gameover':
                result = message.split(":", 1)[1].strip()
                messagebox.showinfo("Game Over", f"Game over: {result}")
                self.root.after(5000, self.on_closing)
            elif msg_type == 'msg':
                messagebox.showinfo("Message", message)
        self.root.after(100, self.check_for_updates)

    def on_closing(self):
        self.running = False
        try:
            self.socket.close()
        except Exception:
            pass
        if self.engine:
            self.engine.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window during dialogs
    username = simpledialog.askstring("Name", "Enter your name:")
    if not username:
        messagebox.showerror("Error", "Username is required")
        root.quit()
    else:
        server_ip = simpledialog.askstring("Server IP", "Enter server IP:")
        if not server_ip:
            messagebox.showerror("Error", "Server IP is required")
            root.quit()
        else:
            root.deiconify()
            gui = ChessGUI(root, server_ip, username)
            root.protocol("WM_DELETE_WINDOW", gui.on_closing)
            root.mainloop()
