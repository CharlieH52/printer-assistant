import subprocess
import re

class SubFunctions:
    def __init__(self):
        self.spooler_status = self._check_service()
    
    def _check_service(self):
        command = subprocess.getoutput('sc query "spooler"').split('\n')
        for line in command:
            if 'ESTADO' in line or 'STATUS' in line:
                status = (re.sub(r'(.*)\s*:\s([0-9])\s*', '', line)).strip()
                return status
            
a = SubFunctions()