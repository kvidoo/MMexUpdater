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


def find_bank_class(bank_type):
    module = importlib.import_module('Bank'+bank_type, 'mmupdater')
    class_ = getattr(module, 'Bank'+bank_type, None)
    if (class_ is None):
        raise UserError("Class", 'Bank'+bank_type, "not found in mmupdater module - is the bank_type property configured correctly in settings.ini?")
    return class_


if __name__ == '__main__':

    try:
        # initialize log level
        logging.basicConfig(level=settings.loglevel)
        
        # initialize the component to talk to the MMex database
        db = MMexDb(settings)
        
        # initialize access to the bank
        class_ = find_bank_class(settings.bank_type)
        bank = class_(settings, db)
        
        # initialize category assignments
        cat_assigner = CategoryAssigner(settings, db)
        
        # get transactions from bank
        transactions = bank.get_transactions()
        
        # fill-in categories where we can
        cat_assigner.assign(transactions)
        
        # save them to the database
        db.save_transactions(transactions)
        
        # successful exit
        exit(0)

    except UserError as e:
        sys.stderr.write("ERROR: " + str(e) + '\n')
        # non-zero to report error
        exit(1)
    
