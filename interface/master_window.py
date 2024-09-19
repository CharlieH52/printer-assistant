import tkinter as tk
from tkinter import *
from tkinter import ttk
import subprocess
import re

class InterfaceModule():
    def __init__(self, root):
        self.ls_clear = []
        self.window = root
        self.tkvariable = tk.StringVar()

        self.ls_box1 = ttk.Combobox(self.window, textvariable=self.tkvariable)
        self.ls_box1.grid(column=0, row=0)

        self.b1_scan = ttk.Button(self.window, text="Escanear", command=self.obtener_impresoras)
        self.b1_scan.grid(column=1, row=0, padx=16)

        self.b2_delete = ttk.Button(self.window, text="Test", command=self.print_testpage, state=DISABLED)
        self.b2_delete.grid(column=1, row=1, padx=16)

        self.tkvariable.trace_add('write', self.revision_estado)

    def revision_estado(self, *args):
        if self.tkvariable.get():
            self.b2_delete.config(state='normal')
        else:
            self.b2_delete.config(state='disabled')

   


root = Tk()
my = InterfaceModule(root)
root.title("Prueba de tkinter")
root.resizable(False, False)
root.geometry("320x200")
root.configure(padx=16, pady=16)


root.mainloop()
