from interface.master_window import InterfaceModule
from printers.printer_management import PrinterManagement

def main():
    ui = InterfaceModule()
    pm = PrinterManagement()

    ui.distribution_configure()

if __name__ == '__main__':
    main()