import sys
import tkinter as tk

class MsgBox:
    def __init__(self, title, message, style):
        self.title = title
        self.message = message
        self.style = style
        
        self.gui = None
        self.color_scheme = ['white', 'black', 'grey']
        self.size = '200x200+200+200'

        if style == 'alert':
            self.color_scheme = ['#af1111', '#0e0e0e', '#dfdfdf']
        
    def show(self):
        # create gui
        self.gui = tk.Tk()
        self.gui.geometry(self.size)
        self.gui.configure(background=self.color_scheme[0])
        self.gui.resizable(width=False, height=False)

        # set text and message
        self.gui.title(self.title)
        tk.Label(self.gui, text=self.message, fg=self.color_scheme[1], bg=self.color_scheme[2], wraplength=180).pack(fill=tk.BOTH, pady=10, padx=10)
        tk.Button(self.gui, text='close', command=self._close, fg=self.color_scheme[1], bg=self.color_scheme[2]).pack(side=tk.BOTTOM, fill=tk.BOTH, pady=10, padx=10)

        # bind esc to exit
        def keydown(e):
            if e.keycode == 27:
                # ESC
                self._close()
        self.gui.bind("<KeyPress>", keydown)

        # show/start gui
        self.gui.attributes("-topmost", True)
        self.gui.mainloop()

    def _close(self):
        self.gui.destroy()
        del self

if __name__ == '__main__':
    ''' Usage in commandline

    >>> python messagebox.py -title 'title' -message 'message' -style 'style'
    >>> python messagebox.py -t 'title' -m 'message' -s 'style'

    >>> python messagebox.py -t 'wachtog wraning' -m 'messga\nmessga\nmessga\n\nhanldung erfrodlich' -s 'alert'
    '''

    # parameters dict
    params = {
        't': '', # title
        'm': '', # message
        's': ''  # style
    }

    # parse command line arguments
    args = sys.argv
    del args[0]

    l = len(args)
    if l:
        for i in range(l):
            if '-' in args[i] and len(args[i]) > 1:
                try:
                    params[args[i][1]] = args[i+1]
                except IndexError:
                    raise ValueError('Inline parameter %s is not defined.'% (args[i]))
    
    b = MsgBox(params['t'], params['m'], params['s'])
    b.show()
