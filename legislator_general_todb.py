#!/usr/bin/python -tt
# Stephen Muchovej

import sunlight
import pandas as pd
from sunlight import openstates
from sqlalchemy import create_engine
from sqlalchemy.types import String 

"""
   This program obtains general information on the legislators in CA,
   downloads their pictures, and writes all this information in a mysql 
   database.
"""

ca_legs = openstates.legislators(state='ca')

# next we want to make a pandas data frame with  

dftest = pd.DataFrame(columns=['id', 'first_name', 'last_name', 'party', 'legislative_body', 'district_id', 'phone_number', 'webpic', 'localpic'])
for i in range(len(ca_legs)):
    photo = 'photos/' + str(ca_legs[i]['id']) + '.jpg'
    if len(ca_legs[i]['offices']) > 0:
        dftest.loc[i] = pd.Series({'id':ca_legs[i]['id'], 
                                   'first_name':ca_legs[i]['first_name'],
                                   'last_name':ca_legs[i]['last_name'],
                                   'party':ca_legs[i]['party'],
                                   'legislative_body':ca_legs[i]['chamber'],
                                   'district_id':ca_legs[i]['district'],
                                   #                                'office_address':ca_legs[i]['offices'][0]['address'],
                                   'phone_number':ca_legs[i]['offices'][0]['phone'],
                                   'webpic':ca_legs[i]['photo_url'],
                                   'localpic':photo})
    else:
        dftest.loc[i] = pd.Series({'id':ca_legs[i]['id'], 
                                   'first_name':ca_legs[i]['first_name'],
                                   'last_name':ca_legs[i]['last_name'],
                                   'party':ca_legs[i]['party'],
                                   'legislative_body':ca_legs[i]['chamber'],
                                   'district_id':ca_legs[i]['district'],
                                   #                                'office_address':ca_legs[i]['offices'][0]['address'],
                                   'phone_number':None,
                                   'webpic':ca_legs[i]['photo_url'],
                                   'localpic':photo})

# write it out to a sequel file:
legislator_table = dftest;

#engine = create_engine("mysql+pymysql://root@localhost/legislator_db")
#legislator_table.to_sql('legislator_table', engine,if_exists='replace')


# download the photos
import os
import re
import sys
import urllib

pics2download = legislator_table['webpic']
pics2name     = legislator_table['photo_url']

for img_url, localname in zip(pics2download, pics2name):
    urllib.urlretrieve(img_url, localname)






