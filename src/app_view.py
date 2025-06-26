from os import system
from src.printer_manager import PrinterManager

class AppView:
    def __init__(self):
        self.pm = PrinterManager()
    
    def __clear_console(self):
        system('cls')

    def __spooler_status(self) -> str:
        return 'RUNNING' if self.pm.spooler_service_status() else 'STOPPED'
    
    def __invalid_input_message(self):
            self.__clear_console()
            print('Input ERROR: Type a valid option.')
            input('Press ANY key to continue...')

    def __confirmation_message(self) -> bool:
        while True:
            confirmation = None
            print('Please confirm your decision typing "YES":')
            confirmation = input('> ')
            if confirmation == "YES" or confirmation.upper() == "YES":
                confirmation = True
            else:
                confirmation = False
            return confirmation
            
    def main_menu(self):
        while True:
            self.__clear_console()
            selection = None
            printer_selected = None
            installed_printers = self.pm.get_printers_installed()
            spooler_status = self.__spooler_status()
            print('PRINTER ASSISTANT...\n')
            print(f'SERVICE <<SPOOLER>> STATUS: {spooler_status}\n')
            print('Type the number of your printer as you choice.\n')
            print('Printers installed on your system:')
            for printer in installed_printers:
                print(f'{installed_printers.index(printer)}. {printer}')

            selection = input('> ')
            if selection.isnumeric():
                printer_selected = installed_printers[int(selection)]
                self.__printer_menu(installed_printers, printer_selected)
            else:
                self.__invalid_input_message()

    def __printer_menu(self, printers: list[str], target_printer: str):
        while True:
            option = None
            print(f'Working on: {target_printer}\n')
            print('Select an option:\n'
                  '0. Cancel all printing jobs\n'
                  '1. Print a test page\n'
                  '2. Delete printer\n'
                  '3. Delete all printers (except this)\n'
                  '4. Back'
                  )
            option = input('> ')
        
            if option.isnumeric():
                if int(option) == 0:
                    self.pm.cancell_all_printing_jobs(target_printer)

                if int(option) == 1:
                    self.pm.print_test_page(target_printer)
                
                if int(option) == 2:
                    if self.__confirmation_message():
                        self.pm.delete_printer(target_printer)

                if int(option) == 3:
                    if self.__confirmation_message():
                        self.pm.delete_printers_except(printers,target_printer)

                if int(option) == 4:
                    break
            
            else:
                self.__invalid_input_message()
            

    