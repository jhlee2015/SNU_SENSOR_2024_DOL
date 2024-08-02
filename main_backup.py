import configparser
import csv

import up_config_manager
import up_databases
import tkinter as tk
from tkinter import filedialog

import up_util

# Connect to the database
db_manager = up_databases.DatabaseManager()
os_config =up_config_manager.ConfigManager().get_os_config()

if os_config.get('os_name') == 'WINDOW':
    # Read the CSV file and insert its contents into the database
    # Open a file dialog to select the CSV file
    # windows용
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    # Read the selected CSV file and insert its contents into the database
    with open(file_path, 'r') as file:
        print('Reading CSV')
        csv_reader = csv.reader(file)
        print(csv_reader)

        for row in csv_reader:
            print('row' + str(row))
            db_manager.backUpinsert(query=db_manager.insertQuery, params=(row[0], row[1], row[2], row[3]))
        print('Finished reading CSV')

elif os_config.get('os_name') == 'LINUX':
    # linux용
    with open('log/sensing_value_old.csv', 'r') as file:
        print('Reading CSV')
        csv_reader = csv.reader(file)
        print(csv_reader)

        for row in csv_reader:
            print('row' + str(row))
            db_manager.backUpinsert(query=db_manager.insertQuery, params=(row[0], row[1], row[2], row[3]))
        print('Finished reading CSV')