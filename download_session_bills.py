#!/usr/bin/python -tt
# Stephen Muchovej

import os
import re
import sys
import urllib
import re
import pandas as pd
from pylegiscan import LegiScan
from bs4 import BeautifulSoup
import math
LEGISCAN_API_KEY = 'Your_api_key';


"""
   Program to access the state of CA website and download the text of 
   bills.
   
   It saves it to disk for further processing.

"""

legis = LegiScan(LEGISCAN_API_KEY);
# first we get the name of the sessions according to legiscan                                                                                
sessions = legis.get_session_list(state='ca');
# sessions is a list of 4 items, listed from most recent to oldest                                                                           
session_id = sessions[0]['session_id'];

billidlist = []
for counter, sessionlist in enumerate(sessions):
    session_id = sessions[counter]['session_id'];
    session_name = str(sessions[counter]['year_start']) + str(sessions[counter]['year_end'])
    
    # next let's get the full list of bills                                                                                              
    master_list = legis.get_master_list(session_id=sessions[counter]['session_id']);
    
    # we can now save that!!!                                                                                                            
    # first turn it into a pandas data frame:                                                                                            
    master_list_data_frame = pd.DataFrame.from_dict(master_list)
    fname = session_name + '_masterlistdataframe.save'
    master_list_data_frame.save('fname')
    # to load it, we do: master_list_data_frame = pd.load('masterlistdataframe.save')                                                    
    billidlist = (master_list_data_frame['bill_id'])

    for bill_id in billidlist:
    if not math.isnan(bill_id):
        bill_info = legis.get_bill(int(bill_id));
        if bill_info['texts']:
            bill_info_list.append(bill_info);
            filename = bill_info['texts'][0]['state_link'].encode('ascii', 'ignore')
            outfilename = '/Users/sjcm/professional/insight/project/data_download/notebook/bills/'+session_name+'/' + bill_info['bill_number'] + '.html'
            urllib.urlretrieve(filename, outfilename);





