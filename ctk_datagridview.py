from tkinter import IntVar, StringVar, DISABLED, NORMAL
from customtkinter import CTkFrame, CTk
from CTkMessagebox import CTkMessagebox

from datasource import DataSourceVar
from ctk_navigator import CTkNavigator
from ctk_label import CTkLabel
from ctk_maskedentry import CTkMaskedEntry
from mask import Mask
from column import Column
from typing import List


class CTkDataGridView(CTkFrame):
    def __init__(self, master, data: DataSourceVar,
                 max_rows: int, columns: List[Column],
                 read_only=False,
                 headers_bg='#000000', headers_fg='#ffffff',
                 even_row_bg='#ffffff', even_row_fg='#000000',
                 odd_row_bg='#eeeeee', odd_row_fg='#000000',
                 true_string='True', false_string='False'):
        super().__init__(master)
        self._columns = columns
        self.master = master
        self._max_rows = max_rows
        self._read_only = read_only
        self._data = data
        self._data.callable(self.update, 'all', True)
        self._sorted_data = data.get()
        self._page = IntVar(self, 0)
        self._num_rows = len(data)
        self._num_cols = len(data[0])
        self._true_string = true_string
        self._false_string = false_string
        self._cells = []
        self._head = CTkFrame(self)
        self._body = CTkFrame(self)
        self._nav = CTkNavigator(self, self._round(self._num_rows / self._max_rows), self._page)
        self._nav.trace(self.update, True)
        self._head.grid(row=0, column=0, sticky='nswe')
        self._body.grid(row=1, column=0, sticky='nswe')
        self._nav.grid(row=2, column=0, sticky='nswe')

        # style variables:
        self._headers_bg = headers_bg
        self._headers_fg = headers_fg
        self._even_row_bg = even_row_bg
        self._even_row_fg = even_row_fg
        self._odd_row_bg = odd_row_bg
        self._odd_row_fg = odd_row_fg
        self._font_family = 'Arial'
        self._font_size = 10
        self._font_weight = 'normal'
        self._border_width = 1
        self._border_color = 'black'

        self._sort_order = None
        # Set the row and column weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=self._max_rows)
        self.rowconfigure(2, weight=1)
        self._head.rowconfigure(0, weight=1)
        for i in range(self._num_cols):
            self._head.columnconfigure(i, weight=2)
            self._body.columnconfigure(i, weight=2)
        for i in range(self._max_rows):
            self._body.rowconfigure(i, weight=1)

        # Create the table header
        for col, key in enumerate(self._data[0].keys()):
            label = CTkMaskedEntry(self._head,
                                   textvariable=StringVar(value=key),
                                   font=(self._font_family, self._font_size, self._font_weight),
                                   fg_color=self._headers_bg,
                                   text_color=self._headers_fg,
                                   border_width=self._border_width,
                                   border_color=self._border_color,
                                   corner_radius=0,
                                   justify='center',
                                   state=DISABLED)
            label.grid(row=0, column=col, sticky='nswe')
            label.bind('<Button-1>', lambda event, col_=col: self.sort_column(col_))

        self._create_table()

    def _create_table(self):
        self._cells = []
        # Create the table _cells
        for grid_row, row in enumerate(list(range(self._max_rows * self._page.get(), self._max_rows * (self._page.get() + 1)))):
            _test_ = row < self._num_rows
            row_cells = []
            is_even = grid_row % 2 == 0
            for col in range(self._num_cols):
                cell_value = StringVar(
                    master=self._body,
                    value=self._revise_values(self._data[row][list(self._data[row].keys())[col]]) if _test_ else None)
                cell_entry = CTkMaskedEntry(self._body, textvariable=cell_value, justify='center',
                                            font=(self._font_family, self._font_size, self._font_weight),
                                            fg_color=self._even_row_bg if is_even else self._odd_row_bg,
                                            text_color=self._even_row_fg if is_even else self._odd_row_fg,
                                            corner_radius=0,
                                            border_width=self._border_width,
                                            border_color=self._border_color,
                                            state=DISABLED if self._read_only or not _test_ else NORMAL)
                cell_entry.grid(row=grid_row, column=col, sticky='nswe')
                cell_entry.bind('<Return>', lambda event, row_=grid_row, col_=col: self.save_cell(event, row_, col_))
                cell_entry.bind('<Escape>', lambda event, row_=grid_row, col_=col: self.cancel_edit(event, row_, col_))
                row_cells.append(cell_value)
            self._cells.append(row_cells)

    def _revise_values(self, value, reverse=False, none_type=False):
        if not reverse:
            if isinstance(value, bool):
                return self._true_string if value else self._false_string
            if value is None:
                return None if none_type else ''
            return value
        else:
            if value is None or value.strip() == '':
                return None
            elif isinstance(value, str) and value.strip().lower() == self._true_string.lower():
                return True
            elif isinstance(value, str) and value.strip().lower() == self._false_string.lower():
                return False
            else:
                try:
                    return int(value)
                except:
                    return value

    def _get_row(self, grid: int) -> int:
        row = grid
        for page in range(self._page.get()):
            row += self._max_rows
        return row

    def save_cell(self, event, grid: int, col: int):
        row = self._get_row(grid)
        value = self._revise_values(self._cells[grid][col].get(), True)
        __value = self._data[row][self._columns[col].cget('name')]
        if type(value) != type(__value):
            CTkMessagebox(title="Warning!",
                          message=f"Incorrect type! Please insert a valid value.\n\nCOD: <{type(value)}{type(__value)}>",
                          icon='warning', option_1="Cancel")
            return
        self._data[row][list(self._data[row].keys())[col]] = value
        self.master.focus()

    def cancel_edit(self, event, grid: int, col: int):
        row = self._get_row(grid)
        value = self._data[row][list(self._data[row].keys())[col]]
        self._cells[grid][col].set(self._revise_values(value))
        self.master.focus()

    def clear(self) -> None:
        for row in range(self._max_rows):
            for col in range(self._num_cols):
                cell_value = self._cells[row][col]
                cell_value.set('')
        if not self._read_only:
            __widget = self._body.grid_slaves()
            for widget in __widget:
                if isinstance(widget, CTkMaskedEntry):
                    widget.configure(state=DISABLED)

    @staticmethod
    def _round(decimal: float):
        string = str(decimal)
        sub = string[string.index('.') + 1:]
        integer = int(sub)
        if integer != 0:
            return int(string[:string.index('.')]) + 1
        else:
            return int(string[:string.index('.')])

    def _return_cells(self) -> List[CTkMaskedEntry]:
        __widget = self._body.grid_slaves()
        __entry_list = []
        for widget in __widget:
            if isinstance(widget, CTkMaskedEntry):
                __entry_list.append(widget)
        __entry_list.reverse()
        return __entry_list

    def update(self, *args, **kwargs) -> None:
        if 'page' in kwargs:
            self._page.set(kwargs.pop('page'))
        self._num_rows = len(self._data)
        self.clear()
        entry_list = self._return_cells()
        for grid_row, row in enumerate(list(range(self._max_rows * self._page.get(), self._max_rows * (self._page.get() + 1)))):
            _test_ = row < self._num_rows
            for col in range(self._num_cols):
                this_entry = entry_list[grid_row * self._num_cols + col]
                this_entry.configure(state=NORMAL)
                self._cells[grid_row][col].set(
                    self._revise_values(self._sorted_data[row][list(self._sorted_data[row].keys())[col]]) if _test_ else '')
                this_entry.configure(state=DISABLED if self._read_only or not _test_ else NORMAL)

    def sort_column(self, col):
        if self._sort_order == col:
            self._sort_order = None
            reverse = True
        else:
            self._sort_order = col
            reverse = False
        # Sort the _data by the selected column
        self._sorted_data = sorted(
            self._data,
            key=lambda row_:
                (self._revise_values(row_[self._columns[col].cget('name')], none_type=True) is not None,
                 self._revise_values(row_[self._columns[col].cget('name')], none_type=True)),
            reverse=not reverse
        )

        # Re-create the cell widgets with the sorted _data
        for row, row_data in enumerate(self._sorted_data):
            if row == self._max_rows:
                break
            for col, key in enumerate(self._columns):
                self._cells[row][col].set(self._revise_values(row_data[key.cget('name')]))

    def cget(self, key: str):
        return getattr(self, '_' + key)

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            # get the current value of the variable
            current_value = getattr(self, key)
            # check if the new value is different from the current value
            if current_value != value:
                # update the variable with the new value
                setattr(self, key, value)

                # update the table widget based on the variable that was changed
                if key == '_read_only':
                    # update the state of the Entry widgets
                    __widgets = self._return_cells()
                    for index, cell in enumerate(__widgets):
                        __row = index // self._num_cols
                        __col = index % self._num_cols
                        if value:
                            cell.config(state='readonly')
                            cell.unbind('<Return>')
                            cell.unbind('<Escape>')
                        else:
                            cell.config(state='normal')
                            cell.bind('<Return>', lambda event, row=__row, col=__col: self.save_cell(event, row, col))
                            cell.bind('<Escape>', lambda event, row=__row, col=__col: self.cancel_edit(event, row, col))
                elif key == '_data':
                    # update the number of rows and columns
                    self._num_rows = len(value)
                    self._num_cols = len(self._columns)
                    # update the table widget with the new data
                    self.update()
                elif key == '_headers':
                    # update the number of rows and columns
                    self._num_rows = len(self._data)
                    self._num_cols = len(value)
                    # update the table widget with the new headers
                    self.update()
                elif key == '_sort_order':
                    self._sort_order = value
                    # sort the data based on the new sort order
                    self.sort_column(self._sort_order)

    def _style_font(self, family=None, size=None, weight=None):
        if family:
            self._font_family = family
        if size:
            self._font_size = size
        if weight:
            self._font_weight = weight
        __widgets = self._return_cells()
        for cell in __widgets:
            cell.configure(font=(self._font_family, self._font_size, self._font_weight))

    def _style_border(self, width=None, color=None):
        if width:
            self._border_width = width
        if color:
            self._border_color = color
        __widgets = self._return_cells()
        for cell in __widgets:
            cell.configure(highlightthickness=self._border_width, highlightcolor=self._border_color)

    def style(self, **kwargs):
        for key, value in kwargs:
            if 'headers_bg' in key:
                self._headers_bg = value
            if 'headers_fg' in key:
                self._headers_fg = value
            if 'even_bg' in key:
                self._even_row_bg = value
            if 'even_fg' in key:
                self._even_row_fg = value
            if 'odd_bg' in key:
                self._odd_row_bg = value
            if 'odd_fg' in key:
                self._odd_row_fg = value
            if 'font' in key:
                self._style_font(**value)
            if 'border' in key:
                self._style_border(**value)

    def _update_style_config(self):
        __headers = self._head.grid_slaves()
        for cell in __headers:
            if isinstance(cell, CTkLabel):
                cell.configure(bg=self._headers_bg, fg=self._headers_fg)

        __widgets = self._return_cells()
        for index, cell in enumerate(__widgets):
            row = index // self._num_cols
            if row % 2 == 0:
                cell.configure(bg=self._even_row_bg, fg=self._even_row_bg)
            else:
                cell.configure(bg=self._odd_row_bg, fg=self._odd_row_bg)

    def index(self, row):
        # Get all the widgets in the grid
        slaves = self._head.grid_slaves() + self._body.grid_slaves()
        slaves.reverse()

        # Loop over all the widgets in the grid
        __will_return = []
        for i, widget in enumerate(slaves):
            j = i
            while j >= len(self._columns):
                j -= len(self._columns)
            # Check if the widget is an Entry widget and has the same values as the given row
            if isinstance(widget, CTkMaskedEntry) and self._revise_values(widget.get(), True) == row[self._columns[j]]:
                __will_return.append(True)
            else:
                __will_return.append(False)
            if len(__will_return) == len(self._columns):
                if False not in __will_return:
                    return (i // len(self._columns)) - 1  # Return the index of the row if it exists
                else:
                    __will_return.clear()

        # Return -1 if the row doesn't exist
        return -1

    def find(self, index):
        if not 0 <= index < self._num_rows:
            return None
        values = {}
        for i, column in enumerate(self._columns):
            cell = self._body.grid_slaves(row=index, column=i)[0]
            if isinstance(cell, CTkMaskedEntry):
                values[column.cget('name')] = self._revise_values(cell.get(), True)
        return values


# Example usage
if __name__ == '__main__':
    root = CTk()
    root.title('Data Grid View')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    __data = DataSourceVar(value=[{'name': 'example', 'age': 15, 'marriage': False}, {'name': 'Fulan', 'age': None, 'marriage': True}])
    table = CTkDataGridView(root, __data, 10)
    table.grid(row=0, column=0, sticky='nsew')
    mynewrow = {'name': 'new name', 'age': 0, 'marriage': True}
    for x in range(10):
        __data.append(mynewrow)
    __index = table.index(mynewrow)

    root.mainloop()
