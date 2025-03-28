from src.app_menus import AppCLI

ac = AppCLI()

if __name__ == '__main__':
    while True:
        ac.main_menu()
        
        selection = input('Type any key to return or "e" to exit...')
                
        if selection == 'e' or selection == 'E':
            break
