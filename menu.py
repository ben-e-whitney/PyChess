import urllib
import GameServer

from ChessGUI            import *
from smtplib             import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText      import MIMEText
from email               import Encoders
from email.MIMEBase      import MIMEBase

class EmailForm:
    def __init__(self, master, app):
        self.root = master
        self.app  = app
        self._init_smtp()
        self._refresh_form()

    def _init_smtp(self):
        self.server = SMTP('smtp.gmail.com:587')
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        
    def _on_okay(self):
        username = self.username.get()
        password = self.password.get()
        self.server.login(username, password)

        msg = MIMEMultipart()
        msg['Subject'] = 'PyChess Invitation!'
        msg['From']    = username
        msg['To']      = to
        part  = MIMEBase('application', 'octet-stream')
        text  = 'To play, download attached client and put in game source file directory. Run with 32 bit python2.7\n\n'
        text += '\tHOST = ' + self.external_ip + '\tPORT = ' + self.port_number.get()
        part.set_payload(text)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="GameClient.py"')
        msg.attach(part)
        msg.attach(MIMEText(text, 'plain'))
        self.server.sendmail(username, to, msg.as_string())
        self.server.quit()
        
        self.app.root.destroy()
        GameServer.run(self.external_ip, int(self.port_number.get()))

    def _on_cancel(self):
        server.quit()
        self.root.destroy()
        return

    def _refresh_ui(self):
        """
        TODO: add error checking for username, to_email. emails must contain @ symbol
              Also must include port/host...use this rather than hardcoding.
        """
        self.root.title('Invite by e-mail')
        Label(self.root, text='To').grid(row=0, sticky = W, pady = (20, 0), padx = (50,0))
        Label(self.root, text='Gmail address').grid(row = 2, sticky = W, padx = (50,0))
        Label(self.root, text='Password').grid(row=3, sticky = W, padx = (50,0))
        Label(self.root, text='PORT').grid(row=1, column = 1, pady = (0, 30))
        Label(self.root, text='HOST').grid(row=1, column = 3, pady = (0, 30))

        e1 = Entry(self.root, textvariable = self.to_address, width = 28)
        e4 = Entry(self.root, width = 5, textvariable = self.port_number)
        e5 = Entry(self.root, width = 5)
        e2 = Entry(self.root, textvariable = self.username, width = 28)
        e3 = Entry(self.root, textvariable = self.password, show="*", width = 28)
        e5.insert(0, self.external_ip)
        e5.config(state = 'readonly')
        
        e1.grid(row=0, column=1, sticky = E, columnspan = 4, pady = (20, 0), padx = (0, 50))
        e4.grid(row=1, column=2, sticky = W+E, pady = (0, 30))
        e5.grid(row=1, column=4, sticky = W+E, padx = (0, 50), pady = (0,30)) 
        e2.grid(row=2, column=1, sticky = E, columnspan = 4, padx = (0, 50))
        e3.grid(row=3, column=1, sticky = E, columnspan = 4, padx = (0, 50))
        
        ok_btn     = Button(self.root, text = 'Send', command = self._on_okay, width = 5).grid(row = 5, column = 2, columnspan = 2, sticky = E, pady = (20,20))
        cancel_btn = Button(self.root, text = 'Cancel').grid(row = 5, sticky  =  E+W, column = 4, columnspan = 2, padx = (0,50), pady = (20,20))
        
    def _refresh_form(self):
        self.to_address   = StringVar(self.root)
        self.username     = StringVar(self.root)
        self.password     = StringVar(self.root)
        self.message      = StringVar(self.root)
        self.port_number  = StringVar(self.root)
        self.external_ip  = urllib.urlopen('http://myip.dnsdynamic.org/').read()
        self._refresh_ui()

class ChessMenu:
    def __init__(self):
        self.root = Tk()
        self._refresh_form()
        
    def mainloop(self):
        self.root.update()
        self.root.mainloop()
    
    def _on_play(self):
        self.root.destroy()
        
    def _on_help(self):
        return

    def _on_mail_click(self):
        self.child = Toplevel(self.root)
        self.app   = EmailForm(self.child, self)
        self.child.grab_set()
        return

    def _refresh_ui(self):
        self.root.title('PyChess')
        Label(self.root, text='Name').grid(row=0,  sticky=W, pady = (50,0), padx = (50,0))
        Label(self.root, text='Opponent').grid(row=2, sticky=W, padx = (50,0))
        
        mail_btn = Button(text = 'Invite', master = self.root, command = self._on_mail_click)
        play_btn = Button(text = 'Play',   master = self.root, command = self._on_play)
        
        e1 = Entry(self.root, textvariable = self.name)
        e2 = OptionMenu(self.root, self.opponent, 'AI', 'Human', '')
        e2.config(width = 3)
        e1.grid(row=0, column=1, sticky = W, columnspan = 2, pady = (50,0), padx = (0,50))
        e2.grid(row=2, column=1, sticky = W+E, padx = (0,1))
        mail_btn.grid(row = 2, column = 2, sticky = E+W, padx = (0,50))
        play_btn.grid(row = 3, column = 0, sticky=E+W, columnspan = 3, pady = (25,20), padx = (50,50))
        
    def _refresh_form(self):
        self.name     = StringVar(self.root)
        self.opponent = StringVar(self.root)
        self._refresh_ui()

       
def main():
    ChessMenu().mainloop()



if __name__ == '__main__':
    main()  
