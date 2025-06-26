import subprocess
from re import sub


class PrinterManager:
    IGNORE_PRINTERS = ['OneNote', 'Fax', 'Microsoft', 'PDF']

    def __remove_path(self, device):
        item = sub(r'.*\\(.*)', r'\1', device).strip()
        return item
    
    def __parse_service_status(self, output: subprocess.CompletedProcess) -> dict[str, str]:
        spooler_status = {}
        get_lines = output.stdout.strip().split('\n')
        for line in get_lines:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                if key and value:
                    spooler_status[key] = value
        return spooler_status

    def __execute_command(self, cmd_list: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(cmd_list, capture_output=True, text=True, shell=True)

    def spooler_service_status(self) -> bool:
        status = False
        service_command = ['sc', 'query', 'spooler']
        try:
            cmd_output = self.__execute_command(service_command)
            service_information = self.__parse_service_status(cmd_output)
            current_status = service_information.get('ESTADO', '').upper()
            if 'RUNNING' in current_status:
                status = True
            if 'STOP' in current_status:
                status = False
        except subprocess.SubprocessError as e:
            print(e)
        return status
    
    # STOP SPOOLER SERVICE
    def stop_spooler_service(self):
        stop_command = ['NET', 'STOP', 'spooler']
        spooler_status = self.spooler_service_status()    
        if spooler_status == True:
            subprocess.run(stop_command)

    # START SPOOLER SERVICE
    def start_spooler_service(self):
        start_command = ['NET', 'START', 'spooler']
        spooler_status = self.spooler_service_status()
        if spooler_status == False:
            subprocess.run(start_command)

    def __parse_printers_list(self, command_output: subprocess.CompletedProcess) -> list[str]:
        printers_set = []
        get_text = command_output.stdout.split('\n')[1:]
        for printer in get_text:
            if all(word_list not in printer for word_list in self.IGNORE_PRINTERS):
                if printer not in printers_set and printer.strip():
                    if '\\' in printer:
                        parse_printer = self.__remove_path(printer)
                        printers_set.append(parse_printer.strip())
                    else:
                        printers_set.append(printer.strip())
        return printers_set

    # SCAN ALL THE PRINTER DRIVERS INSTALLED
    def get_printers_installed(self) -> list[str]:
        printers_command = ['wmic', 'printer', 'get', 'name']
        cmd_output = self.__execute_command(printers_command)
        printers_list = self.__parse_printers_list(cmd_output)
        return printers_list

    # PRINT A TEST PAGE OF THE SELECTED PRINTER
    # This function require administrator permissions
    def print_test_page(self, device: str):
        local_printer_command = ['wmic', 'printer', 'where', f'name="{device}"', 'call', 'PrintTestPage']
        shared_printer_command = ['wmic', 'printer', 'where', f'sharename="{device}"', 'call', 'PrintTestPage']
        ERROR_NAME = 'No hay instancias disponibles'
        try:
            status = self.__execute_command(local_printer_command)
            if ERROR_NAME in status.stdout:
                status = self.__execute_command(shared_printer_command)
                print(status.stdout)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)

    # OPEN THE PRINTER PROPERTIES OF THE SELECTED PRINTER
    def open_printer_properties(self, device: str):
        properties_command = ['START', 'rundll32', 'printui.dll,PrintUIEntryDPIAware', '/p', '/n', f'"{device}"']
        try:
            self.__execute_command(properties_command)
        except Exception as e:
            print(e)

    # CANCEL THE QUEUE PRINT 
    def cancell_all_printing_jobs(self, device: str):
        cancel_local_command = ['wmic', 'printer', 'where', f'name="{device}"', 'call', 'CancelAllJobs']
        cancel_shared_command = ['wmic', 'printer', 'where', f'sharename="{device}"', 'call', 'CancelAllJobs']
        ERROR_NAME = 'No hay instancias disponibles'
        try:
            status = self.__execute_command(cancel_local_command)
            if ERROR_NAME in status.stdout:
                status = self.__execute_command(cancel_shared_command)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)

    # DELETE SELECTED PRINTER
    # Only delete the controller not the software 
    def delete_printer(self, device: str):
        delete_printer_command = ['wmic', 'printer', 'where', f'name="{device}"', 'delete', '/nointeractive']
        self.__execute_command(delete_printer_command)

    # DELETE ALL PRINTERS EXCEPT THE SELECTED
    def delete_printers_except(self, printers_list: list, exception: str):
        to_delete = [printer for printer in printers_list if printer != exception]
        for printer in to_delete:
            self.delete_printer(printer)