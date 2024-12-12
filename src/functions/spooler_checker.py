from subprocess import getoutput
from re import sub

def spooler_status_checker():
    command = getoutput('sc query "spooler"').split('\n')
    for line in command:
        if 'ESTADO' in line or 'STATUS' in line:
            status = (sub(r'(.*)\s*:\s([0-9])\s*', '', line)).strip()
            return status