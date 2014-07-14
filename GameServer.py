from ChessGUI  import *
from socket    import *
from threading import *
from ast       import literal_eval

class GameServer:
    """
    Class to host chess game
        - Should be not be called directly
        - main.py should be the only class making use of GameServer.py
    """
    
    def __init__(self, master, host, port):
        """
        Initialize basic (bind -> listen -> accept -> send, recv -> close) socket server
            - queue will be used to transfer moves accross threads
            - credit http://joyrex.spc.uchicago.edu/bookshelves/python/cookbook/pythoncook-CHP-9-SECT-7.html
              with tk thread management recipe
        """
        self.master = master
        self.queue  = Queue.Queue()
        self.game   = ChessGui(HumanPlayer('ben'),HumanPlayer('joe'), self.master, self, self.queue)
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((host, port))

        self.server.listen(2)
        self.conn      = None 
        self.listener  = Thread(target = self._recv_thread)
        self.listener.start()
        self._update_game()

    def _update_game(self):
        """
        ChessGUI has reference to queue. Will update every 200ms, if a move has been received
        and needs to be made
        """
        self.game.process_incoming()
        self.master.after(200, self._update_game)

    def _recv_thread(self):
        """
        Listen to incoming instructions from second player. Put on second thread to allow concurrent execution
            - incoming message must be in the form ((x,y), (u,v))
        """
        
        while True:
            if not self.conn: 
                self.conn, address  = self.server.accept()
                
            data  = self.conn.recv(1024)
            if data:
                at, to = literal_eval(data)
                self.queue.put((at, to))

        return

    def send_move(self, at, to):
        """
        Will be executed by ChessGUI. Note that ChessGUI verifies that we have a move from @at to @to
            - outgoing message must be in the form ((x,y), (u,v))
        """
        if self.conn:
            message = '(' + str(at) + ',' + str(to) + ')'
            print message
            self.conn.send(message)

    def close(self):
        self.server.close()

def run(host='', port=8000):
    root   = Tk()
    server = GameServer(root, host, port)
    root.mainloop()
