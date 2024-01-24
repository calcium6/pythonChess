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

        self.first_pos = 0
        self.second_pos = 0
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

    def select(self, pos):
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
            self.squares[self.second_pos].config(image = self.first_button["image"])
            self.squares[self.second_pos].image = self.first_button["image"]
            self.squares[self.first_pos].config(image = self.pieces_black["blank"])
            self.squares[self.first_pos].image = self.pieces_black["blank"]
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
    
    def moveBishop(self, pos):
        if (abs(self.first_pos[0] - pos[0]) != abs(self.first_pos[1] - pos[1])): #Kontrola rozdílu v pozicích
            return False
        y = self.first_pos[1]
        if pos[0] > self.first_pos[0]: #   x-->
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
        if pos[0] < self.first_pos[0]: #<--x
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

    def moveKing(self, pos):
        return True

    def moveKnight(self, pos):
        return True
    
    def movePawn(self, pos):
        return True

    def moveQueen(self, pos):
        return True

    def moveRook(self, pos):
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

    def checkLegality(self, pos):
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
            if (self.moveRook(pos) or self.moveBishop(pos)):
                return True
        elif (current_piece == wr or current_piece == br):
            print("Rook")
            return self.moveRook(pos)
        print("???")
        return False
        
    def base_color(self, pos):
        if ((pos[0] + pos[1]) % 2 == 1):
            self.squares[pos].config(bg = "#eeeed2")
            return
        self.squares[pos].config(bg = "#769656")
        return

root = tk.Tk()
root.title("Chess")
root.iconbitmap("")

board = Board(root)
board.start()
#board.set_board()

root.mainloop()
