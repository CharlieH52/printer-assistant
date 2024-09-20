import tkinter as tk

from tkinter import *
from tkinter import ttk
from interface.config import *
from printers.printer_management import PrinterManagement

class InterfaceModule:
    def __init__(self):
        self.pm = PrinterManagement()

        self.root = Tk()
        
        self.tkvariable = tk.StringVar()

        self.gp_list = ttk.Frame(self.root)
        self.ls_box1 = tk.Listbox(self.gp_list, listvariable=self.tkvariable, width=48)
        
        self.gp_buttons = ttk.Frame(self.root)
        self.b1_scan = ttk.Button(self.gp_buttons, text='Scan', command=self.update_list)
        self.b2_testpage = ttk.Button(self.gp_buttons, text='Test Page', command=self.print_testpage, state=DISABLED)
        self.b3_print = ttk.Button(self.gp_buttons, text='Print', command=self.size)
        
        self.gp_history = ttk.Frame(self.root)
        self.ls_box2 = ttk.Label(self.gp_history)

        self.tkvariable.trace_add('write', self.state_checker)

    def state_checker(self, *args):
        if self.tkvariable.get():
            self.b2_testpage.config(state='normal')
        else:
            self.b2_testpage.config(state='disabled')

    def distribution_configure(self):
        main_window_config(self.root)

        self.gp_list.pack(side='left')
        self.ls_box1.pack(side='left')
        
        self.gp_buttons.pack(side='left', padx=16)
        self.b1_scan.pack(side='left')
        self.b2_testpage.pack(side='left', padx=8)
        self.b3_print.pack(side='left')

        self.gp_history.pack(side='left')
        self.ls_box2.pack(side='left')
        
        self.root.mainloop()
    
    def update_list(self):
        printers = self.pm.printer_scanner()
        items_listbox = self.ls_box1.get(0, tk.END)
        for device in printers:
            if device not in items_listbox:
                self.ls_box1.insert(printers.index(device), device)
            else:
                print(f'Ya existe este elemento {device}')

    def print_testpage(self):
        index = self.ls_box1.curselection()
        if index:
            printer = self.ls_box1.get(index)   
            self.pm.print_testpage(printer)
        else:
            print('Debes seleccionar un dispositivo.')

    def size(self):
        var1 = [self.gp_list.winfo_width(), self.root.winfo_height()]
        var2 = [self.b1_scan.winfo_width(), self.b1_scan.winfo_height()]
        print(f'window{var1}')
        print(f'button{var2}')
