import subprocess
import re

class PrinterManagement:
    def __init__(self):
        # Ignore all virtual devices or unnecesary devices
        self.IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']

    def printer_scanner(self):
        printer_list = []
        printers = [items.strip() for items in subprocess.getoutput('wmic printer list brief').split('\n') if items.strip()][1:]
        for item in printers:
            item_cl = re.sub(r' 0.*', '', item).strip()
            if all(word not in item_cl for word in self.IGNORE):
                if item_cl not in printer_list:
                    printer_list.append(item_cl)
        return printer_list
            
    def borrar_impresora(self, device=str):
        subprocess.run(f'wmic printer where name="{device}" delete /nointeractive', shell=True)

    # This function require administrator permissions
    def print_testpage(self, device=str):
        try:
            subprocess.run(f'wmic printer where name="{device}" call PrintTestPage', shell=True)
        except TypeError as e:
            print(e)


'''while True:
    variable = input()
    subprocess.run(f'wmic printer where name="EPSON L3110 Series" get {variable} /value')'''