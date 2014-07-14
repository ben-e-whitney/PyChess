import itertools        
import collections
import Queue

from Tkinter     import *
from ChessGame   import *
from HumanPlayer import *  

class ChessGui:
    """
    Simple gui to display ChessGame instance 
        - @p1 and @p2 must subclass Player.py and implement get_move if they are not HumanPlayers
        - @p1 can be None if running GameClient
        - @socket and @queue are used by GameClient.py and GameServer.py only
        - Logic should be handled entirely by ChessGame.py
        
    TODO: Try to implement gui with grid geometry manager as oppose to absolute positioning
          Also add ability to play again
    """

    def __init__(self, p1, p2, master, socket = None, queue = None):
        self.game = ChessGame()
        self.p1   = p1
        self.p2   = p2
        self.root = master
        self.root.title('Chess')
        self.root.geometry('600x650')
        self.root.protocol('WM_DELETE_WINDOW', self.on_window_close)
        self.socket = socket
        self.queue  = queue
        self._init_board()

    def _init_board(self):
        self.box_size      = 60
        self.gap_size      = 10
        self.board_height  = 8
        self.board_width   = 8
        self.x_margin      = (600 - self.board_width  * (self.box_size + self.gap_size))/2
        self.y_margin      = (600 - self.board_height * (self.box_size + self.gap_size))/2
        self.canvas        = None
        self.playing       = True
        self.waiting       = True if self.p1 == None else False 
        self._highlighted  = set()
        self._label_dict   = { }
        self._refresh_board() 

    def process_incoming(self):
        """
        Used to handle incoming move requests from socket
            - Only used by GameClient.py and GameServer.py
            - moves must be put in queue as ((x,y), (u,v))
        """
        
        if not self.queue:
            return
        
        while self.queue.qsize():
            at, to = self.queue.get(0)
            self._make_move(at, to)
            self.waiting = False
            
    def _advance_turn(self):
        """
        Update status based on the state of the board 
            - only HumanPlayers should be moved by clicks on the board (None implies move will come from P2P socket)
        """

        if self.game.has_winner():
            self.playing = False 
            
        color, player = self.game.get_turn(), self.p1
        if color != ChessGame.WHITE:
            player = self.p2

        if self.p1 != None and not isinstance(player, HumanPlayer):
            at, to = player.get_move()
        
        if self.game.color_in_check(color):
            self._refresh_status('red')
        else:
            self._refresh_status(None)

        self.selected_piece = None
        self._clear_highlighted()
            
    def _make_move(self, at, to):
        """  
        Use to update UI elements after call to move method in ChessGame
        """

        if not at or not to:
            return False
        
        x,y = at
        u,v = to

        made, _ = self.game.make_move(at, to)
        if made == True:
            self._advance_turn()
            self._refresh_square(x,y)
            self._refresh_square(u,v)

            if self.socket:
                self.socket.send_move(at, to)
                self.waiting = True

        if made == False:
            self._refresh_status('yellow')

            return True
        return False 

    def _on_board_click(self, event):
        """
        Handle piece/move selection
            - set the selected_piece if user has clicked on one of his/her pieces
            - try and make the move
            - P2P game is only available for HumanPlayer/HumanPlayer play
        """
        
        if not self.playing:
            return
        
        if self.socket:
            if hasattr(self.socket, 'conn') and not self.socket.conn:
                return 
            if self.waiting:
                return 
        
        x, y = event.widget.row, event.widget.col
        if self._set_piece(x,y):
            return

        self._make_move(self.selected_piece, (x,y))


    def _set_piece(self, x, y):
        """
        Set the clicked square as selected_piece if it is a piece for current player
        """

        piece = self.game.get_piece(x,y)
        if piece and piece.color == self.game.get_turn():
            
            self.selected_piece = x, y
            self._clear_highlighted()
            self._highlight_selected()
            
            return True
        return False

    def _top_left(self, i, j):
        """
        Use this method to get the top and left pixel coordinates from grid coordinates (i,j)
        credit Al Sweigart and http://inventwithpython.com/chapter17.html
        """
        
        left = i * (self.box_size + self.gap_size) + self.x_margin
        top  = j * (self.box_size + self.gap_size) + self.y_margin
        return top, left

    def _highlight_selected(self):
        """
        Highlight possible moves of the selected piece
        """

        if not self.selected_piece:
            return

        x, y = self.selected_piece
        for u, v in self.game.get_moves(x, y):
            self._refresh_square(u, v, 'yellow')

    def _clear_highlighted(self):
        """
        Return the highlighted squares to their normal appearence
        """
    
        for u, v in self._highlighted:
            self._refresh_square(u, v)

        self._highlighted = set()

    def _refresh_status(self, status, msg = None):
        """
        Player color should be text color of status label. If user tries to make a move that
        would set him/her in check, display YELLOW background. If user gets put in check by
        opponent, display RED background

        TODO: implement status updates/replay game option when game is over
        """
        
        background = ChessGame.BLACK
        foreground = ChessGame.WHITE
        turn_color = self.game.get_turn()

        if turn_color == ChessGame.WHITE:
            foreground, background = ChessGame.BLACK, ChessGame.WHITE

        label = ChessPiece(row = None, col = None, text = 'move ' + turn_color, master = self.canvas, bg = background, fg = foreground)
        label.place(x = 240, y = 600, width = 100)
        
        self._clear_highlighted()
        self.root.update()
        return

    def _refresh_square(self, i, j, color = None):
        """
        Tkinter slows down considerably if we redraw the board each time. Make changes only to
        cell specified at row = i, col = j
            - all images must be .gifs and be saved as COLOR_PIECENAME
            - e.g. white_knight.gif
        """

        if not color:
            color = 'gray'
            if (i+j) % 2 == 0:
                color = 'blue'
        else:
            self._highlighted.add((i,j))
        
        top, left  = self._top_left(i, j)
        label = ChessPiece(row = i, col = j, master = self.canvas, bg = color)
        label.bind('<Button-1>', self._on_board_click)

        piece = self.game.get_piece(i,j)
        if piece:

            path  = r'GIFChessPieces/'
            path  = path + piece.color + '_' + piece.name + '.gif' 
            img   = PhotoImage(file = path)
            label.config(image = img)
            label.image = img
        
        if (i,j) in self._label_dict:
            self.canvas.delete(self._label_dict[i,j])
        self._label_dict[i,j] = label
        
        label.place(x=top, y=left, height = self.box_size, width = self.box_size)
        self.canvas.pack(fill=BOTH, expand = 1)
    
    def _refresh_board(self):
        """
        Use this method to redraw the board based on the positions managed by ChessGame.py
        Note that everytime this method is called, a call to self.canvas.update_idletasks() should also be made (canvas loses focus)
        """
        
        self.selected_piece = None
        if self.canvas:
            self.canvas.delete('all')
        else:
            self.canvas = Canvas(self.root)
            
        for i, j in itertools.product(range(8), range(8)):
            self._refresh_square(i,j)
        self._refresh_status(None)

    def on_window_close(self):
        """
        Close any open connections and destroy Tk root
        """
        if self.socket:
            self.socket.close()

        self.root.destroy()

    # used only when running main method of ChessGui.py...should eventually be removed 
    def play(self):
        self.root.update()
        self.root.mainloop()

class ChessPiece(Label):
    """
    Class to represent square on chess board
        - Subclass from label and add row, col to allow easy accessibility 
    """
    def __init__(self, row, col, **kwargs):
        Label.__init__(self, **kwargs)
        self.row = row
        self.col = col

# only for testing purposes 
def main():
    p1 = HumanPlayer('joe')
    p2 = HumanPlayer('ben')
    root = Tk()
    ChessGui(p1,p2, root).play()



if __name__ == '__main__':
    main()  
