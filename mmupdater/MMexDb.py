'''
Created on Aug 30, 2013

@author: novpa01
'''

import sqlite3
import logging
from mmupdater.UserError import UserError

class Account:
    '''
    Internal class for MMexDb to hold the information about accounts we have in the DB.
    '''
    accId = None
    number = None
    
class MMexDb:
    '''
    Implements the interactions with MMex Database
    '''

    __logger = logging.getLogger('MMexDB')
    
    __conn = None
    __accounts = []

    __fioAccountID = None
    __account_number = None
    
    def __init__(self, settings):
        '''
        
        '''
        self.__account_number = settings.account_number
        self.__conn = sqlite3.connect(settings.mmex_dbfile)
        self.__read_accounts()
        
    def save_transactions(self, transactions):
        for trans in transactions:
            self.__save_transaction(trans)
            
    def __save_transaction(self, trans):
        if 'TRANSACTIONNUMBER' in trans and self.__transaction_exists(trans['TRANSACTIONNUMBER']):
            print('Transaction ' + trans['TRANSACTIONNUMBER'] + ' exists already, skipping')
            print()
            return
        keys = ', '.join(trans.keys())
        questionmarks = ','.join('?' * len(trans.keys()))
        query = 'insert into checkingaccount_v1 (' + keys + ') values (' + questionmarks + ')'
        print('Amount ' + ('-' if trans['TRANSCODE'] == 'Withdrawal' else '') + str(trans['TOTRANSAMOUNT']))
        if 'NOTES' in trans:
            print(self.__longest_desc(trans['NOTES']))
        print() 
        c = self.__conn.cursor()
        c.execute(query, list(trans.values()))
        self.__conn.commit()
    
    def __longest_desc(self, notesField):
        stringlist = notesField.split(';') 
        maxLen = max(map(len, stringlist))   
        return [s for s in stringlist if len(s) == maxLen][0].strip("\n\r\t ") 
        
    def __transaction_exists(self, transactionNumber):
        transid = None
        c = self.__conn.cursor()
        result = c.execute('select TRANSID, "dummy" from Checkingaccount_v1 WHERE TRANSACTIONNUMBER = ?', (transactionNumber,))
        for tid,_ in result:
            transid = tid
        return not transid == None
        
    def __read_accounts(self):
        c = self.__conn.cursor()
        result = c.execute('select  ACCOUNTID,  ACCOUNTNUM from accountlist_v1 WHERE STATUS = "Open"')
        for accountid, num in result:
            if num:
                acc = Account()
                acc.accId = accountid
                acc.number = num
                self.__accounts.append(acc)
            
        self.__logger.debug("Accounts: " + str(self.__accounts))
                    
    def get_our_accountid(self):
        ourAccountNumber = self.__account_number
        ourAccounts = [acc for acc in self.__accounts if acc.number == ourAccountNumber]
        if not ourAccounts:
            raise UserError("Account no. " + ourAccountNumber + " does not exist")
        return ourAccounts[0].accId
    
    def get_accountid(self, account_number):
        matching_accounts = [acc for acc in self.__accounts if acc.number == account_number]
        if (len(matching_accounts) > 1):
            raise UserError("There are multiple accounts in MoneyManagerEx with the same number:", account_number)
        return matching_accounts[0].accId if len(matching_accounts) == 1 else None
    
    def get_categoryid(self, category_name):
        categoryid = None
        c = self.__conn.cursor()
        result = c.execute('select CATEGID, "dummy" from Category_v1 WHERE CATEGNAME = ?', (category_name,))
        for cid,_ in result:
            categoryid = cid
        if categoryid == None:
            raise UserError("Category %s not found" % category_name)
        return categoryid
                            
    def get_subcategoryid(self, categ_id, subcategory_name):
        categoryid = None
        c = self.__conn.cursor()
        result = c.execute('select SUBCATEGID, "dummy" from SubCategory_v1 WHERE CategID = ? AND SUBCATEGNAME = ?', (categ_id, subcategory_name,))
        for cid,_ in result:
            categoryid = cid
        if categoryid == None:
            raise UserError("SubCategory %s not found within category #%s" % (subcategory_name, categ_id))
        return categoryid
