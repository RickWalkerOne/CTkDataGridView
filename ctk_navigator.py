from tkinter import StringVar, IntVar
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry
from tkinter import messagebox
from typing import Callable, Optional, Any


class CTkNavigator(CTkFrame):
    def __init__(self, master, last_page: int, current_var: IntVar):
        super().__init__(master)
        self._callbacks = []

        self._current_page_intvar = current_var

        self._last_page_var = StringVar(value=str(last_page))
        self._begin_page_var = StringVar(value=str(0))
        self._current_page_var = StringVar(value=str(current_var.get()))

        self._begin_label = CTkLabel(self, textvariable=self._begin_page_var, justify='center')
        self._begin_button = CTkButton(self, text='|<', command=self.goto_beginning)
        self._previous_button = CTkButton(self, text='<', command=self.goto_previous)
        self._entry = CTkEntry(self, textvariable=self._current_page_var, justify='center')
        self._next_button = CTkButton(self, text='>', command=self.goto_next)
        self._end_button = CTkButton(self, text='>|', command=self.goto_end)
        self._end_label = CTkLabel(self, textvariable=self._last_page_var, justify='center')

        self._begin_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self._begin_button.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self._previous_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        self._entry.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')
        self._next_button.grid(row=0, column=4, padx=10, pady=10, sticky='nsew')
        self._end_button.grid(row=0, column=5, padx=10, pady=10, sticky='nsew')
        self._end_label.grid(row=0, column=6, padx=10, pady=10, sticky='nsew')
        for x in range(7):
            self.columnconfigure(x, weight=1)

        self._entry.bind('<Return>', self.goto_page)

    def config(self,
               last_page: Optional[int] = None,
               current_var: Optional[IntVar] = None,
               current: Optional[int] = None,
               begin_page: Optional[int] = None):
        if last_page is not None:
            self._last_page_var.set(value=str(last_page))
        if begin_page is not None:
            self._begin_page_var.set(value=str(begin_page))
        if current_var is not None:
            self._current_page_intvar = current_var
        if current is not None:
            self._current_page_var.set(value=str(current))

    def goto_beginning(self):
        self._current_page_var.set(self._begin_page_var.get())
        self._current_page_intvar.set(int(self._begin_page_var.get()))
        self._refresh()

    def goto_previous(self):
        current_page = int(self._current_page_var.get())
        if int(self._begin_page_var.get()) < current_page:
            self._current_page_var.set(str(current_page - 1))
            self._current_page_intvar.set(current_page - 1)
            self._refresh()

    def goto_next(self):
        current_page = int(self._current_page_var.get())
        if current_page < int(self._last_page_var.get()):
            self._current_page_var.set(str(current_page + 1))
            self._current_page_intvar.set(current_page + 1)
            self._refresh()

    def goto_end(self):
        self._current_page_var.set(self._last_page_var.get())
        self._current_page_intvar.set(int(self._last_page_var.get()))
        self._refresh()

    def goto_page(self, event=None):
        try:
            page = int(self._current_page_var.get())
            if page < int(self._begin_page_var.get()) or page > int(self._last_page_var.get()):
                raise ValueError
            self._current_page_intvar.set(int(self._current_page_var.get()))
            self._refresh()
        except ValueError:
            messagebox.showerror('Invalid Page', 'Please enter a valid page number.')

    def _refresh(self):
        for func in self._callbacks:
            func()

    def get_current(self):
        return int(self._current_page_var.get())

    def trace(self, func: Callable[[Any], Any], add: Optional[bool] = False):
        if add:
            self._callbacks.append(func)
        else:
            self._callbacks = [func]
