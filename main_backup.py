import csv

import up_databases

# Connect to the database
db_manager = up_databases.DatabaseManager()

# Read the CSV file and insert its contents into the database
with open('log/sensing_value_old.csv', 'r') as file:
    print('Reading CSV')
    csv_reader = csv.reader(file)
    print(csv_reader)

    for row in csv_reader:
        print('row' + str(row))
        db_manager.backUpinsert(query=db_manager.insertQuery, params=(row[0], row[1], row[2], row[3]))
    print('Finished reading CSV')