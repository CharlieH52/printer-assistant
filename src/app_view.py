from os import system
from src.printer_manager import PrinterManager


pm = PrinterManager()
class AppView:
    def __clear_console(self):
        system('cls')

    def __spooler_status(self) -> str:
        status = ''
        if pm.spooler_service_status():
            status = 'EN EJECUCION'
        elif pm.spooler_service_status():
            status = 'DETENIDO'
        return status
    
    def main_menu(self):
        while True:
            self.__clear_console()
            installed_printers = pm.get_printers_installed()
            spooler_status = self.__spooler_status()
            print('PRINTER ASSISTANT...\n')
            print(f'SERVICE <<SPOOLER>> STATUS: {spooler_status}\n')
            print('Type the number of your printer as you choice.\n')
            print('Printers installed on your system:')
            for printer in installed_printers:
                print(f'{installed_printers.index(printer)}. {printer}')

            selection = input('> ')

            printer_selected = installed_printers[int(selection)]
            
            if selection.isnumeric() and printer_selected in installed_printers:
                input()

            if selection == 'e' or selection == 'E':
                break
            
            print('Please, type a valid option.')
            input('Press ANY key to continue...')

    