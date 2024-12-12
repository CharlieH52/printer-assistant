from subprocess import getoutput
from re import sub
from config import IGNORE

def _remove_path(device):
    item = sub(r'.*\\(.*)', r'\1', device).strip()
    return item

def printer_scanner():
    printer_list = []
    printers = [items.strip() for items in getoutput('wmic printer get name').split('\n') if items.strip()][1:]
    for item in printers:
        if all(word not in item for word in IGNORE):
            if item not in printer_list:
                if '\\' in item:
                    item_cl = _remove_path(item)
                    printer_list.append(item_cl)
                else:
                    printer_list.append(item)
    return printer_list