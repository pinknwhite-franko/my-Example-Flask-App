#!/usr/bin/env python
# coding: utf-8

# In[1]:


#################################
##    Package Installation     ##
#################################
import pandas as pd
import numpy as np
import re

from datetime import datetime
import time
from shutil import copyfile


import os
import sys
import shutil
from os import listdir
from os.path import isfile, join


# In[2]:


#################################
##     Fucntion definitions    ##
#################################
def copy_file(file_name_list):
    """make a copy of the file 
    and rename it to end with 'CLEAN'
    """
    copyfile( file_name_list[0] + file_name_list[1] , file_name_list[0] + "_COPY" + file_name_list[1]) # copyfile(selectedFileName, selectedFileName_CLEAN)


# In[3]:


def validate_ei(ei_text):
    """check if the external identification start with yes
    check if it has 53 colunms
    """
    if ei_text is None:
        return False
    elif not (ei_text.lower().startswith('yes') or ei_text.lower().startswith('no')):
        return False
    else:
        return True


# 

# In[4]:


def validate_date(row_cell):
    """Create a workbook 
    importing package used to read in the data
    define the function to validate the date
    """
    # optional 
    #print("cell:", row_cell)
    if row_cell in (None, '', pd.NaT, np.nan):
        #print("none or '': ", row_cell)
        return False
    if row_cell == '0.0f':
        #print("0.0f: ", row_cell)
        return False
    else:
        #print("none of the above:", row_cell)
        return True
        
# TODO: Test cases: run quick tests on the validation functions


# In[5]:


def check_copyover_file(file_name_list):
    """Create a workbook 
    # run through spreadsheet row by row and determine if a row need to be cleaned
    # create a new file with TO_CLEAN at the end
    """
    # open the work sheet
    df_copy = pd.read_excel(file_name_list[0] + "_COPY" + file_name_list[1])
    if len(df_copy.columns) > 19:
        df_copy = df_copy.loc[:, 'Customer':'LOQ']
    series_clean = []
    series_toclean = []
    #df_clean = pd.DataFrame(columns=df_copy.columns)
    #df_toclean = pd.DataFrame(columns=df_copy.columns)
    

    for index, row in df_copy.iterrows():
        if not (validate_date(row['Sample Fixed Date'])
            and validate_date(row['Sample Fixed Date']) 
            and validate_date(row['Sample Receipt Date'])):
            series_toclean.append(row)
        elif not validate_ei(row['External Identification']):
            series_toclean.append(row)
        else:
            ei_text = row['External Identification']
            #Add semi colon to the end
            semi_tail = ";" * (53-ei_text.count(';'))
            row['External Identification'] = ei_text + semi_tail
            series_clean.append(row)
        
        sys.stdout.write("row completed: %s\r" % index)
        sys.stdout.flush()
    
    df_clean = pd.DataFrame(series_clean, columns=df_copy.columns)
    df_toclean = pd.DataFrame(series_toclean, columns=df_copy.columns)
    
    # Read the dataframe back into the excel sheet
    df_clean.to_csv(file_name_list[0] + "_CLEAN_DIRTYCOL" + file_name_list[1], index=False)
    # Read the dataframe back into the excel sheet
    df_toclean.to_excel(file_name_list[0] + "_TO CLEAN" + file_name_list[1], index=False)
    


# In[6]:


def parse_ei_column(dataframe, ei_columns):
    '''
    parse the external identificatino columns and return those columns
    '''
    
    # new data frame with split value columns
    dataframe_newcols = dataframe["External Identification"].str.split(";", n=53, expand=True) 
    
    try:
        dataframe_newcols.columns = ei_columns
    except Exception as err:
        print("Couldn't parse the file, error: {0}\n".format(err))
    #print(dataframe_newcols)
    
    # Dropping old Name columns 
    # dataframe.drop(columns =["External Identification"], inplace = True) 
    
    return dataframe_newcols
    

    


# In[7]:


def clean_col_k(col_k):
    '''    
    clean the col k by changing "core absorbants" into "core" 
    '''
    #create the dictionary for col k values
    valueDic = {
        "CORE ABSORBANTS - ABSORB GEL MAT (AGM)": "CORE - AGM",
        "CORE ABSORBANTS": "CORE"
    }
    
    group = re.match(r'CORE ABSORBANTS(.*)', col_k)
    if group is not None:
        group = group.group()
        if "AGM" in col_k: 
            col_k = valueDic["CORE ABSORBANTS - ABSORB GEL MAT (AGM)"]
        else: 
            col_k = valueDic["CORE ABSORBANTS"] + group[15:]
    return col_k


def clean_col_pickup_loc(pickup_loc):
    '''    
    clean the pickup loc by changing "core absorbants" into "core" 
    '''
    #create the dictionary for col k values
    valueDic = {
        "Market Product  - on line sourced": "Market Product - on line sourced",
    }
    
    group = re.match(r'Market Product  -(.*)', pickup_loc)
    if group is not None:
        pickup_loc = valueDic["Market Product  - on line sourced"]
    return pickup_loc

# In[8]:


def clean_cols(file_name_list):
    '''    
    parse the columns
    clean the material class K columns
    read the dataframe back to the excel sheets
    '''
    dataframe = pd.read_csv(file_name_list[0] + "_CLEAN_DIRTYCOL" + file_name_list[1])
    
    if (dataframe.empty):
        return
    
    # get the new ei col names from the sample sheet
    path ='/Users/luo.h.1/Procter and Gamble/BabyFem SOI Lab Portal - Documents/SOI data clean-up/Working Documents v1.0/DATA_UPLOAD/source/Sample.xlsx'
    book_eicolnames = pd.read_excel(path)
    ei_columns = book_eicolnames.columns
    
    
    # parse the dataframe
    dataframe_newcols = parse_ei_column(dataframe, ei_columns)
    
    # clean_col_k: TODO: REWRITE
    for index, row in dataframe_newcols.iterrows():
        row['Product Pickup Source'] = clean_col_pickup_loc(row['Product Pickup Source'])
        sys.stdout.write("row completed: %s\r" % index)
        sys.stdout.flush()        

    # for index in range(len(dataframe_newcols)):
    # dataframe_newcols.iloc[index]["Material Class"] = clean_col_k(dataframe_newcols.iloc[index]["Material Class"])
    
    
    # DELETEE
    # Readthe dataframe back into the excel sheet
    # dataframe_breakup = pd.concat([dataframe, dataframe_newcols], axis = 1)
    # dataframe_breakup.drop(columns =["External Identification"], inplace = True) 
    # dataframe_breakup.to_excel(file_name_list[0] + "_BREAKUP" + file_name_list[1], index=False)
    
    #dataframe_concat = pd.concat([dataframe,dataframe_newcols], axis=1)
    dataframe['External Identification'] = dataframe_newcols[:].apply(lambda x: ';'.join(x.fillna('')), axis = 1)
    
    
    print('{:.<50}{:.>20}'.format("fix the 'Material Class' col","Done"))
        
    # Read the dataframe back into the excel sheet
    #dataframe.to_excel(file_name_list[0] + "_CLEAN" + file_name_list[1], index=False)
    dataframe.to_csv(file_name_list[0] + "_CLEAN" + '.txt', index=None, sep='^', mode='a')
    

    # Read the dataframe back into the excel sheet
    #dataframe_newcols.to_excel(file_name_list[0] + "_eicol" + file_name_list[1], index=False)


# In[10]:


#################################
##             Main            ##
#################################

def main():
    '''
    INSTRUCTION:

    -> When you run the script, it will have a user prompt asking you to specify which directory you want to read the data from.
    -> It will also print out your current directory to help you navigate to the right directory in the next step
    -> Navigate(type in) to the right directory(folder) and hit enter.
    -> The program will go through and clean all the files in that folder
    -> An example putput:
    ======================================================================
    Hayley-TestData.xlsx                                                  
    --------------------   Cleaning up ... loading    --------------------
    make a copy of the file...........................................Done
    checking the file.................................................Done
    fix the 'Material Class' col......................................Done
    clean the _CLEAN sheet............................................Done
    clean the date format in the _CLEAN sheet.........................Done
    ======================================================================
    Hayley-TestData_CLEAN.xlsx                                            
    File does not need to be parsed
    ======================================================================
'''

    # get the desired directory from user input
    print("Current Working Directory: ", os.getcwd())

    # navigate to parent folder TODO: change it to direct path
    path = os.getcwd() + "/.."
    os.chdir(path)

    #selected_file_directory = input("Enter the path of your file: ")
    selected_file_directory = os.path.join(os.getcwd(), "weekly_updates")

    # change the current directory to the desired folder
    try: 
        os.chdir(selected_file_directory)
        print("...Directory changed")
        # OPTIONAL: print("Current Working Directory: ", os.getcwd())
    except OSError:
        print("...Failed to change the Current Working Directory") 


    file_list = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]

    #output = []
    # go through the list and read in every single spreadsheet in that directory
    for f in file_list:
        file_name_list = os.path.splitext(f)
        print('{:=>50}{:=>10}{:=>10}'.format("","",""))
        print('{:<50}{:>10}{:>10}'.format(f,"",""))

        # check if the file needs to be clean
        if file_name_list[0].endswith('_CLEAN') or file_name_list[0].endswith('_TO CLEAN'):
            print("File does not need to be parsed")
            continue
        # check if the file is a data file
        elif not file_name_list[1].endswith('xlsx') and not file_name_list[0].endswith('txt'):
            print("File is not a galab data file")
            continue
        # if yes, then start the cleaning
        else:
            print('{:-<20}{:^30}{:->20}'.format("","Cleaning up ... loading",""))
            try:
                copy_file(file_name_list)
                print('{:.<50}{:.>20}'.format("make a copy of the file","Done"))
            except Exception as err:
                print("Couldn't copy the file, error: {0}\n".format(err))
                continue
            
            check_copyover_file(file_name_list)
            # try:
            #     print('{:.<50}{:.>20}'.format("checking the file","Done"))
            # except Exception as err:
            #     print("Couldn't parse the file, error: {0}\n".format(err)) 
            #     continue

            try:
                clean_cols(file_name_list)
                print('{:.<50}{:.>20}'.format("clean the _CLEAN sheet","Done"))
            except Exception as err:
                print("Couldn't finish cleaning the cols, error: {0}\n".format(err))
                continue
            '''
            try:
                clean_date_format(file_name_list)
                print('{:.<50}{:.>20}'.format("clean the date format in the _CLEAN sheet","Done"))
            except Exception as err:
                print("Couldn't finish cleaning the date format in _CLEAN sheet, error: {0}\n".format(err))
                continue  
            '''
            try:
                os.remove(file_name_list[0] + "_COPY" + file_name_list[1])
                os.remove(file_name_list[0] + "_CLEAN_DIRTYCOL" + file_name_list[1])
                #shutil.move(file_name_list[0] + file_name_list[1], "./ORIN")
                #shutil.move(file_name_list[0] + "_CLEAN" + file_name_list[1], "./CLEAN")
                #shutil.move(file_name_list[0] + "_TO CLEAN" + file_name_list[1], "./TO_CLEAN")
                #shutil.move(file_name_list[0] + "_BREAKUP" + file_name_list[1], "./BREAKUP")
            except RuntimeError:
                print("Couldn't finish cleaning the date format in _CLEAN sheet, error: {0}\n".format(err))
                continue

    print('{:=>50}{:=>10}{:=>10}'.format("","","")) 

    return True


# In[11]:


#main()


# In[12]:


# file_list = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]
# print(file_list)


# In[ ]:





# In[ ]:




