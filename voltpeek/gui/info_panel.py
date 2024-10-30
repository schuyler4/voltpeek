import tkinter as tk

from voltpeek.commands import COMMAND_DOCS

class InfoPanel:
    BACKGROUND_COLOR: str = 'black'
    BORDER_COLOR: str = 'white'
    TEXT_COLOR: str = 'white'
    BORDER_THICKNESS: int = 2

    def __init__(self, master: tk.Tk) -> None:
        self._visible: bool = False
        self.master: tk.Tk = master
        self.frame: tk.Frame = tk.Frame(self.master, bg=self.BACKGROUND_COLOR, 
                                        highlightbackground=self.BORDER_COLOR,
                                        highlightthickness=self.BORDER_THICKNESS)
        self.info_strings: list[tk.StringVar] = []
        for key in COMMAND_DOCS:
            string_var = tk.StringVar()
            string_var.set(key + ': ' + COMMAND_DOCS[key])
            self.info_strings.append(string_var)

    def __call__(self) -> None:
        for i in range(0, len(COMMAND_DOCS)):
            vertical_label: tk.Label = tk.Label(self.frame, 
                                                textvariable=self.info_strings[i],
                                                bg=self.BACKGROUND_COLOR,
                                                fg=self.TEXT_COLOR, 
                                                justify='left')
            vertical_label.pack()

    def show(self) -> None:
        self._visible = True
        self.frame.grid(sticky=tk.N, row=2, column=0)

    def hide(self) -> None:
        self._visible = False
        self.frame.grid_forget()

    @property
    def visible(self) -> bool: return self._visible
