from tkinter import Variable, Tk
from typing import Literal, Callable, Any


class DataSourceVar(Variable):
    def __init__(self, master=None, value=None, name=None):
        super().__init__(master, value, name)
        self._value = value if value is not None else []
        self._callbacks = {'insert': [], 'remove': [], 'append': [],
                           'pop': [], 'sort': [], 'all': [],
                           'reverse': [], 'clear': []}

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def append(self, item):
        self._value.append(item)
        for func in self._callbacks['append']:
            func(item)

        for func in self._callbacks['all']:
            func(item)

    def remove(self, item):
        self._value.remove(item)
        for func in self._callbacks['remove']:
            func(item)

        for func in self._callbacks['all']:
            func(item)

    def insert(self, index, item):
        self._value.insert(index, item)
        for func in self._callbacks['insert']:
            func(item)

        for func in self._callbacks['all']:
            func(item)

    def pop(self, index):
        self._value.pop(index)
        for func in self._callbacks['pop']:
            func(index)

        for func in self._callbacks['all']:
            func(index)

    def sort(self, key: ... = None, reverse: bool = False):
        self._value.sort(key=key, reverse=reverse)
        for func in self._callbacks['sort']:
            func(key, reverse)

        for func in self._callbacks['all']:
            func(key, reverse)

    def reverse(self):
        self._value.reverse()
        for func in self._callbacks['reverse']:
            func()

        for func in self._callbacks['all']:
            func()

    def clear(self):
        self._value.clear()
        for func in self._callbacks['clear']:
            func()

        for func in self._callbacks['all']:
            func()

    def count(self, value) -> int:
        return self._value.count(value)

    def index(self, value, start, stop) -> int:
        return self._value.index(value, start, stop)

    def callable(self,
                 func: Callable[[Any], Any],
                 method: Literal['insert', 'remove', 'append', 'pop', 'sort', 'all', 'reverse', 'clear'],
                 add=False):
        if add:
            self._callbacks[method.lower()].append(func)
        else:
            self._callbacks[method.lower()] = [func]

    def __len__(self):
        return len(self._value)

    def __getitem__(self, key: int):
        return self._value[key]

    def __setitem__(self, key: int, newvalue: dict):
        self._value[key] = newvalue


if __name__ == '__main__':
    root = Tk()

    def printrow(row):
        print(row)

    datasource = DataSourceVar(value=[{'name': 'John', 'age': 30}, {'name': 'Mary', 'age': 25}])
    datasource.callable(printrow, 'append', add=True)
    datasource.append({'name': 'example', 'age': 2})
