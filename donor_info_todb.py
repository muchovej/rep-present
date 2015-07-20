#!/usr/bin/python -tt
# Stephen Muchovej

apikey = 'your_api_key'
import sys
from sunlight import openstates
from transparencydata import TransparencyData
td = TransparencyData(apikey)
import pandas as pd

"""
   This program obtains general information on the donors to a particular legislator.
   It first obtains all the legislators for the state of CA, and then 
   cycles through all of those to keep relevant information and put it in a pandas
   data frame.  

   It then writes that pandas dataframe to a mysql database
"""

# obtain the list of legislators in teh current session
all_legs = openstates.legislators(state='ca')

# obtain all donor information for the particular legislator in the past 3 years.
index = -1
for leg in all_legs:
    thiscontribution = td.contributions(cycle='2013|2014|2015', recipient_ft=leg['last_name'].lower(), recipient_state='ca')
    df = pd.DataFrame(thiscontribution)
    # df.columns has the name of the column
    index = index + 1
    print index
    if  not df.empty:
        # remove frames which are not of interest.
        del df['candidacy_status']
        del df['committee_ext_id']
        del df['committee_party']
        del df['contributor_ext_id']
        del df['cycle']
        del df['date']
        del df['district_held']
        del df['filing_id']
        del df['is_amendment']
        del df['recipient_state_held']
        del df['seat']
        del df['seat_held']
        del df['seat_result']
        del df['seat_status']
        del df['transaction_id']
        del df['transaction_namespace']
        del df['transaction_type']
        del df['transaction_type_description']
        # we also want to cut on the name of the legislator
        df1 = df.copy()
        df = df1[ df1['recipient_name'].str.contains(leg['first_name'].split()[0].upper())]
        # lastly we add the sunlight id for this person.
        df['sunlight_id'] = leg['id']
        if index==0:
            fulldf = df.copy()
            del df
        else:
            fulldf.append(df)
            

# write out the result to a mysql database.
engine = create_engine("mysql+pymysql://root@localhost/legislator_db")
fulldf.to_sql('donor_table', engine,if_exists='replace')

