import tkinter as tk

from tkinter import *
from tkinter import ttk
from printers.printer_management import PrinterManagement

class InterfaceModule:
    def __init__(self):
        self.pm = PrinterManagement()

        self.root = Tk()
        self.root.title('Printer Management')
        self.root.resizable(width=True, height=False)
        self.root.geometry('320x200')
        self.root.configure(padx=16, pady=16)
        self.root.grid_columnconfigure(index=4)
        
        self.tkvariable = tk.StringVar()

        self.ls_box1 = tk.Listbox(self.root, listvariable=self.tkvariable)
        
        self.group1 = ttk.Frame(self.root)
        self.b1_scan = ttk.Button(self.group1, text='Scan', command=self.update_list)
        self.b2_testpage = ttk.Button(self.group1, text='Test Page', command=self.print_testpage, state=DISABLED)
        self.b3_print = ttk.Button(self.group1, text='Print', command=None)

        self.tkvariable.trace_add('write', self.state_checker)

    def state_checker(self, *args):
        if self.tkvariable.get():
            self.b2_testpage.config(state='normal')
        else:
            self.b2_testpage.config(state='disabled')

    def distribution_configure(self):
        self.ls_box1.grid(column=0, rowspan=1, row=0)
        self.group1.grid(column=1, columnspan=2, rowspan=2, row=0, sticky='NSEW')
        
        self.b1_scan.grid(column=0, row=0, padx=8)
        self.b2_testpage.grid(column=1, row=0)
        self.b3_print.grid(column=2, row=0, padx=8)
        
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
