# ZeroDates. Script converts strings from date formats (xx/xx/xxxx) into integer offset (e.g., 12 = 12 days after Day Zero).
# Inputs: folderpath, patient_info_filename, zero_day_column_name
# Outputs: All *_data_*.txt files in the folderpath are copied into "zeroed" subfolder, with all date strings converted to ints for offset days.
import datetime
from pathlib import Path
import os

# Mandatory
#  folderpath = 'Prostate_TAN'
#  patient_info_filename = "data_clinical_patient.txt"
#  zero_day_column_name =  "DIAGNOSISDATE"   # "FIRST_DATE_OF_METASTASIS"

# Optional
debug_output = True
day_offset_for_errors = -1234 # If this value shows up in output, an error occured (e.g. empty cell)
date_format = '%Y-%M-%d'


# Internal globals
patient_zeros = {}
patient_fails = []


def transform_file(folderpath, filename):
    global debug_output
    global day_offset_for_errors
    global column_names
    global patient_zeros
    global patient_fails
    
    if debug_output:
        print('START transforming ' + filename)

    data_folder = Path(folderpath)
    file_to_open = data_folder / filename
    print("file_to_open=[" + str(file_to_open) + "]")
    f = open(file_to_open)
    content = f.readlines()

    # Build list of columns with dates
    # if column has 'date' in part of row 5, transform it.
    date_cols = []
    column_names = content[4].rstrip().split('\t')
    if debug_output:
        print(column_names)
    date_idx_list = [i for i, value in enumerate(column_names) if "DATE" in value]
    print ("Date indices list : " + str(date_idx_list) +"\n")
    
    # Run through lines of file. If > 5th line, do transformation.
    for idx, val in enumerate(content):
        row = val.rstrip().split('\t')
        
        if idx < 5:
            # header rows
            # print(val)
            if idx == 2:
                # Turn likely STRING to NUMBER type, as we go from '03/13/20' to an int.
                for i, date_index_val in enumerate(date_idx_list):
                    date_index = date_idx_list[i]                
                    row[date_index] = "NUMBER"
                    row_final = "\t".join(row)+"\n"
                    content[idx] = row_final
                    
        else:
            # data rows
            

            # If Excel doesn't have values for every column,
            # let's stick in empty cells. But should probably be a warning.
            row = row + [""] * (len(column_names) - len(row))
            if debug_output:
                print('row len ' + str(len(row)))
                print('row=('+str(row)+')')
            
            patient_id = row[0]
            zero_day = False
            if patient_id in patient_zeros:
                zero_day = patient_zeros[patient_id]
                
            if debug_output:
                print("pid " + patient_id +"!")
                print("zero for " + patient_id + " is " + str(zero_day))


            for i, date_index_val in enumerate(date_idx_list):

                date_index = date_idx_list[i]
                print('date index for i='+str(i)+' is ' + str(date_index))
                
                raw_date_text = row[date_index]
                

                if zero_day == False:
                    row[date_index] = str(day_offset_for_errors)
                else:
                    try:
                        this_day = datetime.datetime.strptime(raw_date_text, date_format)
                        
                        delta = this_day - zero_day
                        days_as_str = str(delta.days)

                        # print(str(date_index)+" converted ["+raw_date_text+"] to " + days_as_str )
                        row[date_index] = days_as_str
                    except Exception as e: 
                        # print(str(date_index)+" zero day exception for ["+raw_date_text+"]" )
                        row[date_index] = str(day_offset_for_errors)
                        # print('exc in col ',str(date_index))
                if date_index == len(row)-1:
                    if debug_output:
                        print("last column, value=",row[date_index])
                    row[date_index] = row[date_index]  # + "\n"

            row_final = "\t".join(row)+"\n"
            content[idx] = row_final
            if debug_output:
                print(idx, row_final+"\n")

    output_filename = "zerodate_" + filename
    file_to_open = data_folder / output_filename
    file2 = open(file_to_open, "w")
    with file_to_open.open("w") as f:
        f.writelines(content)
    
    if debug_output:
        print("DONE transforming     " + filename + "\n\n")


def zero_dates(folderpath, patient_info_filename = "data_clinical_patient.txt", zero_day_column_name =  "DIAGNOSISDATE" ):
    global debug_output
    global column_names
    global patient_zeros
    global patient_fails

    zero_day_column = -1
    with open(folderpath + "/" + patient_info_filename, 'r', newline='\r\n') as f:
        content = f.readlines()
        column_names = content[4].rstrip().split('\t')
        print('=== In zero_dates, column_names     is...')
        print("["+str(column_names)+"]")

        print('=== In zero_dates, column_names[1]     is...')
        print("["+str(column_names[1])+"], zdcn=["+str(zero_day_column_name)+"]")
        zero_day_column = column_names.index(zero_day_column_name)

    print("zero_day_column in " + patient_info_filename + " is " + str(zero_day_column))
    if zero_day_column < 0 :
        raise "Zero day column missing!"
    
    patient_zeros = {}  # dict where key=patientId, value=datetime object of zero day.
    patient_fails = []  # list of patientIds without a zero day value.

    # Find zero day for each patient.
    for x in range(5,len(content)): 
        row = content[x].rstrip().split('\t')
        patient_id = row[0]
        zero_day_string = row[zero_day_column]
        try:
            print('2nd ATTEMPT for pid '+patient_id+' using dateformat ('+str(date_format)+'), based on zero_day_string ['+zero_day_string+']')
            zero_date = datetime.datetime.strptime(zero_day_string, date_format) #   '%m/%d/%Y')
            print('zero_date for pid '+patient_id+' is '+str(zero_date)+', based on zero_day_string ['+zero_day_string+']')
            #    new_row = patient_id, zero_date
            patient_zeros[patient_id] = zero_date
        except Exception as e: 
            patient_fails.append(patient_id)

    print('patient_zeros, count=' + str(len(patient_zeros)))
    print('patient_fails, count=' + str(len(patient_fails)))

    files = os.listdir(folderpath)
    print('Files to transform dates in:')
    #print('SAMPLE ONLY=========')
    for file in files:
        if file.startswith("data") and file.endswith(".txt"):
            print(file) #(os.path.join(root, file))
    print("--START--")

    for filename in files:
        if filename.startswith("data") and filename.endswith(".txt"):
            transform_file(folderpath, filename)

    print("--END--")
    print("Look for output files, with the prefix 'zerodate_'.")

