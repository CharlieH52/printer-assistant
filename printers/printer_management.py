import subprocess
import re

class PrinterManagement:
    def __init__(self):
        # Ignore all virtual devices or unnecesary devices
        self.IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']

    def printer_scanner(self):
        printer_list = []
        printers = [items.strip() for items in subprocess.getoutput('wmic printer get name').split('\n') if items.strip()][1:]
        for item in printers:
            if all(word not in item for word in self.IGNORE):
                if item not in printer_list:
                    if '\\' in item:
                        item_cl = self.remove_path(item)
                        printer_list.append(item_cl)
                    else:
                        printer_list.append(item)
        return printer_list
    
    def remove_path(self, device):
        item = re.sub(r'.*\\(.*)', r'\1', device).strip()
        return item
            
    def borrar_impresora(self, device=str):
        subprocess.run(f'wmic printer where name="{device}" delete /nointeractive', shell=True)

    # This function require administrator permissions
    def print_testpage(self, device=str):
        try:
            ERROR_NAME = 'No hay instancias disponibles'
            status = subprocess.run(f'wmic printer where name="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
            print(status.stdout)
            if ERROR_NAME in status.stdout:
               status = subprocess.run(f'wmic printer where sharename="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
               print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)