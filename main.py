import os
import tkinter as tk
from PIL import Image, ImageTk
import PIL

class Board(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.pack(padx = 30, pady = 30)

        #self.images_white = ["pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7"]
        #self.images_black = ["pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"]
        self.white = []
        self.black = []
        #self.images_blank = ["pyimages2", "pyimages9"]
        self.blank = None

        self.white_king_pos = (4,0)
        self.position_white = [(0,0), (1,0), (2,0), (3,0), (4,0), (5,0), (6,0), (7,0), (0,1), (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1)]
        #???self.position_white = [(i,j) for j in range(8) for i in range(0,2)]
        self.black_king_pos = (4,7)
        self.position_black = [(0,7), (1,7), (2,7), (3,7), (4,7), (5,7), (6,7), (7,7), (0,6), (1,6), (2,6), (3,6), (4,6), (5,6), (6,6), (7,6)]
        self.king_moved = False

        self.first_pos = None
        self.second_pos = None
        self.first_button = None
        self.second_button = None
        self.button_clicks = 0

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
        print(pos)
        print(str(self.squares[pos].image))
        if self.button_clicks % 2 == 0:
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
            
            #print("white king: " + str(self.white_king_pos))
            #print("black king: " + str(self.black_king_pos))
            if self.turns % 2 == 0: #kontrola sachu pro hrace momentalne na rade
                check, _ = self.check_piece_threats(self.white_king_pos, True)
                if check:
                    self.second_button.image = second_image
                    self.second_button["image"] = str(second_image)
                    self.first_button.image = first_image
                    self.first_button["image"] = str(first_image)
                    if self.king_moved:
                        print("Zmena krale zpatky")
                        self.white_king_pos = self.first_pos
                    self.king_moved = False
                    print("Zadny pohyb :(")
                    self.base_color(self.first_pos)
                    self.base_color(pos)
                    self.button_clicks += 1
                    return
                self.position_white[self.find_white_piece_index(self.first_pos)] = self.second_pos
                opponent_check, check_pos = self.check_piece_threats(self.black_king_pos, False)
                if opponent_check:
                    if not self.try_move_king(False):
                        for p in check_pos:
                            if self.take_threat_piece(p, False) or self.block_threat_piece(p, False):
                                break
                        self.end_game(False)
            else:
                check, _ = self.check_piece_threats(self.black_king_pos, False)
                if check:
                    self.second_button.image = second_image
                    self.second_button["image"] = str(second_image)
                    self.first_button.image = first_image
                    self.first_button["image"] = str(first_image)
                    if self.king_moved:
                        print("Zmena krale zpatky")
                        self.black_king_pos = self.first_pos
                    self.king_moved = False
                    print("Zadny pohyb :(")
                    self.base_color(self.first_pos)
                    self.base_color(pos)
                    self.button_clicks += 1
                    return
                self.position_black[self.find_black_piece_index(self.first_pos)] = self.second_pos
                opponent_check, check_pos = self.check_piece_threats(self.white_king_pos, True)
                if opponent_check:
                    if not self.try_move_king(True):
                        for p in check_pos:
                            if self.take_threat_piece(p, True) or self.block_threat_piece(p, True):
                                break
                        self.end_game(True)
                        
            self.button_clicks += 1
            self.turns += 1
            self.base_color(self.first_pos)
            self.base_color(pos)
            if self.king_moved:
                self.king_moved = False
            return
        else:
            print("Zadny pohyb :((")
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
        return
    
    def end_game(self, color):
        print("Konec hry: " + color)
        #todo
        return
    
    def try_for_check(self, first_pos: tuple[int, int], second_pos: tuple[int, int], color: bool) -> bool:
        try:
            if self.check_move_legality(first_pos, second_pos):
                first_piece = self.squares[first_pos].image
                second_piece = self.squares[second_pos].image
                self.squares[first_pos].image = self.blank
                self.squares[second_pos].image = first_piece
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
                    if self.try_for_check(p, pos, color):
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
            if self.try_for_check(king, move, color):
                return True
        return False
        
    
    def find_white_piece_index(self, pos: tuple[int, int]) -> int:
        for index, position in enumerate(self.position_white):
            if position == pos:
                return index
        print("????????")

    def find_black_piece_index(self, pos: tuple[int, int]) -> int:
        for index, position in enumerate(self.position_black):
            if position == pos:
                return index
        print("????????")
    
    def move_bishop(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        if (abs(first_pos[0] - second_pos[0]) != abs(first_pos[1] - second_pos[1])): #Kontrola rozdílu v pozicích
            return False
        y = first_pos[1]
        if second_pos[0] > first_pos[0]: #   x ->
            if second_pos[1] > first_pos[1]: #y ↑
                for x in range(first_pos[0] + 1, second_pos[0]):
                    y += 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if second_pos[1] < first_pos[1]: #y ↓
                for x in range(first_pos[0] + 1, second_pos[0]):
                    y -= 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
        if second_pos[0] < first_pos[0]: #x <-
            if second_pos[1] > first_pos[1]: #y ↑
                for x in range(first_pos[0] - 1, second_pos[0], -1):
                    y += 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if second_pos[0] < first_pos[0]: #y ↓
                for x in range(first_pos[0] - 1, second_pos[0], -1):
                    y -= 1
                    if (self.squares[(x, y)].image != self.blank):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
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
        selected_piece = self.first_button.image
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

    def check_move_legality(self, first_pos: tuple[int, int], second_pos: tuple[int, int]) -> bool:
        selected_piece = self.squares[first_pos].image
        destination = self.squares[second_pos].image
        print(destination)
        if (self.turns % 2 == 0 and destination in self.white):
            return False
        elif (self.turns % 2 == 1 and destination in self.black):
            return False
        if (selected_piece == self.pieces_white["b"] or selected_piece == self.pieces_black["b"]):
            print("Bishop")
            return self.move_bishop(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["k"] or selected_piece == self.pieces_black["k"]):
            print("King")
            return self.move_king(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["n"] or selected_piece == self.pieces_black["n"]):
            print("Knight")
            return self.move_knight(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["p"] or selected_piece == self.pieces_black["p"]):
            print("Pawn")
            return self.move_pawn(first_pos, second_pos)
        elif (selected_piece == self.pieces_white["q"] or selected_piece == self.pieces_black["q"]):
            print("Queen")
            return (self.move_rook(first_pos, second_pos) or self.move_bishop(first_pos, second_pos))
        elif (selected_piece == self.pieces_white["r"] or selected_piece == self.pieces_black["r"]):
            print("Rook")
            return self.move_rook(first_pos, second_pos)
        return False
        
    def base_color(self, pos: tuple[int, int]):
        if ((pos[0] + pos[1]) % 2 == 1):
            self.squares[pos].config(bg = "#eeeed2")
            return
        self.squares[pos].config(bg = "#769656")
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
    
    def piece_found(self, king_color: bool, piece: 'PIL.ImageTk.PhotoImage', check_black: list, check_white: list) -> bool:
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
                if self.squares.get(x+i, y+j, None).image == piece:
                    return True, (x+i, y+j)
                if self.squares.get(x+j, y+i, None).image == piece:
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
        """
        if b_q:
            return True, pos_bq
        if r_q:
            return True, pos_rq
        if n:
            return True, pos_n
        if p:
            return True, pos_p
        #return b_q or r_q or n or p
        return False, None
        """
        print("Check: " + str(b_q) + ", " + str(r_q) + ", " + str(n) + ", " + str(p))
        return (b_q or r_q or n or p), [pos_bq, pos_rq, pos_n, pos_p]
    

root = tk.Tk()
root.title("Chess")
root.iconbitmap("")

board = Board(root)
board.start()
#board.set_board()

root.mainloop()
