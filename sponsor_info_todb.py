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
   Program to get the bill sponsor information and write it to db.

"""

author_db = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'sponsor_name', 'sponsor_sunlight_id'])
billdetail_db = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'title', 'impact_clause', 
                                      'scraped_subjects', 'official_subjects', 'summary_sunlight', 'summary_text', 'full_cleaned_text'])

ca_bills = openstates.bills(state='ca', search_window='term')
authorindex = 0;
billindex   = 0;
for i in range(len(ca_bills)):
    thisbilldetail = openstates.bill_detail(state='ca', session=ca_bills[i]['session'], bill_id = ca_bills[i]['bill_id']);
    keys           = thisbilldetail.keys()

    if (thisbilldetail['created_at'] < '2015-06-01') and ('HR' not in thisbilldetail['bill_id']):

        billname       = ca_bills[i]['bill_id'];
        billsid        = ca_bills[i]['id'];
        billtitle      = ca_bills[i]['title'];
        billclause     = thisbilldetail['+impact_clause']
        if 'scraped_subjects' in keys:
            billscraped    = thisbilldetail['scraped_subjects']
        else:
            billscraped  = None;
        billofficial   = thisbilldetail['subjects']
        billsummarysun = thisbilldetail['summary']
        billfilename = '/Users/sjcm/professional/insight/project/data_download/notebook/bills/' + billname.replace(" ", "") + '.html'

        file = open(billfilename, 'rU')
        if file:
            soup = BeautifulSoup(file);
            body = soup.pre.text
            cleaned_text = re.sub('[,.:\t\n-()"\'$]', ' ', body)
            aa = re.search(r'201(.+) DIGEST (.+)', cleaned_text)
            billsummarytext = aa.group(1)
            cleanedtext = aa.group(2).lower()
            cleanedtext = re.sub('[0123456789$]', ' ', cleanedtext)
        else:
            billsummarytext = ''
            cleanedtext = ''
            file.close()
       
        pdbillrow  = pd.Series({'bill_name':billname, 'sunlight_id':billsid, 'title':billtitle, 'impact_clause':billclause, 'scraped_subjects':billscraped,
                               'official_subjects':billofficial, 'summary_insight':billsummarysun, 'summary_text':billsummarytext, 'full_cleaned_text':cleanedtext});
        billdetail_db.loc[billindex] = pdbillrow
        billindex = billindex+1

        sponsorlist    = thisbilldetail['sponsors'];
        for j in range(len(sponsorlist)):
            sponsorname = sponsorlist[j]['name']
            sponsorid   = sponsorlist[j]['leg_id']
            pdrow       = pd.Series({'bill_name':billname, 'sunlight_id': billsid, 'sponsor_name':sponsorname, 'sponsor_sunlight_id':sponsorid});
            author_db.loc[author_index] = pdrow
            author_index = author_index + 1
   
    else:
        print 'Skipping bill: ' + ca_bills[i]['bill_id']  + 'which was created on' + thisbilldetail['created_at']



engine = create_engine("mysql+pymysql://root@localhost/legislator_db")

billdetail_db_save = billdetail_db.copy();
del billdetail_db['full_cleaned_text']
del billdetail_db['official_subjects']

billdetail_db.to_sql('billdetail_table', engine, if_exists='replace')
# this just made the table without those two rows!!!

# next let's make a data frame with bill_name and full_cleaned_text to save in pandas.
billtext_df = billdetail_db_save.copy();
del billtext_df['impact_clause']
del billtext_df['summary_sunlight']
del billtext_df['summary_text']
del billtext_df['scraped_subjects']
del billtext_df['title']
del billtext_df['official_subjects']

billtext_df.save('billtext_dataframe')



# author table doesn't write out because of the 'sponsor_name' column, 
# let's take the sponsor_name out, and then write a different table to link the sunlight id to sponsor name
author_db_save = author_db.copy()
del author_db['sponsor_name']
author_db.to_sql('bill_author_table', engine,if_exists='replace')


# we don't actually need the name.  to tie the name to the bill_author, all we have to do is join bill_author_table with legislator_table



