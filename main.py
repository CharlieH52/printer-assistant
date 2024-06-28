import subprocess
import re

IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']

def printer_list():
    return [items.strip() for items in subprocess.getoutput('wmic printer list brief').split('\n') if items.strip()][1:]

ls_printer = printer_list()
ls_clear = []
def clean_list():
    for printer in ls_printer:
        item_pr = re.sub(r' 0.*', '', printer).strip()
        for index in IGNORE:
            if index in item_pr:
                pass
            else:
                ls_clear.append(item_pr)

clean_list()
for item in ls_clear:
    print(item)