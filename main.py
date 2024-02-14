import os
import tkinter as tk
from PIL import Image, ImageTk

class Board(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.pack(padx = 30, pady = 30)

        self.images_white = ["pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7"]
        self.images_black = ["pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"]
        self.images_blank = ["pyimages2", "pyimages9"]

        self.white_king_pos = (0, 4)
        self.black_king_pos = (7, 4)
        self.king_moved = False

        self.first_pos = (0, 0)
        self.second_pos = (0, 0)
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
                    square = tk.Button(self, bg="#eeeed2", activebackground="#baca44", borderwidth=0,text = str(7-row) + str(col))
                else:
                    square = tk.Button(self, bg="#769656", activebackground="#baca44", borderwidth=0,text = str(7-row) + str(col))
                square.grid(row=row, column=col)
                pos = (7-row, col)
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
        start_position = {(0,0):"r", (0,1):"n", (0,2):"b", (0,3):"q", (0,4):"k", (0,5):"b", (0,6):"n", (0,7):"r"}
        for square in start_position:
            self.squares[(square[0]+7, square[1])].config(image = self.pieces_black[start_position[square]])
            self.squares[(square[0]+7, square[1])].image = self.pieces_black[start_position[square]]
            self.squares[square].config(image = self.pieces_white[start_position[square]])
            self.squares[square].image = self.pieces_white[start_position[square]]
        
        for i in range(0, 8):
            self.squares[(6,i)].config(image = self.pieces_black["p"])
            self.squares[(6,i)].image = self.pieces_black["p"]
            self.squares[(1,i)].config(image = self.pieces_white["p"])
            self.squares[(1,i)].image = self.pieces_white["p"]
            for j in range(2, 6):
                self.squares[(j,i)].config(image = self.pieces_black["blank"])
                self.squares[(j,i)].image = self.pieces_black["blank"]

    def start(self):
        self.load_pieces()
        self.place_pieces()

    def select(self, pos: tuple):
        print(pos)
        if self.button_clicks % 2 == 0:
            if (self.squares[pos]["image"] in self.images_white) and self.turns % 2 == 0:
                self.first_pos = pos
                self.first_button = self.squares[pos]
                self.button_clicks += 1
                self.squares[pos].config(bg = "#baca44")
            if (self.squares[pos]["image"] in self.images_black) and self.turns % 2 == 1:
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
        if (self.checkLegality(pos)):
            print("Pohyb z " + str(self.first_pos) + " na " + str(pos)) 
            self.second_pos = pos
            self.second_button = self.squares[pos]
            first_image = self.first_button["image"]
            second_image = self.second_button["image"]
            self.second_button["image"] = first_image
            self.first_button["image"] = "pyimage9"
            
            print("white king: " + str(self.white_king_pos))
            print("black king: " + str(self.black_king_pos))
            if self.turns % 2 == 0:
                if self.king_check(self.white_king_pos, True):
                    self.second_button["image"] = second_image
                    self.first_button["image"] = first_image
                    if self.king_moved:
                        self.white_king_pos = self.first_pos
                    self.king_moved = False
                    print("Zadny pohyb :(")
                    self.base_color(self.first_pos)
                    self.base_color(pos)
                    self.button_clicks += 1
                    return
            else:
                if self.king_check(self.black_king_pos, False):
                    self.second_button["image"] = second_image
                    self.first_button["image"] = first_image
                    if self.king_moved:
                        self.black_king_pos = self.first_pos
                    self.king_moved = False
                    print("Zadny pohyb :(")
                    self.base_color(self.first_pos)
                    self.base_color(pos)
                    self.button_clicks += 1
                    return

            self.button_clicks += 1
            self.turns += 1
            self.base_color(self.first_pos)
            self.base_color(pos)
        else:
            print("Zadny pohyb :(")
            self.base_color(self.first_pos)
            self.base_color(pos)
            self.button_clicks += 1
        return
    
    def moveBishop(self, pos: tuple):
        if (abs(self.first_pos[0] - pos[0]) != abs(self.first_pos[1] - pos[1])): #Kontrola rozdílu v pozicích
            return False
        y = self.first_pos[1]
        if pos[0] > self.first_pos[0]: #   x ->
            if pos[1] > self.first_pos[1]: #y ↑
                for x in range(self.first_pos[0] + 1, pos[0]):
                    y += 1
                    if (self.squares[(x, y)]["image"] != "pyimage9"):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if pos[1] < self.first_pos[1]: #y ↓
                for x in range(self.first_pos[0] + 1, pos[0]):
                    y -= 1
                    if (self.squares[(x, y)]["image"] != "pyimage9"):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
        if pos[0] < self.first_pos[0]: #x <-
            if pos[1] > self.first_pos[1]: #y ↑
                for x in range(self.first_pos[0] - 1, pos[0], -1):
                    y += 1
                    if (self.squares[(x, y)]["image"] != "pyimage9"):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
            if pos[1] < self.first_pos[1]: #y ↓
                for x in range(self.first_pos[0] - 1, pos[0], -1):
                    y -= 1
                    if (self.squares[(x, y)]["image"] != "pyimage9"):
                        print("V cestě je figurka: " + str(x) + " , " + str(y))
                        return False
        return True

    def moveKing(self, pos: tuple):
        if abs(self.first_pos[0] - pos[0]) <= 1 and abs(self.first_pos[1] - pos[1]) <= 1:
            if not self.king_nearby(pos, (self.turns % 2 == 0)):
                if self.turns % 2 == 0:
                    self.white_king_pos = pos
                else:
                    self.black_king_pos = pos
                self.king_moved = True
                return True
        return False

    def moveKnight(self, pos: tuple):
        if abs(self.first_pos[0] - pos[0]) == 2 and abs(self.first_pos[1] - pos[1]) == 1:
            return True
        if abs(self.first_pos[0] - pos[0]) == 1 and abs(self.first_pos[1] - pos[1]) == 2:
            return True
        return False
    
    def movePawn(self, pos: tuple):
        selected_piece = self.first_button["image"]
        if self.first_pos[0] == 1: #První pohyb pro bílou
            if pos[0] - self.first_pos[0] == 2 and pos[1] == self.first_pos[1]:
                if self.squares[(2, pos[1])]["image"] != "pyimage9" and self.squares[(3, pos[1])]["image"] != "pyimage9":
                    return False
                return True
        if self.first_pos[0] == 6: #První pohyb pro černou
            if pos[0] - self.first_pos[0] == -2 and pos[1] == self.first_pos[1]:
                if self.squares[(5, pos[1])]["image"] != "pyimage9" and self.squares[(4, pos[1])]["image"] != "pyimage9":
                    return False
                return True
        if selected_piece in self.images_white:
            if pos[0] - self.first_pos[0] == 1:
                if pos[1] == self.first_pos[1]:
                    if self.squares[pos]["image"] != "pyimage9":
                        return False
                    return True
                if abs(pos[1] - self.first_pos[1]) == 1:
                    if self.squares[pos]["image"] == "pyimage9":
                        return False
                    return True
        if selected_piece in self.images_black:
            if pos[0] - self.first_pos[0] == -1:
                if pos[1] == self.first_pos[1]:
                    if self.squares[pos]["image"] != "pyimage9":
                        return False
                    return True
                if abs(pos[1] - self.first_pos[1]) == 1:
                    if self.squares[pos]["image"] == "pyimage9":
                        return False
                    return True

    def moveQueen(self, pos: tuple):
        if self.moveRook(pos) or self.moveBishop(pos):
            return True
        return False

    def moveRook(self, pos: tuple):
        if self.first_pos[0] == pos[0]:
            pos1, pos2 = min(self.first_pos[1], pos[1]), max(self.first_pos[1], pos[1])
            print("R - Horizontal move")
            for i in range(pos1+1, pos2):
                print(self.squares[(self.first_pos[0], i)]["image"])
                if self.squares[(self.first_pos[0], i)]["image"] != "pyimage9":
                    print(str(self.first_pos[0]) + " , " + str(i))
                    print("V cestě je figurka")
                    return False
            return True
        if self.first_pos[1] == pos[1]:
            print("R - Vertical move")
            pos1, pos2 = min(self.first_pos[0], pos[0]), max(self.first_pos[0], pos[0])
            print(str(pos1) + " , " + str(pos2))
            for i in range(pos1+1, pos2):
                print(self.squares[(i, self.first_pos[1])]["image"])
                if self.squares[(i, self.first_pos[1])]["image"] != "pyimage9":
                    print(str(i) + " , " + str(self.first_pos[1]))
                    print("V cestě je figurka")
                    return False
            return True
        print("Diagonal")
        return False

    def checkLegality(self, pos: tuple):
        wb, wk, wn, wp, wq, wr = "pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7" #citelnost kodu
        bb, bk, bn, bp, bq, br = "pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"
        piece = self.squares[pos]["image"]
        current_piece = self.first_button["image"]
        print(piece)
        if (self.turns % 2 == 0 and piece in self.images_white):
            return False
        elif (self.turns % 2 == 1 and piece in self.images_black):
            return False
        if (current_piece == wb or current_piece == bb):
            print("Bishop")
            return self.moveBishop(pos)
        elif (current_piece == wk or current_piece == bk):
            print("King")
            return self.moveKing(pos)
        elif (current_piece == wn or current_piece == bn):
            print("Knight")
            return self.moveKnight(pos)
        elif (current_piece == wp or current_piece == bp):
            print("Pawn")
            return self.movePawn(pos)
        elif (current_piece == wq or current_piece == bq):
            print("Queen")
            return (self.moveRook(pos) or self.moveBishop(pos))
        elif (current_piece == wr or current_piece == br):
            print("Rook")
            return self.moveRook(pos)
        return False
        
    def base_color(self, pos: tuple):
        if ((pos[0] + pos[1]) % 2 == 1):
            self.squares[pos].config(bg = "#eeeed2")
            return
        self.squares[pos].config(bg = "#769656")
        return
    
    def king_nearby(self, king_pos: tuple, king_color: bool):
        if king_color:
            opponent_king = "pyimage10"
        else:
            opponent_king = "pyimage3"
        x, y = king_pos[0], king_pos[1]
        try:
            if self.squares[(x, y + 1)]["image"] == opponent_king:
                return True
            if self.squares[(x + 1, y + 1)]["image"] == opponent_king:
                return True
            if self.squares[(x + 1, y)]["image"] == opponent_king:
                return True
            if self.squares[(x + 1, y - 1)]["image"] == opponent_king:
                return True
            if self.squares[(x, y - 1)]["image"] == opponent_king:
                return True
            if self.squares[(x - 1, y - 1)]["image"] == opponent_king:
                return True
            if self.squares[(x - 1, y)]["image"] == opponent_king:
                return True
            if self.squares[(x - 1, y + 1)]["image"] == opponent_king:
                return True
        except KeyError:
            pass
        return False
    
    def piece_found(self, king_color: bool, piece: str, check_black: list, check_white: list):
        if king_color == False: #black king
            if piece in self.images_black:
                if piece != "pyimage10":
                    return False
            if piece in check_black:
                return True
            if piece in self.images_white:
                return False
            
        if king_color: #white king
            if piece in self.images_white:
                if piece != "pyimage3":
                    return False
            if piece in check_white:
                return True
            if piece in self.images_white:
                return False

    def check_bishop_queen(self, king_pos: tuple, king_color: bool):
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
                return False
            if x1 <= 7:
                if y11 <= 7:
                    if self.squares[(x1, y11)]["image"] != "pyimage9":
                        if self.piece_found(king_color, self.squares[(x1, y11)]["image"], ["pyimage1", "pyimage6"], ["pyimage8", "pyimage13"]):
                            return True
                        y11 = 8
                if y12 >= 0:
                    if self.squares[(x1, y12)]["image"] != "pyimage9":
                        if self.piece_found(king_color, self.squares[(x1, y12)]["image"], ["pyimage1", "pyimage6"], ["pyimage8", "pyimage13"]):
                            return True
                        y12 = -1
            if x2 >= 0:
                if y21 <= 7:
                    if self.squares[(x2, y21)]["image"] != "pyimage9":
                        if self.piece_found(king_color, self.squares[(x2, y21)]["image"], ["pyimage1", "pyimage6"], ["pyimage8", "pyimage13"]):
                            return True
                        y21 = 8
                if y22 >= 0:
                    if self.squares[(x2, y22)]["image"] != "pyimage9":
                        if self.piece_found(king_color, self.squares[(x2, y22)]["image"], ["pyimage1", "pyimage6"], ["pyimage8", "pyimage13"]):
                            return True
                        y22 = -1
        return False
    
    def check_rook_queen(self, king_pos: tuple, king_color: bool):
        x1, x2 = king_pos[0], king_pos[0]
        y1, y2 = king_pos[1], king_pos[1]
        for i in range(0, 8):
            x1 += 1
            y1 += 1
            x2 -= 1
            y2 -= 1
            if x1 <= 7:
                if self.squares[(x1, king_pos[1])]["image"] != "pyimage9":
                    if self.piece_found(king_color, self.squares[(x1, king_pos[1])]["image"], ["pyimage6", "pyimage7"], ["pyimage13", "pyimage14"]):
                        return True
                    x1 = 8
            if y1 <= 7:
                if self.squares[(king_pos[0], y1)]["image"] != "pyimage9":
                    if self.piece_found(king_color, self.squares[(king_pos[0], y1)]["image"], ["pyimage6", "pyimage7"], ["pyimage13", "pyimage14"]):
                        return True
                    y1 = 8
            if x2 >= 0:
                if self.squares[(x2, king_pos[1])]["image"] != "pyimage9":
                    if self.piece_found(king_color, self.squares[(x2, king_pos[1])]["image"], ["pyimage6", "pyimage7"], ["pyimage13", "pyimage14"]):
                        return True
                    x2 = -1
            if y2 >= 0:
                if self.squares[(king_pos[0], y2)]["image"] != "pyimage9":
                    if self.piece_found(king_color, self.squares[(king_pos[0], y2)]["image"], ["pyimage6", "pyimage7"], ["pyimage13", "pyimage14"]):
                        return True
                    y2 = -1
        return False
    
    def check_knight(self, king_pos: tuple, king_color: bool):
        x, y = king_pos[0], king_pos[1]
        if king_color:
            piece = "pyimage11"
        else:
            piece = "pyimage4"
        try:
            if self.squares[(x + 1, y + 2)]["image"] == piece:
                return True
            if self.squares[(x + 1, y - 2)]["image"] == piece:
                return True
            if self.squares[(x - 1, y + 2)]["image"] == piece:
                return True
            if self.squares[(x - 1, y - 2)]["image"] == piece:
                return True
            if self.squares[(x + 2, y + 1)]["image"] == piece:
                return True
            if self.squares[(x + 2, y - 1)]["image"] == piece:
                return True
            if self.squares[(x - 2, y + 1)]["image"] == piece:
                return True
            if self.squares[(x - 2, y - 1)]["image"] == piece:
                return True
        except KeyError:
            pass
        return False

    def check_pawn(self, king_pos: tuple, king_color: bool):
        x, y = king_pos[0], king_pos[1]
        try:
            if king_color:
                if self.squares[(x + 1, y + 1)]["image"] == "pyimage12":
                    return True
                if self.squares[(x + 1, y - 1)]["image"] == "pyimage12":
                    return True
            else:
                if self.squares[(x - 1, y + 1)]["image"] == "pyimage5":
                    return True
                if self.squares[(x - 1, y - 1)]["image"] == "pyimage5":
                    return True
        except KeyError:
            pass
        return False

    
    def king_check(self, king_pos, king_color): #king_color: True - white, False - black
        b_q = self.check_bishop_queen(king_pos, king_color)
        r_q = self.check_rook_queen(king_pos, king_color)
        n = self.check_knight(king_pos, king_color)
        p = self.check_pawn(king_pos, king_color)
        print("Check: " + str(b_q) + ", " + str(r_q) + ", " + str(n) + ", " + str(p))
        return b_q or r_q or n or p
    

root = tk.Tk()
root.title("Chess")
root.iconbitmap("")

board = Board(root)
board.start()
#board.set_board()

root.mainloop()
