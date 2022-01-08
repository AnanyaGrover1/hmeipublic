from flask import Flask, render_template

app = Flask(__name__)

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('gentle-complex-291219-89d8d9d2b18a.json', scope)

# authorize the clientsheet
client = gspread.authorize(creds)

sheet = client.open('US_counties_test')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

print(sheet_instance.cell(col=3, row=2))

#Update Cell
cell = sheet_instance.cell(10,13)
print('Cell Before Update: ',cell.value)
sheet_instance.update_cell(10,13,20)
cell = sheet_instance.cell(10,13)
print('Cell After Update: ',cell.value)


#Update Multiple Cells
cell_list = sheet_instance.range('M2:M8')
cell_values = [10,20,30,40,50,60,70]

for i, val in enumerate(cell_values):  #gives us a tuple of an index and value
    cell_list[i].value = val    #use the index on cell_list and the val from cell_values

sheet_instance.update_cells(cell_list)

#Update cells using corresponding county ID (or name, I'm using ID here)

cell_list2 = []

# get the headers from row #1
headers = sheet_instance.row_values(1)
# find the column "HAZARD", we will remember this column #
colToUpdate = headers.index('HAZARD') + 1

# task 1 of 2
cellLookup = sheet_instance.find('12045')
# get the cell to be updated
cellToUpdate = sheet_instance.cell(cellLookup.row, colToUpdate)
# update the cell's value
cellToUpdate.value = 77
# put it in the queue
cell_list2.append(cellToUpdate)

# task 2 of 2
cellLookup = sheet_instance.find('13039')
# get the cell to be updated
cellToUpdate = sheet_instance.cell(cellLookup.row, colToUpdate)
# update the cell's value
cellToUpdate.value = 28
# put it in the queue
cell_list2.append(cellToUpdate)

# now, do it
sheet_instance.update_cells(cell_list2)

# get all the records of the data
records_data = sheet_instance.get_all_records()


# convert the json to dataframe
records_df = pd.DataFrame.from_dict(records_data)


hazard = records_df[['ID', 'HAZARD']]

# define variables for hazard ranges 

low = ""
medium = ""
high = ""

# iterate through the row and save all values that fit given condition

for idx, row in hazard.iterrows():

    if row['HAZARD'] > 10 and row['HAZARD'] < 50:
      low += 'County ' + str(row['ID']) + ' – ' + str(row['HAZARD']) + '. '

    if row['HAZARD'] >= 50 and row['HAZARD'] < 70:
      medium += 'County ' + str(row['ID']) + ' – ' + str(row['HAZARD']) + '. '
    
    if row['HAZARD'] >= 70:
      high += 'County ' + str(row['ID']) + ' – ' + str(row['HAZARD']) + '! '

print(low)


# send info to website

@app.route('/')
def index():
    return render_template('index.html', low=low, medium=medium, high=high)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

