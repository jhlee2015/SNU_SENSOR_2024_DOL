import configparser
import csv

import up_config_manager
import up_databases
import tkinter as tk
from tkinter import filedialog

import up_util
import os

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
    # Read the selected CSV file and insert its contents into the database
    # Get the list of files in the "log" directory that start with "csv.log."
    file_list = [file_name for file_name in os.listdir('log') if file_name.startswith('csv.log.')]

    # Iterate over each file in the directory
    for file_name in file_list:
        file_path = os.path.join('log', file_name)
        
        # Read the selected CSV file and insert its contents into the database
        with open(file_path, 'r') as file:
            print('Reading CSV')
            
            csv_reader = csv.reader(file)
            print(csv_reader)

            for row in csv_reader:
                print('row' + str(row))
                db_manager.backUpinsert(query=db_manager.insertQuery, params=(row[0], row[1], row[2], row[3]))
            print('Finished reading CSV')

elif os_config.get('os_name') == 'LINUX_UNIT':

    # linux용
    with open('log/csv.log', 'r') as file:
        print('Reading CSV')
        csv_reader = csv.reader(file)
        print(csv_reader)

        for row in csv_reader:
            print('row' + str(row))
            db_manager.backUpinsert(query=db_manager.insertQuery, params=(row[0], row[1], row[2], row[3]))
        print('Finished reading CSV')