import sunlight
import pandas as pd
from sunlight import openstates
from sqlalchemy import create_engine
from sqlalchemy.types import String 
import os
import sys
import re
import commands

"""
   Program to go from bill votes to db

"""


# set up our two dataframes (which will become databases)

voting_db = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'member_id', 'vote'])
ca_bills = openstates.bills(state='ca', search_window='term')
dbindex   = 0;
for i in range(len(ca_bills)):
    thisbilldetail = openstates.bill_detail(state='ca', session=ca_bills[i]['session'], bill_id = ca_bills[i]['bill_id']);
    keys           = thisbilldetail.keys()
    if 'votes' in keys:
        vvotes = thisbilldetail['votes']
        if vvotes != []:
            print 'bills has been voted on!!'
            vvotes = thisbilldetail['votes']   #this is a list with the votes on the bill -- there could be lots of amendments.
            billid = vvotes[0]['bill_id']
            sid    = vvotes[0]['id'] 
            for rollcall in vvotes:
                if 'eading' in rollcall['motion']:
                    # bill was voted on, and is not an amendment
                    for yay in rollcall['yes_votes']:
                        congid = yay['leg_id']
                        pdbillrow  = pd.Series({'bill_name':billid, 'sunlight_id':sid, 'member_id':congid, 'vote':1.0});
                        voting_db.loc[dbindex] = pdbillrow
                        dbindex = dbindex+1
                    for nay in rollcall['no_votes']:
                        congid = nay['leg_id']
                        pdbillrow  = pd.Series({'bill_name':billid, 'sunlight_id':sid, 'member_id':congid, 'vote':-1.0});
                        voting_db.loc[dbindex] = pdbillrow
                        dbindex = dbindex+1
                    for abstain in rollcall['other_votes']:
                        congid = abstain['leg_id']
                        pdbillrow  = pd.Series({'bill_name':billid, 'sunlight_id':sid, 'member_id':congid, 'vote':0});
                        voting_db.loc[dbindex] = pdbillrow
                        dbindex = dbindex+1          


# author table doesn't write out because of the 'sponsor_name' column, 
# let's take the sponsor_name out, and then write a different table to link the sunlight id to sponsor name
engine = create_engine("mysql+pymysql://root@localhost/legislator_db")
voting_db_save = voting_db.copy()
voting_db.to_sql('voting_table', engine,if_exists='replace')




