'''
Created on Aug 30, 2013

@author: novpa01
'''
import logging
import sys
import importlib
from mmupdater.Settings import Settings
from mmupdater.UserError import UserError
from mmupdater.MMexDb import MMexDb
from mmupdater.CategoryAssigner import CategoryAssigner


# Parse settings file
settings = Settings('settings.ini')

if __name__ == '__main__':

    try:
        # initialize log level
        logging.basicConfig(level=settings.loglevel)
        
        # initialize the component to talk to the MMex database
        db = MMexDb(settings)
             
        # initialize category assignments
        cat_assigner = CategoryAssigner(settings, db)
        
        # get transactions with no categories
        transactions = db.get_transactions_with_no_categories()
        print("Found " + str(len(transactions)) + " transactions with no category assigned")
        
        # fill-in categories where we can
        cat_assigner.assign(transactions)
        
        # get just those transactions that have some category assigned
        assigned_transactions = [t for t in transactions if 'CATEGID' in t]
        print("Categories found for " + str(len(assigned_transactions)) + " transactions")
        
        # save them to the database
        db.update_transactions(assigned_transactions, cat_assigner)
        
        # successful exit
        exit(0)

    except UserError as e:
        sys.stderr.write("ERROR: " + str(e) + '\n')
        # non-zero to report error
        exit(1)
    
