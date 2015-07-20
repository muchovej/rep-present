#!/usr/bin/python -tt
# Stephen Muchovej

import sunlight
import pandas as pd
from sunlight import openstates
from sqlalchemy import create_engine
from sqlalchemy.types import String
import os
import re
import sys
import urllib
import re
import pandas as pd
from bs4 import BeautifulSoup
import commands

"""
   This program downloads all the bill text files for the sessions listed in 
   'sessions' variable.  It accesses the openstates api for the bill list, and 
   then downloads them all and saves them to disk.  
   
   It cleans the bill text for numbers and punctuation.
   
   It also sets up pandas dataframes for each session, which can then be written
   out to a sql database.

"""

# set up the sessions and databases.
sessions = ['20092010', '20112012', '20132014', '20152016']
author_db = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'sponsor_name', 'sponsor_sunlight_id', 'session'])
billdetail_db = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'title', 'impact_clause',
                                      'scraped_subjects', 'official_subjects', 'summary_sunlight', 'summary_text', 'full_cleaned_text', 'session'])
authorindex = 0;
billindex   = 0;

for session in sessions:
    thissearch = 'session:'+session;
    ca_bills = openstates.bills(state='ca', search_window=thissearch)

    for index, ca_bill in enumerate(ca_bills):
        print str(index) + 'out of ' + str(len(ca_bills))
        thisbilldetail = openstates.bill_detail(state='ca', session=ca_bill['session'], bill_id = ca_bill['bill_id']);
        keys           = thisbilldetail.keys()

        if 'HR' not in thisbilldetail['bill_id']:
            
            billname       = ca_bill['bill_id'];
            billsid        = ca_bill['id'];
            billtitle      = ca_bill['title'];
            if '+impact_clause' in keys:
                billclause     = thisbilldetail['+impact_clause']
            else:
                billclause     = None;
            if 'scraped_subjects' in keys:
                billscraped    = thisbilldetail['scraped_subjects']
            else:
                billscraped  = None;
            billofficial   = thisbilldetail['subjects']
            if 'summary' in keys:
                billsummarysun = thisbilldetail['summary']
            else:
                billsummarysun = None
            billfilename = '/Users/sjcm/professional/insight/project/data_download/notebook/bills/' + session + '/' + billname.replace(" ", "") + '.html'

            file = open(billfilename, 'rU')
            if file:
                # remove the preamble of the html file
                soup = BeautifulSoup(file);
                if soup.pre:
                    # clean the text of punctuation and numbers.
                    body = soup.pre.text
                    cleaned_text = re.sub('[,.:\t\n-()"\'$]', ' ', body)
                    aa = re.search(r'20(.+) DIGEST (.+)', cleaned_text)
                    billsummarytext = aa.group(1)
                    cleanedtext = aa.group(2).lower()
                    cleanedtext = re.sub('[0123456789$]', ' ', cleanedtext)
                else:
                    cleanedtext = ''
                    billsummarytext = ''
            else:
                billsummarytext = ''
                cleanedtext = ''
                file.close()

            pdbillrow  = pd.Series({'bill_name':billname, 'sunlight_id':billsid, 'title':billtitle, 'impact_clause':billclause, 'scraped_subjects':billscraped,
                                    'official_subjects':billofficial, 'summary_insight':billsummarysun, 'summary_text':billsummarytext, 'full_cleaned_text':cleanedtext, 'session':session});
            billdetail_db.loc[billindex] = pdbillrow
            billindex = billindex+1

            sponsorlist    = thisbilldetail['sponsors'];
            for j in range(len(sponsorlist)):
                sponsorname = sponsorlist[j]['name']
                sponsorid   = sponsorlist[j]['leg_id']
                pdrow       = pd.Series({'bill_name':billname, 'sunlight_id': billsid, 'sponsor_name':sponsorname, 'sponsor_sunlight_id':sponsorid, 'session':session});
                author_db.loc[author_index] = pdrow
                author_index = author_index + 1

        else:
            print 'Skipping bill: ' + ca_bill['bill_id']  + 'which was created on' + thisbilldetail['created_at']


# write the dataframes out, so you can read them in and parse them later.
billdetail_db.save('allsessions_fullbilldetails_dataframe')
author_db.save('allsessions_authordetails_dataframe')
