import subprocess

from time import sleep

from scripts.sub_functions import SubFunctions

sf = SubFunctions()
class PrinterManagement:
    def __init__(self):
        self.lsOptions = ['Imprimir pagina de prueba.',
            'Propiedades de la impresora.',
            'Cancelar trabajos en cola.',
            'Compartir impresora.',
            
            'Reiniciar servicio de cola.',
            'Eliminar impresora.',
            'Eliminar todas EXCEPTO'                 
        ]

    # This function require administrator permissions
    def print_testpage(self, device=str):
        try:
            ERROR_NAME = 'No hay instancias disponibles'
            status = subprocess.run(f'wmic printer where name="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
            print(status.stdout)
            if ERROR_NAME in status.stdout:
               status = subprocess.run(f'wmic printer where sharename="{device}" call PrintTestPage', text=True, capture_output=True, shell=True)
               print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)

    def printer_properties(self, device=str):
        try:
            subprocess.run(f'START rundll32 printui.dll,PrintUIEntryDPIAware /p /n "{device}"', shell=True)
        except Exception as e:
            print(e)

    def cancell_all_jobs(self, device=str):
        try:
            ERROR_NAME = 'No hay instancias disponibles'
            status = subprocess.run(f'wmic printer where name="{device}" call CancelAllJobs', text=True, capture_output=True, shell=True)
            print(status.stdout)
            if ERROR_NAME in status.stdout:
               status = subprocess.run(f'wmic printer where sharename="{device}" call CancelAllJobs', text=True, capture_output=True, shell=True)
               print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)
    
    def reboot_spool(self):
        print(sf.spooler_status)    
        if sf.spooler_status == 'RUNNING':
            sleep(5)
            print('DETENIENDO SERVICIO')
            subprocess.run('NET STOP Spooler')
            sleep(5)
            print('INICIANDO SERVICIO')
            subprocess.run('NET START Spooler')
    
        elif sf.spooler_status == 'STOPPED':
            print('INICIANDO SERVICIO')
            subprocess.run('NET START Spooler')
    
    def delete_printer(self, device=str):
        subprocess.run(f'wmic printer where name="{device}" delete /nointeractive', shell=True)
    
    def delete_except(self, printers=list):
        for devices in printers:
            subprocess.run(f'wmic printer where name="{devices}" delete /nointeractive', shell=True)
            sleep(2)