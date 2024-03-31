import os
import tkinter as tk
from PIL import Image, ImageTk
import PIL

class Board(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(background="#302e2b")
        self.root.geometry('720x720+600+100')
        self.root.title("Chess")
        self.root.iconbitmap("")

        tk.Frame.__init__(self, self.root)
        self.pack(padx = 30, pady = 30)

        self.white = []
        self.black = []
        self.blank = None
        self.move_path = []

        self.white_king_pos = (4,0)
        self.black_king_pos = (4,7)
        self.king_moved = False
        self.promoting = False
        self.white_castled, self.black_castled = False, False
        self.white_rook_move = {(0,0): False, (0,7): False}
        self.black_rook_move = {(7,0): False, (7,7): False}

        self.first_pos = None
        self.second_pos = None
        self.first_button = None
        self.second_button = None
        self.button_clicks = 0

        self.possible_moves = []
        self.squares = {}
        self.pieces_white = {}
        self.pieces_black = {}
        self.turns = 0
        self.set_board()

    def set_board(self):
        for row in range(8):
            for col in range(8):
                if (col+row)%2 == 0:
                    square = tk.Button(self, bg="#eeeed2", activebackground="#baca44", borderwidth=0, text = str(col) + str(7-row))
                else:
                    square = tk.Button(self, bg="#769656", activebackground="#baca44", borderwidth=0, text = str(col) + str(7-row))
                square.grid(row=row, column=col)
                pos = (col, 7-row)
                self.squares.setdefault(pos, square)
                self.squares[pos].config(command = lambda arg = pos: self.select(arg))

    def load_pieces(self):
        path = os.path.join(os.path.dirname(__file__), 'whitePieces')
        images = os.listdir(path)
        for imgPath in images:
            piece = Image.open(path + '\\' + imgPath)
            piece = piece.resize((80, 80))
            piece = ImageTk.PhotoImage(image = piece)
            self.pieces_white.setdefault(os.path.splitext(imgPath)[0], piece)
        
        path = os.path.join(os.path.dirname(__file__), 'blackPieces')
        images = os.listdir(path)
        for imgPath in images:
            piece = Image.open(path + '\\' + imgPath)
            piece = piece.resize((80, 80))
            piece = ImageTk.PhotoImage(image = piece)
            self.pieces_black.setdefault(os.path.splitext(imgPath)[0], piece)

        path = os.path.join(os.path.dirname(__file__), 'movePath')
        images = os.listdir(path)
        for imgPath in images:
            image_dot = Image.open(path + '\\' + imgPath)
            image_dot = image_dot.resize((80, 80))
            image_dot = ImageTk.PhotoImage(image = image_dot)
            self.move_path.append(image_dot)

    def place_pieces(self):
        start_position = {(0,0):"r", (1,0):"n", (2,0):"b", (3,0):"q", (4,0):"k", (5,0):"b", (6,0):"n", (7,0):"r"}
        for square in start_position:

            self.squares[(square[0], square[1]+7)].image = self.pieces_black[start_position[square]]
            self.squares[(square[0], square[1]+7)]["image"] = self.pieces_black[start_position[square]]
            
            self.squares[square].image = self.pieces_white[start_position[square]]
            self.squares[square]["image"] = self.pieces_white[start_position[square]]
        
        for i in range(0, 8):
            self.squares[(i,6)].image = self.pieces_black["p"]
            self.squares[(i,6)]["image"] = self.pieces_black["p"]
            self.squares[(i,1)].image = self.pieces_white["p"]
            self.squares[(i,1)]["image"] = self.pieces_white["p"]
            for j in range(2, 6):
                self.squares[(i,j)].image = self.pieces_black["blank"]
                self.squares[(i,j)]["image"] = self.pieces_black["blank"]
        
        for key in self.pieces_white:
            if key == "blank":
                self.blank = self.pieces_white[key]
                continue
            self.white.append(self.pieces_white[key])

        for key in self.pieces_black:
            if key == "blank":
                self.blank = self.pieces_black[key]
                continue
            self.black.append(self.pieces_black[key])

    def start(self):
        self.load_pieces()
        self.place_pieces()

    def select(self, pos: tuple):
        if self.promoting:
            return
        if self.button_clicks % 2 == 0:
            self.possible_moves = self.find_moves(self.turns % 2 == 0, pos)
            self.highlight_moves()
            print("turns: " + str(self.turns))
            if (self.squares[pos].image in self.white) and self.turns % 2 == 0:
                self.first_pos = pos
                self.first_button = self.squares[pos]
                self.button_clicks += 1
                self.squares[pos].config(bg = "#baca44")
            if (self.squares[pos].image in self.black) and self.turns % 2 == 1:
                self.first_pos = pos
                self.first_button = self.squares[pos]
                self.button_clicks += 1
                self.squares[pos].config(bg = "#baca44")
            return
        self.hide_moves()
        if self.castling_pieces(self.turns % 2 == 0, self.first_pos, pos):
            self.castle(self.turns % 2 == 0, self.first_button, pos)
            pass #TODO: if castling true -> set castling pieces
        if pos == self.first_pos: #Oba kliky na stejnou figurku
            print("Stejná figurka")
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
            return
        if (self.check_move_legality(self.first_pos, pos)):
            #print("Pohyb z " + str(self.first_pos) + " na " + str(pos)) 
            self.second_pos = pos
            self.second_button = self.squares[pos]
            first_image = self.first_button.image
            second_image = self.second_button.image
            self.second_button.image = first_image
            self.second_button["image"] = str(first_image)
            self.first_button.image = self.blank
            self.first_button["image"] = str(self.blank)
            self.base_color(self.first_pos)
            self.base_color(pos)

            if self.check_current_turn(pos, self.turns % 2 == 0, first_image, second_image):
                return
            if self.king_moved:
                if self.turns % 2 == 0:
                    self.white_castled = True
                else:
                    self.black_castled = True
                self.king_moved = False
            self.button_clicks += 1
            self.turns += 1
            self.check_castling()
            return
            
        else:
            print("Zadny pohyb :((")
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
        return
    
    def end_game(self, color: bool) -> None:
        print("Konec hry: " + str(color))
        #todo
        return
    
    def castle(self, color, first_pos, second_pos):
        pass
    
    def castling_pieces(self, color: bool, first_pos: tuple[int,int], second_pos: tuple[int,int]) -> bool:
        if color: #TODO: dat do funkce
            if self.white_castled:
                return False
            king = self.pieces_white["k"]
            rook = self.pieces_white["r"]
            rookPos = [(0,0), (7,0)]
        else:
            if self.black_castled:
                return False
            king = self.pieces_black["k"]
            rook = self.pieces_black["r"]
            rookPos = [(0,7),(7,7)]
        if self.squares[first_pos].image == king:
            if second_pos in rookPos:
                if color:
                    if not self.white_rook_move[second_pos]: #TODO: dat do funkce
                        self.white_rook_move[second_pos] = True
                        return True
                else:
                    if not self.black_rook_move[second_pos]:
                        self.black_rook_move[second_pos] = True
                        return True
        if self.squares[second_pos].image == king:
            if first_pos in rookPos:
                if color:
                    if not self.white_rook_move[first_pos]:
                            self.white_rook_move[first_pos] = True
                            return True
                    else:
                        if not self.black_rook_move[first_pos]:
                            self.black_rook_move[first_pos] = True
                            return True
        return False
        
    def check_castling(self):
        if not self.white_castled:
            if False not in self.white_rook_move.values():
                self.white_castled = True
                return
            rookPos = [(0,0), (0,7)]
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
        self.promoting = True
        def return_piece(piece, pos):
            self.squares[pos]["image"] = str(piece)
            self.squares[pos].image = piece
            self.promo.destroy()
            self.promo.quit()
            return
        
        self.root.bind('<Configure>', self.root_conf)
        self.promo = tk.Toplevel(self.root)
        self.promo.geometry("+%d+%d" % (self.root.winfo_x() + 196, self.root.winfo_y() + 340)) # TODO: fix values
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
        self.promoting = False
        return
        
    
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
            self.second_button.image = second_image
            self.second_button["image"] = str(second_image)
            self.first_button.image = first_image
            self.first_button["image"] = str(first_image)
            if self.king_moved:
                print("Zmena krale zpatky")
                if color:
                    self.white_king_pos = self.first_pos
                else:
                    self.black_king_pos = self.first_pos
                king = self.first_pos
            self.king_moved = False
            print("Zadny pohyb :(")
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
            return True
        if self.squares[self.second_pos].image == pawn:
            print("pawn moved")
            print(str(self.second_pos[1] == 0))
            print(str(self.second_pos[1] == 7))
            if self.second_pos[1] == 0 or self.second_pos[1] == 7:
                print("promote pawn")
                self.promote_pawn(pos, color)
        print("hovno")
        opponent_check, check_pos = self.check_piece_threats(king_opponent, not color)
        print("opponent check: " + str(opponent_check))
        if opponent_check:
            if not self.try_move_king(not color):
                for p in check_pos:
                    if p is None:
                        continue
                    if self.take_threat_piece(p, not color) or self.block_threat_piece(p, not color):
                        break
                self.end_game(not color)
    
    def try_for_check(self, first_pos: tuple[int, int], second_pos: tuple[int, int], color: bool, find_path: bool) -> bool:
        if find_path:
            if color:
                threat_pos = self.white_king_pos
            else:
                threat_pos = self.black_king_pos
        else:
            threat_pos = second_pos
        try:
            if self.check_move_legality(first_pos, second_pos):
                first_piece = self.squares[first_pos].image
                second_piece = self.squares[second_pos].image
                self.squares[first_pos].image = self.blank
                self.squares[second_pos].image = first_piece
                threatened, _ = self.check_piece_threats(threat_pos, color)
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
                return True
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

    def move_king(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        if abs(first_pos[0] - second_pos[0]) <= 1 and abs(first_pos[1] - second_pos[1]) <= 1:
            if not self.king_nearby(second_pos, (self.turns % 2 == 0)):
                if self.turns % 2 == 0:
                    self.white_king_pos = second_pos
                else:
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
    
    def move_pawn(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        #selected_piece = self.first_button.image
        selected_piece = self.squares[first_pos].image
        if first_pos[1] == 1: #První pohyb pro bílou
            if second_pos[1] - first_pos[1] == 2 and second_pos[0] == first_pos[0]:
                if self.squares[(second_pos[0], 2)].image != self.blank and self.squares[(second_pos[0], 3)].image != self.blank:
                    return False
                return True
        if first_pos[1] == 6: #První pohyb pro černou
            if second_pos[1] - first_pos[1] == -2 and second_pos[0] == first_pos[0]:
                if self.squares[(second_pos[0], 5)].image != self.blank and self.squares[(second_pos[0], 4)].image != self.blank:
                    return False
                return True
        if selected_piece in self.white:
            if second_pos[1] - first_pos[1] == 1:
                if second_pos[0] == first_pos[0]:
                    if self.squares[second_pos].image != self.blank:
                        return False
                    return True
                if abs(second_pos[0] - first_pos[0]) == 1:
                    if self.squares[second_pos].image == self.blank:
                        return False
                    return True
        if selected_piece in self.black:
            if second_pos[1] - first_pos[1] == -1:
                if second_pos[0] == first_pos[0]:
                    if self.squares[second_pos].image != self.blank:
                        return False
                    return True
                if abs(second_pos[0] - first_pos[0]) == 1:
                    if self.squares[second_pos].image == self.blank:
                        return False
                    return True

    def move_rook(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        if first_pos[1] == second_pos[1]:
            pos1, pos2 = min(first_pos[0], second_pos[0]), max(first_pos[0], second_pos[0])
            print("R - Horizontal move")
            for i in range(pos1+1, pos2):
                print(self.squares[(i, first_pos[1])].image)
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
    
    def find_moves(self, color: bool, piece_pos: tuple[int, int]):
        moves = []
        for x in range(8):
            for y in range(8):
                if (x,y) != piece_pos:
                    if self.try_for_check(piece_pos, (x,y), color, True):
                        moves.append((x,y))
        return moves

    def check_move_legality(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        print("Kontrola: " + str(first_pos))
        print(str(self.squares[first_pos].image))
        selected_piece = self.squares[first_pos].image
        destination = self.squares[second_pos].image
        if (self.turns % 2 == 0 and destination in self.white):
            return False
        elif (self.turns % 2 == 1 and destination in self.black):
            return False
        if (selected_piece == self.pieces_white["b"] or selected_piece == self.pieces_black["b"]):
            #print("Bishop")
            return self.move_bishop(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["k"] or selected_piece == self.pieces_black["k"]):
            #print("King")
            return self.move_king(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["n"] or selected_piece == self.pieces_black["n"]):
            #print("Knight")
            return self.move_knight(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["p"] or selected_piece == self.pieces_black["p"]):
            #print("Pawn")
            return self.move_pawn(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["q"] or selected_piece == self.pieces_black["q"]):
            #print("Queen")
            return (self.move_rook(first_pos, second_pos) or self.move_bishop(first_pos, second_pos))
        elif (selected_piece == self.pieces_white["r"] or selected_piece == self.pieces_black["r"]):
            #print("Rook")
            return self.move_rook(first_pos, second_pos)
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
        if king_color:
            opponent_king = self.pieces_black["k"]
        else:
            opponent_king = self.pieces_white["k"]
        x, y = king_pos[0], king_pos[1]
        try:
            if self.squares[(x, y + 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x + 1, y + 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x + 1, y)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x + 1, y - 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x, y - 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x - 1, y - 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x - 1, y)].image == opponent_king:
                return True
        except KeyError:
            pass
        try:
            if self.squares[(x - 1, y + 1)].image == opponent_king:
                return True
        except KeyError:
            pass
        return False
    
    def piece_found(self, king_color: bool, piece: tk.PhotoImage, check_black: list, check_white: list) -> bool:
        if king_color == False: #black king
            if piece in self.black:
                if piece != self.pieces_black["k"]:
                    return False
            if piece in check_black:
                return True
            if piece in self.white:
                return False
            
        if king_color: #white king
            if piece in self.white:
                if piece != self.pieces_white["k"]:
                    return False
            if piece in check_white:
                return True
            if piece in self.white:
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
                if x+i or x+j or y+i or y+j > 7:
                    continue
                if x+i or x+j or y+i or y+j < 0:
                    continue
                if self.squares.get((x+i, y+j)).image == piece:
                    return True, (x+i, y+j)
                if self.squares.get((x+j, y+i)).image == piece:
                    return True, (x+j, y+i)
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

board = Board()
board.start()
board.root.mainloop()
