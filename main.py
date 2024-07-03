import subprocess
import re

IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']

class PrinterList:
    def __init__(self):
        self.ls_clear = self.printer_list_cap()    

    # Captura y registra las impresoras instaladas en el sistema.
    def printer_list_cap(self):
        ls_clear = []
        ls_printer = [items.strip() for items in subprocess.getoutput('wmic printer list brief').split('\n') if items.strip()][1:]
        for printer in ls_printer:
            item_pr = re.sub(r' 0.*', '', printer).strip()
            if all(index not in item_pr for index in IGNORE):
                ls_clear.append(item_pr)
        return ls_clear
    
    # Lista las impresoras en pantalla.
    def printer_list(self):
        print('Impresoras instaladas en el sistema... \n')
        for index, item in enumerate(self.ls_clear):
            print(f"{index}. {item}")

class PrinterCleanner(PrinterList):
    def delete_printer(self, printer_name):
        try:
            subprocess.run(f"wmic printer where name='{printer_name}' delete /nointeractive", shell=True)
        except PermissionError as e:
            return print(e)

    def delete_all(self, printer_list):
        pass

    def main_program(self):
        print('MODULO DE LIMPIEZA')
        print('Selecciiona una opcion:\n')
        print('0. Eliminar una impresora.')
        print('1. Eliminar todas las impresoras.\n')
        print('Ingresa el numero de la opcion:')
              
        sel = input()
        
        if sel == '0':
                self.printer_list()
                print('Ingresa el numero de la impresora:')
                sel = input()
            while sel:

        if sel == '1':
            self.delete_all()            
        
class PrinterJobs:
    def test_page(self, printer_name):
        pass

    def reset_spool_service():
        pass

    def clean_queue():
        pass


if __name__ == '__main__':
    pc = PrinterCleanner()

    pc.printer_list()
    pc.main_program()

    