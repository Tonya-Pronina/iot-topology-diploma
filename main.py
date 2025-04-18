# main.py
import os
import sys

# 1) Вказуємо Qt шукати плагіни платформ у папці "platforms", що лежить поруч із main.py
plugin_path = os.path.join(os.path.dirname(__file__), 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

# 2) Тільки після цього можна імпортувати PyQt5
from PyQt5.QtWidgets import QApplication
from network import Network
from cli_parser import CLIParser
from gui_main import MainWindow

def main():
    # Налаштовуємо мережу та CLI
    network = Network()
    cli = CLIParser(network)

    # Додаємо пару тестових пристроїв
    network.add_device("sensor")
    network.add_device("lamp")

    # Створюємо і запускаємо GUI
    app = QApplication(sys.argv)
    window = MainWindow(network, cli)
    window.refresh()    # малюємо вузли і список уперше
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()