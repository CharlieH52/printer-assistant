from os import system

from scripts.printer_management import PrinterManagement
from scripts.device_reader import Reader
from scripts.sub_functions import SubFunctions

if __name__ == '__main__':
    pm = PrinterManagement()
    sf = SubFunctions()
    rdr = Reader()
    
    control = False
    printer = str

    while True:
        system('cls')
        print('PRINTER MANAGEMENT...\n')
        print(f'ESTADO DEL SERVICIO <<SPOOLER>>: {sf.spooler_status}\n')
        print('Ingresa el numero de la impresora a gestionar.\n')
        print('Impresoras instaladas en el sistema: ')
        for printer in rdr.printer_list:
            print(f'{rdr.printer_list.index(printer)} - {printer}')
        
        while True:
            selection = input('DISPOSITIVO: ')
            if selection.isnumeric():
                selection = int(selection)
                break
            else:
                print('Ingresa un valor valido...')

        for printer in rdr.printer_list:   
            if selection == rdr.printer_list.index(printer):
                control = True
                break

        if control:
            system('cls')
            control = False
            break
    
        print('Impresora especificada no localizada...\n')

    while True:
        print(f'Impresora seleccionada... {printer}\n')
        print('Ingresa el numero de la opcion a ejecutar.\n')
        for option in pm.lsOptions:
            if 'EXCEPTO' in option:
                print(f'{pm.lsOptions.index(option)} - {option} >> "{printer}"')
            else:
                print(f'{pm.lsOptions.index(option)} - {option}')
        
        print('Escribe "e" o "E" para salir del programa.\n')

        selection = input('OPCION: ')
        
        if selection.isnumeric():
            selection = int(selection)

        elif 'e' or 'E' in selection:
            selection

        if selection == 0:
            pm.print_testpage(device=printer)
        elif selection == 1:
            pm.printer_properties(device=printer)
        elif selection == 2:
            pm.cancell_all_jobs(device=printer)
        elif selection == 3:
            pm.reboot_spool()
        elif selection == 4:
            pm.delete_printer(device=printer)
        elif selection == 5:
            pm.delete_except(device=printer)
        elif selection == 6:
            devices = []
            for device in rdr.printer_list:
                if printer not in device:
                    devices.append(device)
                else:
                    print(f'{printer} not added.')
            
            pm.delete_except(devices)
        elif selection == 'e' or selection == 'E':
            break
        