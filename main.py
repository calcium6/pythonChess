import os, sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import PIL

class Board(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(background="#302e2b")
        self.create_menu()
        self.root.geometry('720x720+600+100')
        self.root.resizable(False, False)
        self.root.title("Šachy")
        self.root.iconbitmap(resource('appIcon.ico'))

        tk.Frame.__init__(self, self.root)
        self.pack(padx = 30, pady = 30)

        self.blank = None
        self.move_path = []

        self.white_king_pos = None
        self.black_king_pos = None
        self.king_moved = False

        self.lock_game = False

        self.white_castled, self.black_castled = False, False
        self.white_rook_move = {(0,0): True, (7,0): True}
        self.black_rook_move = {(0,7): True, (7,7): True}

        self.first_pos = None
        self.second_pos = None
        self.first_button = None
        self.second_button = None
        self.button_clicks = 0

        self.possible_moves = []
        self.squares = {}
        self.pieces_white = {}
        self.pieces_black = {}
        self.piece_to_str = {}
        self.positions_white = []
        self.positions_black = []

        self.board_states = {}
        self.halfmoves = 0
        self.piece_taken = False
        self.en_passant_pawn = (False, None, None)
        self.en_passant_made = False
        self.moves = 0
        self.set_board()
        self.load_pieces()
    
    def load_game_from_fen(self, load_entry: tk.Entry):
        try:
            fen = (load_entry.get()).split(" ")
            self.start(fen[0], fen[1], fen[2], fen[3], fen[4], fen[5])
        except:
            messagebox.showerror("Chyba", "Nesprávný formát FEN")
        self.load_window.destroy()

    def load_menu(self):
        self.load_window = tk.Toplevel(self.root)
        self.load_window.geometry("500x200+710+380")
        self.load_window.resizable(False, False)
        self.load_window.title("Nahrání pozice")
        self.load_window.iconbitmap(resource('appIcon.ico'))

        label = tk.Label(self.load_window, text="Zadej řetězec notace FEN:", font=('Helvetica 12'))
        label.pack(pady=20)
        load_entry = tk.Entry(self.load_window, width=76)
        load_entry.pack()
        
        self.load_button = tk.Button(self.load_window,text= "Nahrát", font=('Helvetica 12'), command= lambda:self.load_game_from_fen(load_entry))
        self.cancel_button =tk.Button(self.load_window, text="Zrušit", font=('Helvetica 12'), command= self.load_window.destroy)
        self.load_button.pack(pady=10,side=tk.TOP)
        self.cancel_button.pack(pady=10, side=tk.TOP)

    def popup_current_fen(self):
        show_window = tk.Toplevel(self.root)
        show_window.iconbitmap(resource('appIcon.ico'))
        show_window.resizable(False, False)
        ent = tk.Entry(show_window, font=('Helvetica 12'), width=76, state='readonly', justify='center')
        var = tk.StringVar()
        var.set(self.get_fen_string())
        ent.config(textvariable=var)
        but = tk.Button(show_window, font=('Helvetica 12'), text="Konec", command=show_window.destroy)
        ent.pack(padx=15, pady=15, side=tk.TOP)
        but.pack(padx=15, pady=10, side=tk.TOP)

    def about_menu(self):
        about_window = tk.Toplevel(self.root)
        about_window.iconbitmap(resource('appIcon.ico'))
        about_window.resizable(False, False)
        label = tk.Label(about_window, text="Šachy 2024 Edice\n© Jiří Vaňůra léta páně dva tisíce dvacet čtyři", font=('Helvetica 12'), justify="center")
        label.pack(padx=200, pady=200)

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.options_menu = tk.Menu(self.menubar, tearoff=False)
        self.options_menu.add_command(label="Restart hry", command=self.start)
        self.options_menu.add_command(label="Načíst pozici", command=self.load_menu)
        self.options_menu.add_command(label="Vypsat pozici", command=self.popup_current_fen)
        #self.options_menu.add_command(label="O programu", command=self.about_menu)
        self.options_menu.add_command(label='Konec', command=self.root.destroy)
        self.menubar.add_cascade(label="Možnosti", menu=self.options_menu)

    def set_board(self):
        for row in range(8):
            for col in range(8):
                pos = (col, 7-row)
                if (col+row)%2 == 0:
                    square = tk.Button(self, bg="#eeeed2", activebackground="#baca44", borderwidth=0, command = lambda arg = pos: self.select(arg))
                else:
                    square = tk.Button(self, bg="#769656", activebackground="#baca44", borderwidth=0, command = lambda arg = pos: self.select(arg))
                square.grid(row=row, column=col)
                self.squares.setdefault(pos, square)

    def load_pieces(self):
        #path = os.path.join(os.path.dirname(__file__), 'whitePieces')
        path = resource('whitePieces')
        images = os.listdir(path)
        for imgPath in images:
            piece = Image.open(path + '\\' + imgPath)
            piece = piece.resize((80, 80))
            piece = ImageTk.PhotoImage(image = piece)
            pieceName = os.path.splitext(imgPath)[0]
            if pieceName != "blank":
                self.pieces_white.setdefault(pieceName, piece)
                self.piece_to_str.setdefault(piece, pieceName.capitalize())
        
        #path = os.path.join(os.path.dirname(__file__), 'blackPieces')
        path = resource('blackPieces')
        images = os.listdir(path)
        for imgPath in images:
            piece = Image.open(path + '\\' + imgPath)
            piece = piece.resize((80, 80))
            piece = ImageTk.PhotoImage(image = piece)
            pieceName = os.path.splitext(imgPath)[0]
            if pieceName != "blank":
                self.pieces_black.setdefault(pieceName, piece)
                self.piece_to_str.setdefault(piece, pieceName)
            else:
                self.blank = piece

        #path = os.path.join(os.path.dirname(__file__), 'movePath')
        path = resource('movePath')
        images = os.listdir(path)
        for imgPath in images:
            image_dot = Image.open(path + '\\' + imgPath)
            image_dot = image_dot.resize((80, 80))
            image_dot = ImageTk.PhotoImage(image = image_dot)
            self.move_path.append(image_dot)
        

    def set_image(self, pos: tuple[int,int], img: tk.PhotoImage) -> None:
        self.squares[pos].image = img
        self.squares[pos]["image"] = img
        return

    def place_pieces(self, position: str) -> None:
        rows = position.split("/")
        for row in range(8):
            y = 7 - row
            x = 0
            for p in rows[row]:
                if p.isdigit():
                    for i in range(int(p)):
                        self.set_image((x,y), self.blank)
                        x += 1
                else:
                    if p.isupper():
                        self.set_image((x,y), self.pieces_white[p.lower()])
                        if p == "K":
                            self.white_king_pos = (x,y)
                    else:
                        self.set_image((x,y), self.pieces_black[p])
                        if p == "k":
                            self.black_king_pos = (x,y)
                    x += 1
        return

    def set_turn(self, on_turn: str, halfmove: str, fullmove: str) -> None:
        self.moves = 2 * int(fullmove)
        self.halfmoves = int(halfmove)
        if on_turn == "b":
            self.moves += 1
        return

    def set_castling(self, castling: str) -> None:
        if castling == "-":
            return
        for c in castling:
            match c:
                case "K":
                    self.white_rook_move[(7,0)] = False
                case "Q":
                    self.white_rook_move[(0,0)] = False
                case "k":
                    self.black_rook_move[(0,7)] = False
                case "q":
                    self.black_rook_move[(7,7)] = False
        return
    
    def set_en_passant(self, en_passant: str) -> None:
        if en_passant != "-":
            self.en_passant_pawn = (True, (int(chr(ord(en_passant[0]) - 49)), int(en_passant[1])), self.moves)
        return
    
    def record_pieces(self):
        for x in range(8):
            for y in range(8):
                if self.squares[(x,y)].image != self.blank:
                    if self.squares[(x,y)].image in self.pieces_white.values():
                        self.positions_white.append((x,y))
                    else:
                        self.positions_black.append((x,y))

    def start(self, position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", on_turn = "w", castling = "KQkq", en_passant = "-", halfmove = "0", fullmove = "0") -> None:
        try:
            self.place_pieces(position)
            self.set_turn(on_turn, halfmove, fullmove)
            self.set_castling(castling)
            self.set_en_passant(en_passant)
            self.record_pieces()
        except:
            messagebox.showerror("Chyba", "Nesprávný formát FEN")
            self.error_popup()
        return
    
    def error_popup(self):
        pass #TODO

    def dokumentace_cervena(self, pos: tuple[int,int]) -> None:
        if ((pos[0] + pos[1]) % 2 == 1):
            self.squares[pos].config(bg = "#f33e42") #f33e42
            return
        self.squares[pos].config(bg = "#e73536") #e73536
        return

    def select(self, pos: tuple[int,int]) -> None:
        if self.lock_game:
            return
        if self.button_clicks % 2 == 0:
            if (self.squares[pos].image in self.pieces_white.values()) and self.moves % 2 == 0:
                self.possible_moves, _ = self.find_moves(self.moves % 2 == 0, pos, False)
                self.highlight_moves()
                self.first_pos = pos
                self.first_button = self.squares[pos]
                self.button_clicks += 1
                self.squares[pos].config(bg = "#baca44")
            if (self.squares[pos].image in self.pieces_black.values()) and self.moves % 2 == 1:
                self.possible_moves, _ = self.find_moves(self.moves % 2 == 0, pos, False)
                self.highlight_moves()
                self.first_pos = pos
                self.first_button = self.squares[pos]
                self.button_clicks += 1
                self.squares[pos].config(bg = "#baca44")
            return
        self.hide_moves()
        print(self.castling_pieces(self.moves % 2 == 0, self.first_pos, pos))
        if self.castling_pieces(self.moves % 2 == 0, self.first_pos, pos):
            if self.castle(self.moves % 2 == 0, self.first_pos, pos):
                self.halfmoves += 1
                self.moves += 1
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
            return
        if pos == self.first_pos: #Oba kliky na stejnou figurku
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
            return
        if (self.check_move_legality(self.moves % 2 == 0, self.first_pos, pos, True)):
            self.second_pos = pos
            self.second_button = self.squares[pos]
            first_image = self.first_button.image
            second_image = self.second_button.image
            if second_image in self.pieces_black.values() or second_image in self.pieces_white.values():
                self.piece_taken = True
            if first_image == self.pieces_white["p"] or first_image == self.pieces_black["p"]:
                self.piece_taken = True
            self.second_button.image = first_image
            self.second_button["image"] = first_image
            self.first_button.image = self.blank
            self.first_button["image"] = self.blank
            self.base_color(self.first_pos)
            self.base_color(pos)

            if self.check_current_turn(pos, self.moves % 2 == 0, first_image, second_image):
                return
            if self.king_moved:
                if self.moves % 2 == 0:
                    self.white_castled = True
                else:
                    self.black_castled = True
                self.king_moved = False
            self.button_clicks += 1
            self.moves += 1
            self.check_castling()
            current_fen = self.fen_board_placement()
            if self.en_passant_pawn[0] and self.moves > self.en_passant_pawn[2]:
                    self.en_passant_pawn = (False, None, None)
                    self.en_passant_made = False
                    self.halfmoves = 0
            if self.piece_taken:
                self.halfmoves = 0
                self.piece_taken = False
            else:
                self.halfmoves += 1
            if self.halfmoves == 100:
                self.draw_by_50_moves()
            if current_fen in self.board_states:
                self.board_states[current_fen] += 1
                if self.board_states[current_fen] == 3:
                    self.draw_by_repetition()
            else:
                self.board_states.setdefault(current_fen, 1)
            return
        else:
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
        return
    
    def end_game(self, color: bool) -> None:
        if color:
            text = "Konec hry, vyhrává černý hráč"
        else:
            text = "Konec hry, vyhrává bílý hráč"
        self.end_game_menu(text)
        return
    
    def draw_by_stalemate(self) -> None:
        self.end_game_menu("Remíza: Pat")
        return
    
    def draw_by_50_moves(self) -> None:
        self.end_game_menu("Remiza: Pravidlo 50 tahů")
        return
    
    def draw_by_repetition(self) -> None:
        self.end_game_menu("Remíza: Trojí opakování pozice")
        return
    
    def restart_game(self):
        self.start()
        self.end_window.destroy()
        self.lock_game = False
    
    def end_game_menu(self, label_text: str):
        self.lock_game = True
        self.end_window = tk.Toplevel(self.root)
        self.end_window.geometry("500x150+710+380")
        self.end_window.resizable(False, False)
        self.end_window.title("Konec hry")
        self.end_window.iconbitmap(resource('appIcon.ico'))

        end_game_message = tk.Label(self.end_window, text=label_text, font=('Helvetica 12 bold'))
        end_game_message.pack(pady=10)
        self.restart_button = tk.Button(self.end_window,text= "Hrát znovu", font=('Helvetica 12'), command= lambda:self.restart_game())
        self.cancel_button =tk.Button(self.end_window, text="Konec", font=('Helvetica 12'), command=lambda:self.root.destroy())
        self.restart_button.pack(pady=10,side=tk.TOP)
        self.cancel_button.pack(pady=5, side=tk.TOP)
    
    def fen_board_placement(self) -> list[str]:
        piece_placement = ""
        for i in range(7, -1, -1):
            blank_squares = 0
            for j in range(8):
                if self.squares[(j,i)].image != self.blank:
                    if blank_squares != 0:
                        piece_placement += str(blank_squares)
                        blank_squares = 0
                    piece_placement += self.piece_to_str[self.squares[(j,i)].image]
                else:
                    blank_squares += 1
            if i != 0:
                if blank_squares != 0:
                    piece_placement += str(blank_squares)
                piece_placement += "/"
        return piece_placement
    
    def fen(self) -> list[str]:
        piece_placement = self.fen_board_placement()
        castling = ""
        enpassant = "-"
        if self.moves % 2 == 0:
            turn = "w"
        else:
            turn = "b"
        if not self.white_castled:
            if not self.white_rook_move[(0,0)]:
                castling += "K"
            if not self.white_rook_move[(7,0)]:
                castling += "Q"
        if not self.black_castled:
            if not self.black_rook_move[(7,7)]:
                castling += "k"
            if not self.black_rook_move[(0,7)]:
                castling += "q"
        if castling == "":
            castling = "-"
        if self.en_passant_pawn[0]:
            enpassant = chr(self.en_passant_pawn[1][0] + 97) + str(self.en_passant_pawn[1][1])
        return [piece_placement, turn, castling, enpassant, str(self.halfmoves), str(self.moves//2)]
    
    def get_fen_string(self) -> str:
        return " ".join(self.fen())
    
    def castle(self, color: bool, first_pos: tuple[int,int], second_pos: tuple[int,int]) -> bool:
        if color:
            king = self.white_king_pos
            king_piece = self.pieces_white["k"]
            rook_piece = self.pieces_white["r"]
        else:
            king = self.black_king_pos
            king_piece = self.pieces_black["k"]
            rook_piece = self.pieces_black["r"]
        y = king[1]
        if second_pos[0] == 0:
            new_king_pos = (king[0] - 2, y)
            new_rook_pos = (king[0] - 1, y)
        else:
            new_king_pos = (king[0] + 2, y)
            new_rook_pos = (king[0] + 1, y)
        for x in range(min(first_pos[0], second_pos[0]) + 1, max(first_pos[0], second_pos[0])):
            if self.squares[(x, y)].image != self.blank:
                return False
        for x in range(min(new_king_pos[0], new_rook_pos[0]), max(new_king_pos[0], new_rook_pos[0]) + 1):
            check, _ = self.check_piece_threats((x,y), color)
            if check:
                return False
        self.set_image(first_pos, self.blank)
        self.set_image(second_pos, self.blank)
        self.set_image(new_king_pos, king_piece)
        self.set_image(new_rook_pos, rook_piece)
        self.white_castled = True
        if color:
            self.white_king_pos = new_king_pos
        else:
            self.black_king_pos = new_king_pos
        return True
    
    def castling_pieces(self, color: bool, first_pos: tuple[int,int], second_pos: tuple[int,int]) -> bool:
        if color: #TODO: dat do funkce
            if self.white_castled:
                return False
            king = self.pieces_white["k"]
            rookPos = [(0,0), (7,0)]
        else:
            if self.black_castled:
                return False
            king = self.pieces_black["k"]
            rookPos = [(0,7),(7,7)]
        if self.squares[first_pos].image == king:
            if second_pos in rookPos:
                if color:
                    if not self.white_rook_move[second_pos]: #TODO: dat do funkce
                        return True
                else:
                    if not self.black_rook_move[second_pos]:
                        return True
        if self.squares[second_pos].image == king:
            if first_pos in rookPos:
                if color:
                    if not self.white_rook_move[first_pos]:
                            return True
                    else:
                        if not self.black_rook_move[first_pos]:
                            return True
        return False
        
    def check_castling(self):
        if not self.white_castled:
            if False not in self.white_rook_move.values():
                self.white_castled = True
                return
            rookPos = [(0,0), (7,0)]
            for pos in rookPos:
                if self.squares[pos].image != self.pieces_white["r"]:
                    if not self.white_rook_move[pos]:
                        self.white_rook_move[pos] = True
        if not self.black_castled:
            if False not in self.black_rook_move.values():
                self.black_castled = True
                return
            rookPos = [(0,7), (7,7)]
            for pos in rookPos:
                if self.squares[pos].image != self.pieces_black["r"]:
                    if not self.black_rook_move[pos]:
                        self.black_rook_move[pos] = True
    
    def set_promotion_image(self, color: bool, piece: str) -> tk.PhotoImage:
        if color:
            return self.pieces_white[piece]
        else:
            return self.pieces_black[piece]
        
    def root_conf(self, e):
        self.promo.geometry('{}x{}+{}+{}'.format(self.promo.winfo_width(), self.promo.winfo_height(), e.x + 196, e.y + 340))

    def promote_pawn(self, pos: tuple[int, int], color: bool) -> None:
        self.lock_game = True
        def return_piece(piece, pos):
            self.squares[pos]["image"] = str(piece)
            self.squares[pos].image = piece
            self.promo.destroy()
            self.promo.quit()
            return
        
        self.root.bind('<Configure>', self.root_conf)
        self.promo = tk.Toplevel(self.root)
        self.promo.geometry("+%d+%d" % (self.root.winfo_x() + (0.275 * self.root.winfo_width()), self.root.winfo_y() + (0.5 * self.root.winfo_height())))
        self.promo.overrideredirect(True)
        self.promo.grab_set()
        self.promo.title("Pawn promotion")
        if color:
            promo_knight = tk.Button(self.promo, text="Knight", command=lambda: return_piece(self.pieces_white["n"], pos))
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(self.promo, text="Bishop", command=lambda: return_piece(self.pieces_white["b"], pos))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(self.promo, text="Rook", command=lambda: return_piece(self.pieces_white["r"], pos))
            promo_rook.grid(row=0, column=2)
            promo_queen = tk.Button(self.promo, text="Queen", command=lambda: return_piece(self.pieces_white["q"], pos))
            promo_queen.grid(row=0, column=3)
        elif not color:
            promo_knight = tk.Button(self.promo, text="Knight", command=lambda: return_piece(self.pieces_black["n"], pos))
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(self.promo, text="Bishop", command=lambda: return_piece(self.pieces_black["b"], pos))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(self.promo, text="Rook", command=lambda: return_piece(self.pieces_black["r"], pos))
            promo_rook.grid(row=0, column=2)
            promo_queen = tk.Button(self.promo, text="Queen", command=lambda: return_piece(self.pieces_black["q"], pos))
            promo_queen.grid(row=0, column=3)
        promo_knight["image"] = self.set_promotion_image(color, "n")
        promo_bishop["image"] = self.set_promotion_image(color, "b")
        promo_rook["image"] = self.set_promotion_image(color, "r")
        promo_queen["image"] = self.set_promotion_image(color, "q")
        self.promo.protocol("WM_DELETE_WINDOW", lambda: None)
        self.promo.mainloop()
        self.lock_game = False
        return
        
    def update_positions(self, color: bool, pos: tuple[int,int]):
        if color:
            self.positions_white.remove(self.first_pos)
            if pos in self.positions_black:
                self.positions_black.remove(pos)
            self.positions_white.append(pos)
        else:
            self.positions_black.remove(self.first_pos)
            if pos in self.positions_white:
                self.positions_white.remove(pos)
            self.positions_black.append(pos)
    
    def stalemate_check(self, color: bool):
        if color:
            positions = self.positions_white
        else:
            positions = self.positions_black
        for p in positions:
            _, stalemate = self.find_moves(color, p, True)
            if not stalemate:
                return
        self.draw_by_stalemate()
    
    def check_current_turn(self, pos: tuple[int, int], color: bool, first_image: tk.PhotoImage, second_image: tk.PhotoImage) -> bool:
        if color:
            king = self.white_king_pos
            king_opponent = self.black_king_pos
            pawn = self.pieces_white["p"]
        else:
            king = self.black_king_pos
            king_opponent = self.white_king_pos
            pawn = self.pieces_black["p"]
        check, _ = self.check_piece_threats(king, color)
        if check:
            self.piece_taken = False
            self.second_button.image = second_image
            self.second_button["image"] = second_image
            self.first_button.image = first_image
            self.first_button["image"] = first_image
            if self.king_moved:
                if color:
                    self.white_king_pos = self.first_pos
                else:
                    self.black_king_pos = self.first_pos
                king = self.first_pos
            if self.en_passant_made:
                if color:
                    self.set_image(self.en_passant_pawn[1], self.pieces_black["p"])
                else:
                    self.set_image(self.en_passant_pawn[1], self.pieces_white["p"])
                self.en_passant_made = False
            self.king_moved = False
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
            return True
        self.update_positions(color, pos)
        if self.squares[self.second_pos].image == pawn:
            if self.second_pos[1] == 0 or self.second_pos[1] == 7:
                self.promote_pawn(pos, color)
        opponent_check, check_pos = self.check_piece_threats(king_opponent, not color)
        if opponent_check:
            if not self.try_move_king(not color):
                for p in check_pos:
                    if p is None:
                        continue
                    if self.take_threat_piece(p, not color) or self.block_threat_piece(p, not color):
                        return
                self.end_game(not color)
        else:
            self.stalemate_check(not color)
    
    def try_for_check(self, first_pos: tuple[int, int], second_pos: tuple[int, int], color: bool, find_path: bool) -> bool:
        if find_path:
            if color:
                threat_pos = self.white_king_pos
            else:
                threat_pos = self.black_king_pos
        else:
            threat_pos = second_pos
        try:
            if self.check_move_legality(color, first_pos, second_pos, False):
                print("Pohoda")
                first_piece = self.squares[first_pos].image
                second_piece = self.squares[second_pos].image
                self.squares[first_pos].image = self.blank
                self.squares[second_pos].image = first_piece
                if self.piece_to_str[first_piece] not in "kK":
                    threatened, _ = self.check_piece_threats(threat_pos, color)
                else:
                    threatened, _ = self.check_piece_threats(second_pos, color)
                self.squares[first_pos].image = first_piece
                self.squares[second_pos].image = second_piece
                if threatened:
                    return False
                return True
        except KeyError:
            return False
        
    def block_rook_path(self, king: tuple[int, int], pos: tuple[int, int], color: bool) -> bool:
        if king[0] == pos[0]:
            min_y, max_y = min(king[1], pos[1]), max(king[1], pos[1])
            for i in range(min_y+1, max_y):
                if self.take_threat_piece((pos[0], i), color):
                    return True
        if king[1] == pos[1]:
            min_x, max_x = min(king[0], pos[0]), max(king[0], pos[0])
            for i in range(min_x, max_x):
                if self.take_threat_piece((i, pos[1]), color):
                    return True
        return False

    def block_bishop_path(self, king: tuple[int, int], pos: tuple[int, int], color: bool) -> bool:
        if (abs(pos[0] - king[0]) != abs(pos[1] - king[1])):
            return False
        y = pos[1]
        if king[0] > pos[0]: #   x ->
            if king[1] > pos[1]: #y ↑
                for x in range(pos[0] + 1, king[0]):
                    y += 1
                    if self.take_threat_piece((x, y), color):
                        return True
            if king[1] < pos[1]: #y ↓
                for x in range(pos[0] + 1, king[0]):
                    y -= 1
                    if self.take_threat_piece((x, y), color):
                        return True
        if king[0] < pos[0]: #x <-
            if king[1] > pos[1]: #y ↑
                for x in range(pos[0] - 1, king[0], -1):
                    y += 1
                    if self.take_threat_piece((x, y), color):
                        return True
            if king[0] < pos[0]: #y ↓
                for x in range(pos[0] - 1, king[0], -1):
                    y -= 1
                    if self.take_threat_piece((x, y), color):
                        return True
        return False
    
    def block_threat_piece(self, pos: tuple[int, int], color: bool) -> bool:
        if color:
            king = self.white_king_pos
            pieces = self.pieces_black
        else:
            king = self.black_king_pos
            pieces = self.pieces_white
        piece = self.squares[pos].image
        if piece == pieces["p"] or pieces["n"]:
            return False
        if piece == pieces["r"] or pieces["q"]:
            if self.block_rook_path(king, pos, color):
                return True
        if piece == pieces["r"] or pieces["q"]:
            if self.block_bishop_path(king, pos, color):
                return True
        return False
        
    def take_threat_piece(self, pos: tuple[int, int], color: bool) -> bool: #todo rename
        threatened, threat_pos = self.check_piece_threats(pos, not color)
        if threatened:
            for p in threat_pos:
                if p != None:
                    if self.try_for_check(p, pos, color, False):
                        return True
        return False
    
    def try_move_king(self, color: bool) -> bool:
        if color:
            king = self.white_king_pos
        else:
            king = self.black_king_pos
        x, y = king[0], king[1]
        moves = [(x, y+1), (x+1,y+1), (x+1,y), (x+1,y-1), (x,y-1), (x-1,y-1), (x-1,y), (x-1,y+1)]
        for move in moves:
            if self.try_for_check(king, move, color, False):
                #print(str(move[0]) + "," + str(move[1]) + " True")
                return True
            #print(str(move[0]) + "," + str(move[1]) + " False")
        return False
    
    def move_bishop(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        print("bishop check")
        if (abs(first_pos[0] - second_pos[0]) != abs(first_pos[1] - second_pos[1])): #Kontrola rozdílu v pozicích
            return False
        y = first_pos[1]
        if second_pos[0] > first_pos[0]: #   x ->
            if second_pos[1] > first_pos[1]: #y ↑
                for x in range(first_pos[0] + 1, second_pos[0]):
                    y += 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("1V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if second_pos[1] < first_pos[1]: #y ↓
                for x in range(first_pos[0] + 1, second_pos[0]):
                    y -= 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("2V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
        if second_pos[0] < first_pos[0]: #x <-
            if second_pos[1] > first_pos[1]: #y ↑
                for x in range(first_pos[0] - 1, second_pos[0], -1):
                    y += 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("3V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if second_pos[1] < first_pos[1]: #y ↓
                for x in range(first_pos[0] - 1, second_pos[0], -1):
                    y -= 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("4V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
        return True

    def move_king(self, opponent_color: bool, first_pos: tuple[int, int], second_pos: tuple[int, int], in_game: bool) -> bool:
        if abs(first_pos[0] - second_pos[0]) <= 1 and abs(first_pos[1] - second_pos[1]) <= 1:
            print(str(first_pos) + "to" + str(second_pos))
            if not self.king_nearby(second_pos, opponent_color):
                if in_game:
                    if self.moves % 2 == 0:
                        print("zmena bileho krale ve funkci")
                        self.white_king_pos = second_pos
                    else:
                        print("zmena cerneho krale v efunkci")
                        self.black_king_pos = second_pos
                    self.king_moved = True
                return True
        return False

    def move_knight(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        if abs(first_pos[1] - second_pos[1]) == 2 and abs(first_pos[0] - second_pos[0]) == 1:
            return True
        if abs(first_pos[1] - second_pos[1]) == 1 and abs(first_pos[0] - second_pos[0]) == 2:
            return True
        return False
    
    def move_pawn(self, first_pos: tuple[int, int], second_pos: tuple[int, int], in_game: bool) -> bool:
        selected_piece = self.squares[first_pos].image
        if first_pos[1] == 1: #První pohyb pro bílou
            if second_pos[1] - first_pos[1] == 2 and second_pos[0] == first_pos[0]:
                if self.squares[(second_pos[0], 2)].image == self.blank and self.squares[(second_pos[0], 3)].image == self.blank:
                    if in_game:
                        print("pawn 2 ................... white")
                        self.en_passant_pawn = (True, second_pos, self.moves + 1)
                    return True
                return False
        if first_pos[1] == 6: #První pohyb pro černou
            if second_pos[1] - first_pos[1] == -2 and second_pos[0] == first_pos[0]:
                if self.squares[(second_pos[0], 5)].image == self.blank and self.squares[(second_pos[0], 4)].image == self.blank:
                    if in_game:
                        print("pawn 2 ................... black")
                        self.en_passant_pawn = (True, second_pos, self.moves + 1)
                    return True
                return False
        if selected_piece in self.pieces_white.values():
            if second_pos[1] - first_pos[1] == 1:
                if second_pos[0] == first_pos[0]:
                    if self.squares[second_pos].image != self.blank:
                        return False
                    return True
                if abs(second_pos[0] - first_pos[0]) == 1:
                    if self.squares[second_pos].image == self.blank:
                        if self.en_passant_pawn[0]:
                            if self.moves == self.en_passant_pawn[2]:
                                print("enpassant.............................................w")
                                if (self.en_passant_pawn[1][1] + 1 == second_pos[1]):
                                    if self.en_passant_pawn[1][0] == second_pos[0]:
                                        self.en_passant_made = True
                                        if in_game:
                                            self.set_image(self.en_passant_pawn[1], self.blank)
                                        return True
                        return False
                    return True
        if selected_piece in self.pieces_black.values():
            if second_pos[1] - first_pos[1] == -1:
                if second_pos[0] == first_pos[0]:
                    if self.squares[second_pos].image != self.blank:
                        return False
                    return True
                if abs(second_pos[0] - first_pos[0]) == 1:
                    if self.squares[second_pos].image == self.blank:
                        if self.en_passant_pawn[0]:
                            if self.moves == self.en_passant_pawn[2]:
                                print("enpassant.............................................b")
                                if (self.en_passant_pawn[1][1] - 1 == second_pos[1]):
                                    if self.en_passant_pawn[1][0] == second_pos[0]:
                                        self.en_passant_made = True
                                        if in_game:
                                            self.set_image(self.en_passant_pawn[1], self.blank)
                                        return True
                        return False
                    return True

    def move_rook(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        if first_pos[1] == second_pos[1]:
            pos1, pos2 = min(first_pos[0], second_pos[0]), max(first_pos[0], second_pos[0])
            print("R - Horizontal move")
            for i in range(pos1+1, pos2):
                if self.squares[(i, first_pos[1])].image != self.blank:
                    print(str(first_pos[1]) + " , " + str(i))
                    print("V cestě je figurka")
                    return False
            return True
        if first_pos[0] == second_pos[0]:
            print("R - Vertical move")
            pos1, pos2 = min(first_pos[1], second_pos[1]), max(first_pos[1], second_pos[1])
            print(str(pos1) + " , " + str(pos2))
            for i in range(pos1+1, pos2):
                print(self.squares[(first_pos[0], i)].image)
                if self.squares[(first_pos[0], i)].image != self.blank:
                    print(str(i) + " , " + str(first_pos[0]))
                    print("V cestě je figurka")
                    return False
            return True
        print("Diagonal")
        return False
    
    def find_moves(self, color: bool, piece_pos: tuple[int, int], return_when_found: bool) -> tuple[list, bool]:
        moves = []
        for x in range(8):
            for y in range(8):
                if (x,y) != piece_pos:
                    if self.try_for_check(piece_pos, (x,y), color, True):
                        if return_when_found:
                            return [], False
                        moves.append((x,y))
        return moves, True

    def check_move_legality(self, color: bool, first_pos: tuple[int, int], second_pos: tuple[int, int], in_game: bool) -> bool:
        selected_piece = self.squares[first_pos].image
        destination = self.squares[second_pos].image
        if (color and destination in self.pieces_white.values()):
            return False
        elif ((not color) and destination in self.pieces_black.values()):
            return False
        match self.piece_to_str[selected_piece].lower():
            case "b":
                return self.move_bishop(first_pos, second_pos)
            case "k":
                return self.move_king(not color, first_pos, second_pos, in_game)
            case "n":
                return self.move_knight(first_pos, second_pos)
            case "p":
                return self.move_pawn(first_pos, second_pos, in_game)
            case "q":
                return (self.move_rook(first_pos, second_pos) or self.move_bishop(first_pos, second_pos))
            case "r":
                return self.move_rook(first_pos, second_pos)
            case _:
                return False
        
    def base_color(self, pos: tuple[int, int]):
        if ((pos[0] + pos[1]) % 2 == 1):
            self.squares[pos].config(bg = "#eeeed2")
            return
        self.squares[pos].config(bg = "#769656")
        return
    
    def highlight_moves(self):
        colors = ["#638046", "#cacbb3"]
        for pos in self.possible_moves:
            if self.squares[pos].image == self.blank:
                self.squares[pos]["image"] = self.move_path[((pos[0] + pos[1]) % 2)]
            else:
                self.squares[pos].config(bg = colors[((pos[0] + pos[1]) % 2)])
        return
    
    def hide_moves(self):
        for pos in self.possible_moves:
            if self.squares[pos].image == self.blank:
                self.squares[pos]["image"] = str(self.blank)
            else:
                self.base_color(pos)
        self.possible_moves.clear()
        return
    
    def king_nearby(self, king_pos: tuple[int, int], king_color: bool) -> bool:
        print("Barva nepritele" + str(king_color))
        if not king_color:
            opponent_king = self.pieces_black["k"]
        else:
            opponent_king = self.pieces_white["k"]
        x, y = king_pos[0], king_pos[1]
        moves = [(x, y+1), (x+1,y+1), (x+1,y), (x+1,y-1), (x,y-1), (x-1,y-1), (x-1,y), (x-1,y+1)]
        for move in moves:
            try:
                if self.squares[move].image == opponent_king:
                    print("kral na " + str(move))
                    return True
            except KeyError:
                pass
        return False
    
    def piece_found(self, king_color: bool, piece: tk.PhotoImage, check_black: list, check_white: list) -> bool:
        if king_color == False: #black king
            if piece in self.pieces_black.values():
                if piece != self.pieces_black["k"]:
                    return False
            if piece in check_black:
                return True
            if piece in self.pieces_white.values():
                return False
            
        if king_color: #white king
            if piece in self.pieces_white.values():
                if piece != self.pieces_white["k"]:
                    return False
            if piece in check_white:
                return True
            if piece in self.pieces_white.values():
                return False

    def check_bishop_queen(self, king_pos: tuple[int, int], king_color: bool) -> tuple[bool, tuple[int, int]]:
        x1, x2 = king_pos[0], king_pos[0]
        y11, y12, y21, y22 = king_pos[1], king_pos[1], king_pos[1], king_pos[1]
        for i in range(0, 8):
            x1 += 1
            y11 += 1
            y21 += 1
            x2 -= 1
            y12 -= 1
            y22 -= 1
            if x1 > 7 and x2 < 0:
                return False, None
            if x1 <= 7:
                if y11 <= 7:
                    if self.squares[(x1, y11)].image != self.blank:
                        if self.piece_found(king_color, self.squares[(x1, y11)].image, [self.pieces_white["b"], self.pieces_white["q"]], [self.pieces_black["b"], self.pieces_black["q"]]):
                            return True, (x1, y11)
                        y11 = 8
                if y12 >= 0:
                    if self.squares[(x1, y12)].image != self.blank:
                        if self.piece_found(king_color, self.squares[(x1, y12)].image, [self.pieces_white["b"], self.pieces_white["q"]], [self.pieces_black["b"], self.pieces_black["q"]]):
                            return True, (x1, y12)
                        y12 = -1
            if x2 >= 0:
                if y21 <= 7:
                    if self.squares[(x2, y21)].image != self.blank:
                        if self.piece_found(king_color, self.squares[(x2, y21)].image, [self.pieces_white["b"], self.pieces_white["q"]], [self.pieces_black["b"], self.pieces_black["q"]]):
                            return True, (x2, y21)
                        y21 = 8
                if y22 >= 0:
                    if self.squares[(x2, y22)].image != self.blank:
                        if self.piece_found(king_color, self.squares[(x2, y22)].image, [self.pieces_white["b"], self.pieces_white["q"]], [self.pieces_black["b"], self.pieces_black["q"]]):
                            return True, (x2, y22)
                        y22 = -1
        return False, None
    
    def check_rook_queen(self, king_pos: tuple[int, int], king_color: bool) -> tuple[bool, tuple[int, int]]:
        x1, x2 = king_pos[0], king_pos[0]
        y1, y2 = king_pos[1], king_pos[1]
        for i in range(0, 8):
            x1 += 1
            y1 += 1
            x2 -= 1
            y2 -= 1
            if x1 <= 7:
                if self.squares[(x1, king_pos[1])].image != self.blank:
                    if self.piece_found(king_color, self.squares[(x1, king_pos[1])].image, [self.pieces_white["q"], self.pieces_white["r"]], [self.pieces_black["q"], self.pieces_black["r"]]):
                        return True, (x1, king_pos[1])
                    x1 = 8
            if y1 <= 7:
                if self.squares[(king_pos[0], y1)].image != self.blank:
                    if self.piece_found(king_color, self.squares[(king_pos[0], y1)].image, [self.pieces_white["q"], self.pieces_white["r"]], [self.pieces_black["q"], self.pieces_black["r"]]):
                        return True, (king_pos[0], y1)
                    y1 = 8
            if x2 >= 0:
                if self.squares[(x2, king_pos[1])].image != self.blank:
                    if self.piece_found(king_color, self.squares[(x2, king_pos[1])].image, [self.pieces_white["q"], self.pieces_white["r"]], [self.pieces_black["q"], self.pieces_black["r"]]):
                        return True, (x2, king_pos[1])
                    x2 = -1
            if y2 >= 0:
                if self.squares[(king_pos[0], y2)].image != self.blank:
                    if self.piece_found(king_color, self.squares[(king_pos[0], y2)].image, [self.pieces_white["q"], self.pieces_white["r"]], [self.pieces_black["q"], self.pieces_black["r"]]):
                        return True, (king_pos[0], y2)
                    y2 = -1
        return False, None
    
    def check_knight(self, king_pos: tuple[int, int], king_color: bool) -> tuple[bool, tuple[int, int]]:
        x, y = king_pos[0], king_pos[1]
        if king_color:
            piece = self.pieces_black["n"]
        else:
            piece = self.pieces_white["n"]
        for i in (-2, 2):
            for j in (-1, 1):
                x1 = x+i
                y1 = y+j
                x2 = x+j
                y2 = y+i
                if not (x1 > 7) and not (x1 < 0):
                    if not (y1 > 7) and not (y1 < 0):
                        if self.squares.get((x1, y1)).image == piece:
                            return True, (x1, y1)
                if not (x2 > 7) and not (x2 < 0):
                    if not (y2 > 7) and not (y2 < 0):
                        if self.squares.get((x2, y2)).image == piece:
                            return True, (x2, y2)
        return False, None

    def check_pawn(self, king_pos: tuple[int, int], king_color: bool) -> tuple[bool, tuple[int, int]]:
        x, y = king_pos[0], king_pos[1]
        try:
            if king_color:
                if self.squares[(x - 1, y + 1)].image == self.pieces_black["p"]:
                    return True, (x-1, y+1)
                if self.squares[(x + 1, y + 1)].image == self.pieces_black["p"]:
                    return True, (x+1, y+1)
            else:
                if self.squares[(x + 1, y - 1)].image == self.pieces_white["p"]:
                    return True, (x+1, y-1)
                if self.squares[(x - 1, y - 1)].image == self.pieces_white["p"]:
                    return True, (x-1, y-1)
        except KeyError:
            pass
        return False, None
    
    def check_piece_threats(self, pos: tuple[int, int], color: bool) -> tuple[bool, list]: #king_color: True - white, False - black
        b_q, pos_bq = self.check_bishop_queen(pos, color)
        r_q, pos_rq = self.check_rook_queen(pos, color)
        n, pos_n = self.check_knight(pos, color)
        p, pos_p = self.check_pawn(pos, color)
        print("Check: " + str(b_q) + ", " + str(r_q) + ", " + str(n) + ", " + str(p))
        return (b_q or r_q or n or p), [pos_bq, pos_rq, pos_n, pos_p]
    
def resource(relative_path):
    relative_path = "assets/" + relative_path.replace("/", os.sep)
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

board = Board()
#board.start("1R6/k1nK4/1p6/1P6/8/8/8/8", "w")
#board.start("k7/7Q/8/8/8/8/8/K7")
board.start()
board.root.mainloop()
