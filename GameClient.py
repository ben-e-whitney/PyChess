from ChessGUI  import *
from socket    import *
from threading import *
from ast       import literal_eval

class GameClient:
    """
    Class to connect with other player hosting game
        - Must always reside in same directory as source files
        - Should be called directly, not by main.py or any other class 
    """

    def __init__(self, master, name=None, color=None):
        """
        Use @master Tk reference rather than creating a new one
            - Neither @name nor @color are currently being used
            - ChessGUI will need to process incoming moves in the order they are received; 
              queue should never have more than one element
        """
        self.root  = master
        self.queue = Queue.Queue()
        self._refresh_form()

    def _on_play(self):
        """
        Connect the client after specifying the PORT and HOST of the server
            - HOST should be external ip of the server; port should be a 4 digit port
            - Use localhost (HOST = '') and port 8000 for testing
            - listening must be done on separate thread 
        """
        self.game   = ChessGui(None, HumanPlayer('joe'), self.root, self,
                               self.queue)
        self.client = socket(AF_INET, SOCK_STREAM)
        host, port  = self.host.get(), int(self.port.get())
        self.client.connect((host, port)) # temp for testing

        self.listener = Thread(target=self._recv_thread)
        self.listener.daemon = True   # end if main thread quits
        self.listener.start()
        self._update_game()

    def _refresh_ui(self):
        """
        TODO: require that host and port be specified 
        """
        self.root.title('Connect to Server')
        Label(self.root, text='HOST').grid(row=0, column=0, padx=(50, 0),
                                           pady=(50, 0))
        Label(self.root, text='PORT').grid(row=0, column=2, pady=(50, 0))

        e1 = Entry(self.root, textvariable=self.host, width=10)
        e2 = Entry(self.root, textvariable=self.port, width=10)
        play_btn = Button(text='Play', master=self.root, command=self._on_play)

        e1.grid(row=0, column=1, sticky=W, pady=(50, 0))
        e2.grid(row=0, column=3, padx=(0, 50), sticky=W, pady=(50, 0))
        play_btn.grid(row=1, column=0, sticky=E+W, columnspan=4, padx=(50, 50),
                      pady=(10, 50))

        return

    def _refresh_form(self):
        """
        Reset host and port variables; refresh ui display
        """
        self.host = StringVar(self.root)
        self.port = StringVar(self.root)
        self._refresh_ui()
        return 

    def _update_game(self):
        """
        ChessGUI has reference to queue. Will update every 200ms, if a move has been received
        and needs to be made
        """
        self.game.process_incoming()
        self.root.after(200, self._update_game)  # schedule recurring update

    def _recv_thread(self):
        """
        Listen to incoming instructions from second player. Put on second thread to allow concurrent execution
            - incoming message must be in the form ((x,y), (u,v))
        """
        while True:
            try:
                reply  = self.client.recv(1024)
                if reply:
                    print 'received something on client'
                    at, to = literal_eval(reply)
                    self.queue.put((at, to))

            except:
                self.client.close()

    def send_move(self, at, to):
        """
        Will be executed by ChessGUI. Note that ChessGUI verifies that we have a move from @at to @to
            - outgoing message must be in the form ((x,y), (u,v))
        """
        message = '({at},{to})'.format(at=at, to=to)
        self.client.send(message)

    def close(self):
        self.client.close()


def main():
    root   = Tk()
    client = GameClient(root)
    root.mainloop()


if __name__ == '__main__':
    main()
