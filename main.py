from config import *
from src.functions.spooler_checker import spooler_status_checker
from src.functions.printer_installed_scanner import printer_scanner

if __name__ == '__main__':
    while True:
        clear_console()
        installed_printers = printer_scanner()
        spooler_status = spooler_status_checker()

        print('PRINTER MANAGEMENT...\n')
        print(f'ESTADO DEL SERVICIO <<SPOOLER>>: {spooler_status}\n')
        print('Ingresa el numero de la impresora a gestionar.\n')
        print('Impresoras instaladas en el sistema: ')
        for printer in installed_printers:
            print(f'{installed_printers.index(printer)} - {printer}')
        
        input()
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
        # elif selection == 'e' or selection == 'E':
        #     break
        