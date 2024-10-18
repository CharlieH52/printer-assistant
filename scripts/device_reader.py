import subprocess
import re

class Reader:
    def __init__(self):
        self.printer_list = []

        # Ignore all virtual devices or unnecesary devices
        self.IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']
        self.printer_list = self.printer_scanner()

    def printer_scanner(self):
        printers = [items.strip() for items in subprocess.getoutput('wmic printer get name').split('\n') if items.strip()][1:]
        for item in printers:
            if all(word not in item for word in self.IGNORE):
                if item not in self.printer_list:
                    if '\\' in item:
                        item_cl = self._remove_path(item)
                        self.printer_list.append(item_cl)
                    else:
                        self.printer_list.append(item)
        return self.printer_list
    
    def _remove_path(self, device):
        item = re.sub(r'.*\\(.*)', r'\1', device).strip()
        return item