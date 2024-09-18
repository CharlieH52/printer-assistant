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
        self.b1_scan.grid(column=1, row=0)

        self.b2_delete = ttk.Button(self.window, text="Borrar", command=self.borrar_impresora, state=DISABLED)
        self.b2_delete.grid(column=1, row=1)

        self.tkvariable.trace_add('write', self.revision_estado)

    def revision_estado(self, *args):
        if self.tkvariable.get():
            self.b2_delete.config(state='normal')
        else:
            self.b2_delete.config(state='disabled')

    def obtener_impresoras(self):
        ls_printer = [items.strip() for items in subprocess.getoutput('wmic printer list brief').split('\n') if items.strip()][1:]
        for printer in ls_printer:
            item_pr = re.sub(r' 0.*', '', printer).strip()
            if item_pr not in self.ls_clear:
                self.ls_clear.append(item_pr)
            
            self.ls_box1['values'] = self.ls_clear

    def borrar_impresora(self):
        printer = self.ls_box1.get()
        print(f"La impresora {printer} ha sido eliminada.")


root = Tk()
my = InterfaceModule(root)
root.title("Prueba de tkinter")
root.geometry("320x200")

root.mainloop()
