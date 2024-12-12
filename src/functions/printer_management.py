from subprocess import run

from config import *

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
