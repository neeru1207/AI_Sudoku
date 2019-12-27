'''
The Main UI File that controls and executes all the other files.
'''
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox, filedialog
from RecognizeAndConstructBoard import ConstructGrid
from BoardExtractor import BoardExtractor
from SudokuSolver import Solver
import webbrowser
import os
from shutil import rmtree
from copy import copy, deepcopy

'''The main window controlling all the frames.'''
class MainUI(Tk):

    def __init__(self, modeltype):
        Tk.__init__(self)
        self.resizable(width=False, height=False)
        # Create the folders if they don't already exist
        try:
            os.makedirs("CleanedBoardCells")
            os.makedirs("StagesImages")
            os.makedirs("BoardCells")
        except:
            pass
        # Modeltype CNN or KNN
        self.modeltype = modeltype
        # Variables for the Sudoku Board and Solution respectively
        self.board = None
        self.solutiongrid = None
        # The main frame
        self.container = Frame(self)
        # An object for the RecognizeAndConstructBoard Class
        self.recognizeandconstructobj = None
        # An object for the Boardextractor Class
        self.boardextractor = None
        self.container.pack(fill=BOTH, expand=True)
        # A Dictionary containing all the frames
        self.frameslist = {}
        # Create the HomePage Frame and StagesFrame Frame and append to frames list
        for F in (HomePage, StagesFrame):
            frame = F(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frameslist[F] = frame
        # Show the first frame ie.. the homepage
        self.show_frame(HomePage)
        self.title("AI Sudoku")
    '''This function is called when the user presses the next button in the Home Page.
    As soon as the path to the image is obtained, this function initializes an object of 
    BoardExtractor, calls it's functions to get a 2D array of the board cell images, then 
    creates an object of ConstructGrid Class passing the 2D array to it, then the recognized sudoku
    grid returned by the constructgrid() function is stored in the board variable. Then the
    Sudoku Game Object is created, the SudokuUI Frame is created and added to the frameslist. 
    '''
    def get_and_set_board(self):
        self.boardextractor = BoardExtractor(self.frameslist[HomePage].selectedimagepath)
        self.boardextractor.preprocess_image()
        self.boardextractor.detect_and_crop_grid()
        boardcells = self.boardextractor.create_image_grid()
        self.recognizeandconstructobj = ConstructGrid(boardcells, self.modeltype)
        board = self.recognizeandconstructobj.constructgrid()
        self.board = deepcopy(board)
        self.sudokugameobj = SudokuGame(self.board)
        F = SudokuUI
        frame = F(self.container, self, self.sudokugameobj)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frameslist[F] = frame

    '''This function is called when the reveal button is pressed in the SudokuUI Frame.
    This function creates an object of the Sudoku Solver's Solver class and stored the solved
    grid returned by it's solve_sudoku() function in the solutiongrid variable'''
    def getsolngrid(self):
        self.solutiongrid = None
        solverobj = Solver()
        tmp = deepcopy(self.board)
        #solverobj.print_board(tmp)
        if not solverobj.checkvalidpuzzle(tmp):
            messagebox.showerror("Invalid Puzzle", "The puzzle board is invalid, please rectify the wrong entries and try again")
            return False
        if not solverobj.solve_sudoku(tmp):
            messagebox.showerror("No Solution!", "This puzzle has no solution")
            self.show_frame(SudokuUI)
        else:
            self.solutiongrid = deepcopy(tmp)
        return True

    '''This function shows a particular frame by raising it'''
    def show_frame(self, cont):
        frame = self.frameslist[cont]
        frame.tkraise()

    '''This function cleans up by deleting the created directories'''
    def cleanup(self):
        try:
            rmtree("BoardCells/")
        except:
            pass
        try:
            rmtree("CleanedBoardCells/")
        except:
            pass
        try:
            rmtree("StagesImages/")
        except:
            pass

'''This is the First Frame which is where the user selects the image, the image is displayed and
upon pressing next, the get_and_set_board() function is called and the next frame is shown.'''
class HomePage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # The container frame is the parent
        self.parent = parent
        # The instance of the Main UI
        self.controller = controller
        # Initially no image is selected
        self.selectedimagepath = None
        self.controller.title("Sudoku Solver")
        self.titlelabel = Label(self, text="Smart Sudoku Solver", relief=GROOVE, font=("Consolas 18"), bg="lightgreen")
        self.titlelabel.grid(row=0, columnspan=4, sticky="ew")

        self.selimg = Button(self, text='Open image', command=self.open_img, relief=RAISED, fg="blue", bg="light blue",
                             borderwidth=3, padx=20)
        self.selimg.grid(row=1, column=0, padx=5, pady=5)
        self.imagepathdisplay = Entry(self, text="Path to image file", fg="gray", width=40, font=("Consolas 12"), borderwidth=3)
        self.imagepathdisplay.insert(0, "No Image Selected")
        self.imagepathdisplay.grid(row=1, column=1, padx=5, pady=5)

        self.imglabel = Label(self, text="Preview", font=("Consolas 10"))
        self.imglabel.grid(row=2, columnspan=2, sticky="w", padx=3, pady=3)

        self.img = ImageTk.PhotoImage(Image.open("defimg.png").resize((490, 450), Image.ANTIALIAS))
        self.imgpanel = Label(self, image=self.img)
        self.imgpanel.grid(row=3, columnspan=2, padx=15, pady=3)
        # The Exit Button
        self.exitbut = Button(self, text="Exit", command=self.exit, padx=30, fg="red", bg="lightblue")
        self.exitbut.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        # The Next Button
        self.nextbut = Button(self, text="Next", command=self.next, padx=30, fg="gray")
        self.nextbut.grid(row=4, column=1, padx=5, pady=5, sticky="e")
        self.mylink = Label(self, text="Developed by Neeramitra Reddy", borderwidth=3, relief=SUNKEN, fg="blue",
                            cursor="hand2")

        self.mylink.grid(row=5, columnspan=6, sticky="ew")
        self.mylink.bind("<Button-1>", lambda e: self.callback("https://github.com/neeru1207"))

    # Get_and_set_the_board, set the selected image path in the Stages Frame and show the Stages Frame
    def next(self):
        if self.selectedimagepath is None:
            messagebox.showerror("Error", "Image not selected!")
            return
        self.controller.frameslist[StagesFrame].setselectedimgpath()
        self.controller.get_and_set_board()
        self.controller.show_frame(StagesFrame)
        self.controller.title("Stages")

    # A function to open a link in a web browser
    def callback(self, url):
        webbrowser.open_new(url)

    # Exit function
    def exit(self):
        if messagebox.askyesno("Exit", "Do you really want to exit?"):
            self.controller.cleanup()
            self.controller.destroy()
        else:
            pass

    # Open image and handle errors
    def open_img(self):
        try:
            filename = filedialog.askopenfilename(title='open')
        except:
            return
        try:
            img = Image.open(filename)
        except:
            messagebox.showerror("ERROR", "Non Image File selected")
            return
        self.selectedimagepath = filename
        self.imagepathdisplay.configure(fg="black")
        self.imagepathdisplay.delete(0, END)
        self.imagepathdisplay.insert(0, filename)
        img = img.resize((490, 450), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.imgpanel.configure(image=img)
        self.img = img
        self.nextbut.configure(fg="black")

'''This is the Second Frame where the different stages of processing the image
are shown. The user can choose to skip these by pressing the skip button or view every stage
by pressing next'''
class StagesFrame(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.numberofstages = 15
        # This is initialized as None and set to the selected image path as soon as the next
        # button is pressed by the user in the first frame.
        self.initimagepath = None
        # A dictionary to store the titles of various stages
        self.stagesdict = {1: 'Initial Image', 2: 'Gaussian Blurring Image', 3: 'Adaptive Gaussian Thresholding',
                           4: 'Inverting', 5: 'Dilating to fill up cracks', 6: 'Floodfilling in progress',
                           7: 'Biggest blob found!', 8: 'Eroding the grid a bit',
                           9: 'Using Hough Transform to find lines',
                           10: 'Finding the extreme lines',
                           11: 'Plotting the border lines points on the original image',
                           12: 'Correcting Perspective and cropping the grid out',
                           13: 'Thresholding and Inverting the grid',
                           14: 'Slicing the grid to get the cells',
                           15: 'Blackfilling and centering the image'}
        self.currentstage = 1
        self.mylink = Label(self, text="Developed by Neeramitra Reddy", borderwidth=3, relief=SUNKEN, fg="blue",
                            cursor="hand2")

        self.mylink.grid(row=5, columnspan=6, sticky="ew")
        self.mylink.bind("<Button-1>", lambda e: self.callback("https://github.com/neeru1207"))
        self.controller.title("Stages")
        self.stagelabel = Label(self, relief=GROOVE, text=self.stagesdict[self.currentstage], font=("Consolas 14"),
                                bg="lightblue")
        self.stagelabel.grid(row=0, columnspan=4, sticky="ew")
        self.img = ImageTk.PhotoImage(Image.open("defimg.png").resize((490, 490), Image.ANTIALIAS))
        self.imgpanel = Label(self, image=self.img)
        self.imgpanel.grid(row=1, columnspan=4, padx=15, pady=10)
        #Home button
        self.gobackhome = Button(self, text="<<Home", command=self.homefunc, font=("Consolas 12"), bg="lightgray")
        self.gobackhome.grid(row=2, column=0, ipadx=20, ipady=5, padx=3, pady=3)
        #Back button
        self.backbut = Button(self, text="<Back", font=("Consolas 12"), fg="Red", command=self.back, bg="lightblue")
        self.backbut.grid(row=2, column=1, ipadx=20, ipady=5, padx=3, pady=3)
        #Next button
        self.nextbut = Button(self, text="Next>", font=("Consolas 12"), fg="Green", bg="lightblue", command=self.next)
        self.nextbut.grid(row=2, column=2, ipadx=20, ipady=5, padx=3, pady=3)
        #Skip button
        self.skipbut = Button(self, text="Skip>>", fg="Black", font=("Consolas 12"), command=self.skipfunc,
                              bg="lightgray")
        self.skipbut.grid(row=2, column=3, ipadx=20, ipady=5, padx=3, pady=3)

    '''This function is called when the user presses next in the HomePage Frame.
    This function sets the selectedimagepath variable to the path of the image selected by
    the user. This then loads the selected image in the Initial Image stage'''
    def setselectedimgpath(self):
        self.initimagepath = self.controller.frameslist[HomePage].selectedimagepath
        img = ImageTk.PhotoImage(Image.open(self.initimagepath).resize((490, 490), Image.ANTIALIAS))
        self.imgpanel.configure(image=img)
        self.img = img

    '''A function to open a link in a webbrowser'''
    def callback(self, url):
        webbrowser.open_new(url)

    '''Go back to Home function. This loads the first frame'''
    def homefunc(self):
        self.controller.show_frame(HomePage)
        self.controller.title("AI Sudoku")

    '''Skip and go to the Sudoku frame'''
    def skipfunc(self):
        self.controller.show_frame(SudokuUI)
        self.controller.title("Sudoku Recognized!")

    '''Back function'''
    def back(self):
        #If we are at the initial stage, then pressing back takes the user back to the
        #first frame
        if self.currentstage == 1:
            self.controller.show_frame(HomePage)
            self.controller.title("AI Sudoku")
            return
        self.currentstage -= 1
        self.stagelabel['text'] = self.stagesdict[self.currentstage]
        #If we have reached the first frame, then load the initial image
        if self.currentstage == 1:
            currstageimgpath = self.initimagepath
        else:
            currstageimgpath = "StagesImages/" + str(self.currentstage - 1) + ".jpg"
        img = ImageTk.PhotoImage(Image.open(currstageimgpath).resize((490, 490), Image.ANTIALIAS))
        self.imgpanel.configure(image=img)
        self.img = img

    '''Next function that takes the user to the next stage or the next frame if the user is already
    in the last stage'''
    def next(self):
        # Check if the user is in the last stage
        if self.currentstage == self.numberofstages:
            self.controller.show_frame(SudokuUI)
            self.controller.title("Sudoku Recognized")
            return
        self.currentstage += 1
        self.stagelabel['text'] = self.stagesdict[self.currentstage]
        currstageimgpath = "StagesImages/" + str(self.currentstage - 1) + ".jpg"
        img = ImageTk.PhotoImage(Image.open(currstageimgpath).resize((490, 490), Image.ANTIALIAS))
        self.imgpanel.configure(image=img)
        self.img = img

'''The Third Frame that shows the Recognized Sudoku grid. Since there might be errors in the 
recognition, the user can change entries in the grid and then view the solution.
This Frame encompasses two stages - one when the user has clicked on the reveal solution button 
and the solution is displayed vs the second where the user is still correcting the grid'''
class SudokuUI(Frame):

    def __init__(self, parent, controller, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        # A BOOL that keeps track of whether the user has clicked on the reveal solution
        # button or not.
        self.solutionrevealed = False
        self.row, self.col = -1, -1
        self.solutionrevealed = False
        self.controller.title("Sudoku Recognized!")
        self.toplabel = Label(self,
                              text="Click on any cell to enter or change any wrong entries.\nEnter . to empty the cell or a number to fill it",
                              font=("Consolas 12"), relief=GROOVE, bg="lightblue")
        self.toplabel.pack(fill=X, side=TOP)
        # The canvas for the grid
        self.canvas = Canvas(self,
                             width=490,
                             height=490)
        self.canvas.pack(fill=BOTH, side=TOP, padx=10)
        # The reveal solution button
        self.reveal_button = Button(self,
                                    text="Reveal Solution", font=("Consolas 12"), relief=RAISED, fg="green",
                                    bg="lightblue",
                                    command=self.reveal_solution, padx=4, pady=4)
        self.reveal_button.pack(fill=X, side=RIGHT, padx=20, pady=5)
        self.home_button = Button(self, text="Go to Home", font=("Consolas 12"), relief=RAISED, fg="red",
                                  bg="lightblue", command=self.gohome, padx=4, pady=4)
        self.home_button.pack(fill=X, side=LEFT, padx=20, pady=5)
        self.back_button = Button(self, text="Back", font=("Consolas 12"), relief=RAISED, fg="red",
                                  bg="lightblue", command=self.goback, padx=10, pady=4)
        self.back_button.pack(fill=X, side=LEFT, padx=50, pady=5)
        self.mylink = Label(self, text="Developed by Neeramitra Reddy", borderwidth=3, relief=SUNKEN, fg="blue",
                            cursor="hand2")
        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    '''This function first checks the solutionrevealed Boolean and determines whether the user has
    clicked on reveal solution or not. If the user is on the revealed solution frame then
    this takes the user back to the Sudoku Page otherwise takes the user back to the Second or
    Stages Frame'''
    def goback(self):
        if self.solutionrevealed:
            self.__draw_grid()
            self.__draw_puzzle()
            self.solutionrevealed = False
            self.reveal_button.configure(bg="lightblue", fg="red")
            self.toplabel['text'] = "Click on any cell to enter or change any wrong entries.\nEnter . to empty the cell or a number to fill it"
        else:
            self.controller.show_frame(StagesFrame)
            self.controller.title("Stages")

    '''This function takes the user back to the Home Page'''
    def gohome(self):
        self.controller.show_frame(HomePage)
        self.controller.title("AI Sudoku")


    '''Draws grid divided with blue lines into 3x3 squares'''
    def __draw_grid(self):
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = 20 + i * 50
            y0 = 20
            x1 = 20 + i * 50
            y1 = 490 - 20
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = 20
            y0 = 20 + i * 50
            x1 = 490 - 20
            y1 = 20 + i * 50
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    '''Draws the puzzle on the grid after erasing the previous entries'''
    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = 20 + j * 50 + 50 / 2
                    y = 20 + i * 50 + 50 / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )
    '''Draws the solution grid after erasing previous entries. This function is called
    when the user clicks on the reveal solution button'''
    def draw_soln_puzzle(self, puzzle, solution):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = solution[i][j]
                if answer != 0:
                    x = 20 + j * 50 + 50 / 2
                    y = 20 + i * 50 + 50 / 2
                    original = puzzle[i][j]
                    color = "black" if answer == original else "green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )
    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = 20 + self.col * 50 + 1
            y0 = 20 + self.row * 50 + 1
            x1 = 20 + (self.col + 1) * 50 - 1
            y1 = 20 + (self.row + 1) * 50 - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    '''Handle mouse clicks by determining the cell in which the user clicked.'''
    def __cell_clicked(self, event):
        x, y = event.x, event.y
        if 20 < x < 470 and 20 < y < 470:
            self.canvas.focus_set()
            row, col = (y - 20) // 50, (x - 20) // 50
            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    '''Handle Key presses'''
    def __key_pressed(self, event):
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
        if self.row >= 0 and self.col >= 0 and event.char == ".":
            self.game.puzzle[self.row][self.col] = 0
            self.__draw_puzzle()
            self.__draw_cursor()

    '''The command function for the reveal function button. This function erases the board and redraws
     the solution grid and disables the reveal solution button'''
    def reveal_solution(self):
        self.__draw_grid()
        self.controller.board = deepcopy(self.game.puzzle)
        tmpbool = self.controller.getsolngrid()
        if not tmpbool:
            return
        self.draw_soln_puzzle(self.game.puzzle, self.controller.solutiongrid)
        self.solutionrevealed = True
        self.toplabel['text'] = "Solution Revealed!"
        self.reveal_button.configure(bg="lightgray", fg="gray")

class SudokuGame(object):
    def __init__(self, board):
        self.start_puzzle = board
        self.puzzle = board
