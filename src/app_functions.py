from subprocess import getoutput, run
from re import sub

IGNORE = ['OneNote', 'Fax', 'Microsoft', 'PDF']

class PrinterFunctions:
    def __init__(self):
        self.device_ignored = IGNORE

    def _remove_path(self, device):
        item = sub(r'.*\\(.*)', r'\1', device).strip()
        return item
    
    def spooler_service_status(self):
        command = getoutput('sc query "spooler"').split('\n')
        for line in command:
            if 'ESTADO' in line or 'STATUS' in line:
                status = (sub(r'(.*)\s*:\s([0-9])\s*', '', line)).strip()
                return status
    
    # STOP SPOOLER SERVICE
    def stop_spooler_service(self):
        spooler_status = self.spooler_service_status()    
        if spooler_status == 'RUNNING':
            run('NET STOP Spooler')

    # START SPOOLER SERVICE
    def start_spooler_service(self):
        spooler_status = self.spooler_service_status()
        if spooler_status == 'STOPPED':
            run('NET START Spooler')

    # SCAN ALL THE PRINTER DRIVERS INSTALLED
    def printer_scanner(self):
        printer_list = []
        printers = [items.strip() for items in getoutput('wmic printer get name').split('\n') if items.strip()][1:]
        for item in printers:
            if all(word not in item for word in self.device_ignored):
                if item not in printer_list:
                    if '\\' in item:
                        item_cl = self._remove_path(item)
                        printer_list.append(item_cl)
                    else:
                        printer_list.append(item)
        return printer_list

    # PRINT A TEST PAGE OF THE SELECTED PRINTER
    # This function require administrator permissions
    def print_testpage(device=str):
        try:
            ERROR_NAME = 'No hay instancias disponibles'
            status = run(f'wmic printer where name="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
            print(status.stdout)
            if ERROR_NAME in status.stdout:
                status = run(f'wmic printer where sharename="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
                print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)

    # OPEN THE PRINTER PROPERTIES OF THE SELECTED PRINTER
    def printer_properties_window(device=str):
        try:
            run(f'START rundll32 printui.dll,PrintUIEntryDPIAware /p /n "{device}"', shell=True)
        except Exception as e:
            print(e)

    # CANCEL THE QUEUE PRINT 
    def cancell_all_printing_jobs(device=str):
        try:
            ERROR_NAME = 'No hay instancias disponibles'
            status = run(f'wmic printer where name="{device}" call CancelAllJobs', text=True, capture_output=True, shell=True)
            print(status.stdout)
            if ERROR_NAME in status.stdout:
                status = run(f'wmic printer where sharename="{device}" call CancelAllJobs', text=True, capture_output=True, shell=True)
                print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)

    # DELETE SELECTED PRINTER
    # Only delete the controller not the software 
    def delete_printer_driver( device=str):
        run(f'wmic printer where name="{device}" delete /nointeractive', shell=True)

    # DELETE ALL PRINTERS EXCEPT THE SELECTED
    def delete_except(printers=list):
        for devices in printers:
            run(f'wmic printer where name="{devices}" delete /nointeractive', shell=True)