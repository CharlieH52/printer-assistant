from os import system
from src.app_functions import PrinterFunctions

pf = PrinterFunctions()

lsOptions = [
    '1. Print test page.',
    '2. Printer properties.',
    '3. Cancel all queue tasks.',
    '4. Share printer.',
    '5. Reset queue service.',
    '6. Delete printer.',
    '7. Delete all EXCEPT ONE.'
    'Exit'                 
]

class AppCLI:
    def __init__(self):
        self.selection = None
        self.printer_selected = None

    def clear_console(self):
        system('cls')

    def main_menu(self):
        self.selection = None
        installed_printers = pf.printer_scanner()
        spooler_status = pf.spooler_service_status()
        while True:
            self.clear_console()
            pf.spooler_service_status()
            print('PRINTER ASSISTANT...\n')
            print(f'SERVICE <<SPOOLER>> STATUS: {spooler_status}\n')
            print('Type the number of your printer as you choice.\n')
            print('Printers installed on your system:')
            for printer in installed_printers:
                print(f'{installed_printers.index(printer)}. {printer}')

            self.selection = input('> ')
            self.printer_selected = installed_printers[int(self.selection)]
            print(len(installed_printers))
            if self.selection.isnumeric() and self.printer_selected in installed_printers:
                self.printer_menu()

            if self.selection == 'e' or self.selection == 'E':
                break
            
            print('Please, type a valid option.')
            input('Press ANY key to continue...')


    def printer_menu(self):
        self.selection = None
        while True:
            for item in lsOptions:
                print(item)

            self.selection = input('> ')

            if self.selection == 'e' or self.selection == 'E':
                break
            

    # if selection == 0:
    #     pm.print_testpage(device=printer)
    # elif selection == 1:
    #     pm.printer_properties(device=printer)
    # elif selection == 2:
    #     pm.cancell_all_jobs(device=printer)
    # elif selection == 3:
    #     pass
    # elif selection == 4:
    #     pm.reboot_spool()
    # elif selection == 5:
    #     pm.delete_printer(device=printer)
    # elif selection == 6:
    #     pm.delete_except(device=printer)
    #     devices = []
    #     for device in rdr.printer_list:
    #         if printer not in device:
    #             devices.append(device)
    #         else:
    #             print(f'{printer} not added.')
        
    #     pm.delete_except(devices)
    