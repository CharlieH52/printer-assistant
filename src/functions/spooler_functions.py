from subprocess import run
from src.functions.spooler_checker import spooler_status_checker

# REBOOT SERVICE SPOOLER
def stop_spooler_service():
    spooler_status = spooler_status_checker()    
    if spooler_status == 'RUNNING':
        run('NET STOP Spooler')

def start_spooler_service():
    spooler_status = spooler_status_checker()
    if spooler_status == 'STOPPED':
        run('NET START Spooler')