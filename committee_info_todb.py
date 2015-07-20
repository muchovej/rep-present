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
   This program obtains information on the committees a certain legislator
   serves on and writes it to a database.
"""


# set up our two dataframes (which will become databases)

committeeinfo_db = pd.DataFrame(columns=['committee_name', 'committee_id'])
committeemembers_db = pd.DataFrame(columns=['committee_id', 'member_id', 'role']) # role is 3 for chair, 2 is vice chair, 1 for member.

committees = openstates.committees(state='ca')
committee_index = 0;
member_index    = 0;
for committee in committees:
    pdrow = pd.Series({'committee_name':committee['committee'].encode('ascii', 'ignore'), 'committee_id':committee['id']});
    committeeinfo_db.loc[committee_index] = pdrow;
    committee_index = committee_index + 1;

    detailedinfo = openstates.committee_detail(committee_id = committee['id'])
    for member in detailedinfo['members']:
        memnum = 1
        if member['role'] == 'Chair':
            memnum = 3;
        if member['role'] == 'Vice Chair':
            memnum = 2

        pdrow = pd.Series({'committee_id':committee['id'], 'member_id':member['leg_id'], 'role':memnum})
        committeemembers_db.loc[member_index] = pdrow
        member_index = member_index + 1

engine = create_engine("mysql+pymysql://root@localhost/legislator_db")
committeeinfo_db.to_sql('committees_table', engine,if_exists='replace')

committeemembers_db.to_sql('committeemembers_table', engine,if_exists='replace')
        



