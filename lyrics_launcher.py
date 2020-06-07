import tkinter
import webbrowser
from tkinter import messagebox


class Launcher:
    TITLE = 'Lyrics Launcher'

    def __init__(self, interrupt_main=False, clear_lyrics_cache=None):
        self.interrupt_main = interrupt_main
        self.clear_lyrics_cache = clear_lyrics_cache
        self.create()

    def on_quit(self):
        answer = messagebox.askyesno(self.TITLE,
                                     'Are you sure you want to shut down Lyrics Renderer?')
        if answer:
            self.root.destroy()
            if self.interrupt_main:
                import _thread
                _thread.interrupt_main()

    def on_open_controller(self):
        webbrowser.open('http://127.0.0.1:59742/controller')

    def on_open_renderer(self):
        webbrowser.open_new('http://127.0.0.1:59742/')

    def create(self):
        self.root = tkinter.Tk()
        self.root.title(self.TITLE)
        self.root.protocol('WM_DELETE_WINDOW', self.on_quit)
        self.framel = tkinter.Frame(self.root)
        self.framel.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
        self.framer = tkinter.Frame(self.root)
        self.framer.pack(side=tkinter.RIGHT, expand=tkinter.TRUE)
        tkinter.Button(self.framel,
                       text='Open Control Interface',
                       command=self.on_open_controller).pack()
        tkinter.Button(self.framel,
                       text='Open Renderer',
                       command=self.on_open_renderer).pack()
        tkinter.Button(self.framel,
                       text='Quit',
                       command=self.on_quit).pack()
        if self.clear_lyrics_cache is not None:
            tkinter.Button(self.framer,
                        text='Clear Lyric Cache',
                        command=self.clear_lyrics_cache).pack()


    def run(self):
        self.root.mainloop()


def run_launcher(*args, **kwargs):
    launcher = Launcher(*args, **kwargs)
    launcher.run()


if __name__ == '__main__':
    import lyrics
    lyrics.main(True)
