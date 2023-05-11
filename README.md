# CTkDataGridView

CTkDataGridView is a library based in [C# DataGridView from Windows Forms](https://learn.microsoft.com/pt-br/dotnet/api/system.windows.forms.datagridview?view=windowsdesktop-7.0) created in tkinter using grid, a custom CTkEntry named [CTkMaskedEntry](https://github.com/RickWalkerOne/CTkMaskedEntry) and Variable.

## Installation

Download Raw files and import all for you code. Import too te folder from [CTkMaskedEntry](https://github.com/RickWalkerOne/CTkMaskedEntry) and paste in the root folder.

## Usage

```python
from customtkinter import CTk
from CTkDataGridView import CTkDataGridView, DataSource, Column
from CTkDataGridView.mask import Mask

root = CTk()
root.title('Data Grid View')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

__columns = [
    Column('name', column_type=str, text='Name'),
    Column('age', column_type=int, text='Age'),
    Column('marriage', column_type=bool, text='Marriage'),
    Column('cellphone', column_type=str, text='Cellphone', mask=Mask('fixed', '9999-9999'))
]
__data = DataSourceVar(
    value=[{'name': 'example', 'age': 15, 'marriage': False, 'cellphone': '12341234'},
           {'name': 'Fulan', 'age': None, 'marriage': True, 'cellphone': '43214321'}])
table = CTkDataGridView(root, __data, 10, __columns)
table.grid(row=0, column=0, sticky='nsew')
mynewrow = {'name': 'new name', 'age': 0, 'marriage': True, 'cellphone': '12344321'}
for x in range(10):
    __data.append(mynewrow)
__index = table.index(mynewrow)

root.mainloop()
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## How it looks?
![Screenshot](https://raw.githubusercontent.com/RickWalkerOne/CTkDataGridView/main/Capturar.jpg)

## License

[Creative Commons Zero v1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
