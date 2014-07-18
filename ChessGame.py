import collections, itertools, random

class ChessGame:
    """
    Controller class to be used with ChessGUI.py. All logic for chess game
    should be implemented here.

    TODO: implement castling and en passant in _get_piece_moves. Pawns also need to
          be able to move two spots at the beginning of the game
          and be traded for highest value piece if they make it to other side

    """

    BLACK = 'black'
    WHITE = 'white'
    Piece = collections.namedtuple('Piece', ['name', 'color'])

    def __init__(self):
        """
        WHTIE always goes first 
        """

        self.__turn_info  = { 'turn': ChessGame.WHITE }
        self.init_board()

    def init_board(self):
        """
        Maintain game board as a dict and keep location of player pieces in sets
        No top level classes should have access to self.__board
        """

        self.__board = dict()
        order  = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop',
                  'knight', 'rook']
        for j, name in enumerate(order):

            self.__board[(0, j)] = ChessGame.Piece( name,  ChessGame.WHITE)
            self.__board[(7, j)] = ChessGame.Piece( name,  ChessGame.BLACK)
            self.__board[(1, j)] = ChessGame.Piece('pawn', ChessGame.WHITE)
            self.__board[(6, j)] = ChessGame.Piece('pawn', ChessGame.BLACK)

        self.__players = { ChessGame.WHITE: set(), ChessGame.BLACK: set() }
        for color in (ChessGame.BLACK, ChessGame.WHITE):
            self.__players[color] = {(x, y) for (x, y), piece in
                self.__board.iteritems() if piece.color == color }

        return

    def get_turn(self):
        """
        Get the current turn color
        """
        return self.__turn_info['turn']

    def get_player_piece_locs(self, mycolor):
        """
        Get piece locations for @mycolor
            - return None for invalid @mycolor
        """
        if mycolor not in (ChessGame.BLACK, ChessGame.WHITE):
            return None

        return self.__players[mycolor]

    def get_opponent_color(self, mycolor):
        """
        Get the opponent of @mycolor
        """
        if mycolor == ChessGame.BLACK:
            return ChessGame.WHITE
        elif mycolor == ChessGame.WHITE:
            return ChessGame.BLACK
        else:
            raise NotImplementedError()

    def get_piece_dict(self, mycolor):
        """
        Get piece locations and pieces for @mycolor
        """
        pieces = { (x, y) : self.get_piece(x, y) for (x, y) in
                   self.__players[mycolor] }
        if None in pieces.values():
            raise ValueError()
        return pieces

    def in_bounds(self, x, y):
        """
        Board locations must be strictly in [0, 8)
        """
        return x >= 0 and x < 8 and y >= 0 and y < 8

    def piece_at(self, x, y):
        """
        Determine if x,y is a piece
        """
        return ((x, y) in self.__board and
                isinstance((self.__board[(x, y)]), self.Piece))

    def get_piece(self, x, y):
        """
        Get piece at (x,y)
            - Use this function rather than accessing self.__board directly
        """
        if self.in_bounds(x, y) and self.piece_at(x, y):
            return self.__board[(x, y)]
        return None

    def is_enemy(self, x, y, mycolor):
        """
        Determine if piece at (x,y) is an enemy
        """
        piece = self.get_piece(x, y)
        if piece:
            return piece.color != mycolor
        return False

    def has_winner(self):
        """
        Determine if BLACK or WHITE has a win.
            - return None if no win
        """
        if self.color_check_mate(ChessGame.BLACK):
            return ChessGame.WHITE
        elif self.color_check_mate(ChessGame.WHITE):
            return ChessGame.BLACK
        else:
            return None

    def color_in_check(self, mycolor):
        """
        Determine whether mycolor is in check 
        """

        opponent = self.__players[self.get_opponent_color(mycolor)]

        x, y = None, None
        for (u, v) in self.__players[mycolor]:
            piece = self.get_piece(u, v)
            if not piece:
                raise ValueError()

            if self.get_piece(u, v).name == 'king':
                x, y = u, v
                break

        for (u, v) in opponent:
            if (x, y) in self._get_piece_moves(u, v):
                return True

        return False

    def color_check_mate(self, mycolor):
        """
        Determine whether mycolor is in check-mate 
        """

        if not self.color_in_check(mycolor):
            return False

        incheck = True
        for (x, y) in self.__players[mycolor]:
            moves = self._get_piece_moves(x, y)
            for to in moves:
                res, captured = self._make_move((x, y), to)
                if not self.color_in_check(mycolor):
                    incheck = False

                self._unmake_move(to, (x, y), captured)
                if not incheck:
                    return False

        return incheck

    def make_move(self, at, to):
        """
        Wrapper for internal _make_move that advances turn for ChessGame instances
        """

        made, captured = self._make_move(at, to)
        if made:
            self._advance_turn()
        return made, captured

    def _advance_turn(self):
        """
        Update move color; for internal use only
        """

        self.__turn_info['turn'] = ChessGame.BLACK if
            self.__turn_info['turn'] == ChessGame.WHITE else ChessGame.WHITE

    def _make_move(self, at, to):
        """
        Make a move for a piece at @at to @to
            - first verify that the move is valid
            - an invalid move is one that isn't on the board or one where there's no piece to move
            - next, see if we need to capture (remove from opponents pieces)
            - finally, replace whatever was at u,v with what as at board; report success

        return NONE (no move to be made), TRUE (move succeeded), FALSE (move puts opponent in check)
               along with CAPTURED to simplify code used by AI/GUI
        """

        x, y = at
        u, v = to

        piece = self.get_piece(x, y)
        if not piece:
            return None, None

        if piece.color != self.get_turn():
            return None, None

        if at == to or to not in self._get_piece_moves(x, y):
            return None, None

        color    = piece.color
        captured = None
        if self.is_enemy(u, v, color):
            captured = self.get_piece(u, v)

            del self.__board[(u, v)]
            self.__players[self.get_opponent_color(color)].remove((u, v))

        self.__board[(u, v)] = piece
        del self.__board[(x, y)]

        self.__players[piece.color].remove((x, y))
        self.__players[piece.color].add((u, v))

        ret = True
        if self.color_in_check(color):
            self._unmake_move(to, at, captured)
            ret = False

        self._check_integrity()
        return ret, captured

    def _unmake_move(self, at, to, captured=None):
        """
        Unmake a move for a piece moved to @at back to @to
            - if we're out of bounds, or there's no piece at u,v then we can't do anything 
            - captured is the result of a capture, or None if nothing was captured 
            - exchange whatever is at u,v with whatever is at x,y
        """

        u, v = at
        x, y = to

        if not self.in_bounds(x, y) or not self.in_bounds(u, v):
            return False

        piece = self.get_piece(u, v)
        if not piece:
            raise ValueError()

        if isinstance(captured, ChessGame.Piece):
            opponent = self.get_opponent_color(piece.color)
            self.__board[(u, v)] = captured
            self.__players[opponent].add((u, v))
        else:
            del self.__board[(u, v)]

        self.__board[(x, y)] = piece
        self.__players[piece.color].add((x, y))
        self.__players[piece.color].remove((u, v))
        self._check_integrity()
        return True

    def _check_integrity(self):
        """
        Check the integrity of the board
            - make sure that each piece in a players piece set is in the board
            - the union of the piece sets must cover the board exactly 
        """

        count = 0
        for (x, y) in self.__players[ChessGame.BLACK].union(
            self.__players[ChessGame.WHITE]):
            assert (x, y) in self.__board
            count += 1

        assert count == len(self.__board)


    def get_moves(self, x, y):
        """
        Top-level function that should be used ONLY by GUI/AI (do not use with ChessGame.py)
            - gets moves that won't the moving player in check
            - should not be used in ChessGame.py..._make_move makes calls to _get_piece_moves
              and we could induce infinite recursion by replacing that call with a call to
              get_moves

        TODO: think about making this a static function, accessible with ChessGame.get_piece_moves(boards, x, y)
        """

        if not self.piece_at(x, y):
            return set()

        moves = self._get_piece_moves(x, y)
        legal = set(moves)
        at = x, y
        for to in moves:
            res, captured = self._make_move(at, to)
            if not res:
                legal.remove(to)
            else:
                self._unmake_move(to, at, captured)

        self._check_integrity()
        return legal

    def _get_moves_indirection(self, x, y, direc, moves=[]):
        """
        Get sequential moves in a given direction recursively
            - handle attack moves with the move function 
        """

        compass = {
            'up'    : (x-1, y),
            'down'  : (x+1, y),
            'left'  : (x, y-1),
            'right' : (x, y+1),
            'd1'    : (x-1, y+1),
            'd2'    : (x+1, y-1),
            'd3'    : (x+1, y+1),
            'd4'    : (x-1, y-1)
        }

        u, v = compass[direc]
        if not self.in_bounds(u, v):
            return moves

        if self.piece_at(u, v):
            return [(u, v)] + moves
        return [(u, v)] + self._get_moves_indirection(u, v, direc, moves)


    def _get_piece_moves(self, x, y):
        """
        Get moves for a piece at location @x, @y. Should NOT be called by GUI/AI
            - @x denotes the row on the board. Increases in x imply downward movement
            - @y denotes the column on the board
        """

        piece = self.get_piece(x, y)
        moves = []

        if not piece:
            return moves

        if piece.name == 'rook' or piece.name == 'queen':
            direcs = ['up', 'down', 'left', 'right']
            moves = [self._get_moves_indirection(x, y, direc) for direc in
                     direcs]

        elif piece.name == 'bishop' or piece.name == 'queen':
            direcs = ['d1', 'd2', 'd3', 'd4']
            for direc in direcs:
                moves +=  self._get_moves_indirection(x, y, direc)

        elif piece.name == 'king':
            moves = [(x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1),
                     (x, y+1), (x+1, y-1), (x+1, y), (x+1, y+1)]

        elif piece.name == 'knight':
            moves = [(x-1, y-2), (x-2, y-1), (x-2, y+1), (x-1, y+2),
                     (x+1, y+2), (x+2, y+1), (x+1, y-2), (x+2, y-1)]

        elif piece.name == 'pawn':
            if piece.color == ChessGame.BLACK:
                moves = [(x-1, y), (x-1, y-1), (x-1, y+1)]
            else:
                moves = [(x+1, y), (x+1, y-1), (x+1, y+1)]

            tmp = list(moves)
            for u, v in tmp:
                if v != y and not self.is_enemy(u, v, piece.color):
                    moves.remove((u, v))

                if v == y and self.is_enemy(u, v, piece.color):
                    moves.remove((u, v))

        mycolor = piece.color
        valid   = set()
        for (u, v) in moves:
            if not self.in_bounds(u, v):
                continue

            if not self.get_piece(u, v):  # board is blank
                valid.add((u, v))

            if self.is_enemy(u, v, mycolor):
                valid.add((u, v))

        return valid

