#!/usr/bin/env python
# coding: utf-8

# In[1]:

import subprocess
subprocess.call(['pip', 'install', 'openpyxl'])


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
    elif not (ei_text.startswith('YES') or ei_text.startswith('NO')):
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
    if type(row_cell) is pd._libs.tslibs.timestamps.Timestamp or datetime:
        return True
    else:
        #print("none of the above:", row_cell)
        return False
        
# TODO: Test cases: run quick tests on the validation functions


# In[5]:


import time


def check_copyover_file(file_name_list):
    """Create a workbook 
    # run through spreadsheet row by row and determine if a row need to be cleaned
    # create a new file with TO_CLEAN at the end
    """
    # open the work sheet
    df_copy = pd.read_excel(file_name_list[0] + "_COPY" + file_name_list[1])
    
    if len(df_copy.columns) > 19:
        df_copy = df_copy.loc[:, 'Customer':'LOQ']
    df_clean = pd.DataFrame(columns=df_copy.columns)
    df_toclean = pd.DataFrame(columns=df_copy.columns)
    
    # check the clean sheet row by row: valid date? valid external identification col?
    start_point=0
    length = len(df_copy)
    for index in range(length):
        # if the row reaches 100000 per sheet
        if (index-start_point <= 49999) :
            if not (validate_date(df_copy.iloc[index]['Report Created']) 
                and validate_date(df_copy.iloc[index]['Sample Fixed Date']) 
                and validate_date(df_copy.iloc[index]['Sample Receipt Date'])):
                df_toclean = df_toclean.append(df_copy.iloc[index])
            elif not validate_ei(df_copy.iloc[index]['External Identification']):
                df_toclean = df_toclean.append(df_copy.iloc[index])
            else:
                df_clean = df_clean.append(df_copy.iloc[index])
                # if we reach the end of our sheet, reads out the output
            if (index == length-1):
                start_point=index
                # Read the dataframe back into the excel sheet
                df_clean.to_excel(file_name_list[0] + "_" + str(index)  + "_CLEAN-DIRTYCOL" + file_name_list[1], index=False)
                # Read the dataframe back into the excel sheet
                df_toclean.to_excel(file_name_list[0] + "_" + str(index)  + "_TO CLEAN"+ file_name_list[1], index=False)
                df_clean = pd.DataFrame(columns=df_copy.columns)
                df_toclean = pd.DataFrame(columns=df_copy.columns)
        # if yes, then reset the start_point and then export the rows into excel sheets
        elif (index-start_point>49999) or (index==length):
            start_point=index
            # Read the dataframe back into the excel sheet
            df_clean.to_excel(file_name_list[0] + "_" + str(index)  + "_CLEAN-DIRTYCOL" + file_name_list[1], index=False)
            # Read the dataframe back into the excel sheet
            df_toclean.to_excel(file_name_list[0] + "_" + str(index)  + "_TO CLEAN"+ file_name_list[1], index=False)
            df_clean = pd.DataFrame(columns=df_copy.columns)
            df_toclean = pd.DataFrame(columns=df_copy.columns)
        
        sys.stdout.write("row completed: %s\r" % index)
        sys.stdout.flush()
    
    #df_clean.replace('', np.nan)
    #df_toclean.replace('', np.nan)


# In[6]:


def parse_ei_column(dataframe, ei_columns):
    '''
    parse the external identification columns and return those columns
    '''
    
    dataframe["External Identification"] = dataframe["External Identification"].apply(lambda x: x + ';-'*(53-x.count(';')))
    
    # new data frame with split value columns
    dataframe_newcols = dataframe["External Identification"].str.split(";", n=53, expand=True) 
    
    try:
        dataframe_newcols.columns = ei_columns
    except Exception as err:
        print("Couldn't parse the file, error: {0}\n".format(err))
    
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


# In[8]:


def clean_cols(file_name_list):
    '''    
    parse the columns
    clean the material class K columns
    read the dataframe back to the excel sheets
    '''
    dataframe = pd.read_excel(file_name_list[0] + file_name_list[1])
    
    if (dataframe.empty):
        return
    
    # get the new ei col names from the sample sheet
    path ='./source/Sample.xlsx'
    book_eicolnames = pd.read_excel(path)
    ei_columns = book_eicolnames.columns
    
    
    # parse the dataframe
    dataframe_newcols = parse_ei_column(dataframe, ei_columns)
    
    # clean_col_k
    for index in range(len(dataframe_newcols)):
        dataframe_newcols.iloc[index]["Material Class"] = clean_col_k(dataframe_newcols.iloc[index]["Material Class"])
        sys.stdout.write("row completed: %s\r" % index)
        sys.stdout.flush()        
    
    
    # DELETEE
    # Readthe dataframe back into the excel sheet
    #dataframe_breakup = pd.concat([dataframe, dataframe_newcols], axis = 1)
    #dataframe_breakup.drop(columns =["External Identification"], inplace = True) 
    #dataframe_breakup.to_excel(file_name_list[0].split('_')[0] + '_' + file_name_list[0].split('_')[1] + "_BREAKUP" + file_name_list[1], index=False)
    
    #dataframe_concat = pd.concat([dataframe,dataframe_newcols], axis=1)
    dataframe['External Identification'] = dataframe_newcols[:].apply(lambda x: ';'.join(x.fillna('')), axis = 1)
    
    
    print('{:.<50}{:.>20}'.format("fix the 'Material Class' col","Done"))
        
    # Read the dataframe back into the excel sheet
    dataframe.to_excel(file_name_list[0].split('_')[0] + '_' + file_name_list[0].split('_')[1] + "_CLEAN" + file_name_list[1], index=False)
    

    # Read the dataframe back into the excel sheet
    #dataframe_newcols.to_excel(file_name_list[0] + "_eicol" + file_name_list[1], index=False)


# In[9]:


# In[10]:


#################################
##       separate files        ##
#################################


def separate_files():
    
    '''
    INSTRUCTION:

    -> When you run the script, it will have a user prompt asking you to specify which directory you want to read the data from.
    -> It will also print out your current directory. This is to help you navigate to the directory you actually want
    -> Navigate(=type in) to the right directory(=folder name) and hit enter.
    -> The program will go through the folder and clean all the files
    -> An example putput:
    ======================================================================
    TestData.xlsx                                                  
    --------------------   Cleaning up ... loading    --------------------
    make a copy of the file...........................................Done
    checking the file.................................................Done
    fix the 'Material Class' col......................................Done
    ======================================================================
    TestData_CLEAN.xlsx                                            
    File does not need to be parsed
    ======================================================================
    '''

    # get the desired directory from user input
    print("Current Working Directory: ", os.getcwd())
    #selected_file_directory = input("Enter the path of your file: ")
    selected_file_directory = os.getcwd() + "/../quarterly_updates"

    # change the current directory to the desired folder
    try: 
        os.chdir(selected_file_directory)
        print("...Directory changed")
        print("Current Working Directory now: ", os.getcwd())
    except OSError:
        print("...Failed to change the Current Working Directory") 


    file_list = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]

    # go through the list and read in every single spreadsheet in that directory
    for f in file_list:
        file_name_list = os.path.splitext(f)
        print('{:=>50}{:=>10}{:=>10}'.format("","",""))
        print('{:<50}{:>10}{:>10}'.format(f,"",""))

        # check if the file needs to be clean,if yes, then start the cleaning
        if file_name_list[0].endswith('_CLEAN') or file_name_list[0].endswith('_TO CLEAN') :
            print("File does not need to be parsed")
            continue
        else:
            # copy the original file
            try:
                copy_file(file_name_list)
                print('{:.<50}{:.>20}'.format("make a copy of the file","Done"))
            except Exception as err:
                print("Couldn't copy the file, error: {0}\n".format(err))
                continue

            print('{:-<20}{:-^30}{:->20}'.format("","",""))

            # parse the file into _CLEAN/TO_CLEAN files
            try:
                check_copyover_file(file_name_list)
                print('{:.<50}{:.>20}'.format("checking the file","Done"))
            except Exception as err:
                print("Couldn't parse the file, error: {0}\n".format(err)) 
                continue
        
        # romove the copy
        try:
            os.remove(file_name_list[0] + "_COPY" + file_name_list[1])
            shutil.move(file_name_list[0] + file_name_list[1], "./ORIG")
        except RuntimeError:
            print("Couldn't delete the _COPY sheet, error: {0}\n".format(err))
            continue

    print('{:=>50}{:=>10}{:=>10}'.format("","",""))  
        


# In[11]:


def cleanup_files():
    # get the desired directory from user input
    print("Current Working Directory: ", os.getcwd())
    #selected_file_directory = input("Enter the path of your file: ")
    selected_file_directory = os.getcwd() + "/../quarterly_updates"

    # change the current directory to the desired folder
    try: 
        os.chdir(selected_file_directory)
        print("...Directory changed")
        print("Current Working Directory now: ", os.getcwd())
    except OSError:
        print("...Failed to change the Current Working Directory") 


    file_list = []
    # r=root, d=directories, f = files
    for f in listdir(os.getcwd()):
        if ('.xlsx' in f) and ('CLEAN-DIRTYCOL' in f):
            file_list.append(os.path.join(f))
            
    # go through the list and read in every single spreadsheet in that directory
    print(file_list)
    for f in file_list:
        file_name_list = os.path.splitext(f)
        print('{:=>50}{:=>10}{:=>10}'.format("","",""))
        print('{:<50}{:>10}{:>10}'.format(f,"",""))
        # clean the cols of the file
        clean_cols(file_name_list)
        '''try:
            clean_cols(file_name_list)
            print('{:.<50}{:.>20}'.format("clean the _CLEAN sheet","Done"))
        except Exception as err:
            print("Couldn't finish cleaning the cols, error: {0}\n".format(err))
            continue
        '''
        print('{:-<20}{:-^30}{:->20}'.format("","",""))

        # move all the files into the correct folder
        try:
            #if os.path.isfile(file_name_list[0].split('_')[0] + '_' + file_name_list[0].split('_')[1] + "_CLEAN" + file_name_list[1]):
                #shutil.move(file_name_list[0].split('_')[0] + '_' + file_name_list[0].split('_')[1] + "_CLEAN" + file_name_list[1], "./CLEAN")
                #shutil.move(file_name_list[0].split('_')[0] + '_' +file_name_list[0].split('_')[1] + "_BREAKUP" + file_name_list[1], "./BREAKUP")
            shutil.move(file_name_list[0].split('_')[0] + '_' +file_name_list[0].split('_')[1] + "_TO CLEAN" + file_name_list[1], "./TO_CLEAN")

            print('{:.<50}{:.>20}'.format("sort the files into the correct folder","Done"))
        except:
            print("Couldn't move the files into the correct folder, or the file has been replaced in the designated directory")
            continue



    print('{:=>50}{:=>10}{:=>10}'.format("","",""))   
        


# # In[12]:
# print("Choose one of the following procedure you would like to process on the quarterly data? 1: separate files, 2: clean up files")
# response = input("Enter your option: ")
# print(response)
# if (response == '1'):
#     separate_files()
# elif (response == '2'):
#     print("option 2 produced")
#     cleanup_files()


# In[ ]:





# In[ ]:




