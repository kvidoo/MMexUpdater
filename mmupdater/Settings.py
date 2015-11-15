'''
Created on Sep 12, 2013

@author: novpa01
'''
import configparser
import logging
from mmupdater.UserError import UserError
import os
from urllib.parse import urlparse

class Settings:
    '''
    classdocs
    '''
    config = None


    def __init__(self, configFile):
        if not os.path.isfile(configFile):
            raise UserError("Cannot find configuration file: ", configFile)
        
        self.config = configparser.ConfigParser()
        with open(configFile, mode='r', encoding='utf-8') as conf_file:
            self.config.read_file(conf_file)
    
    def __getbanksection(self):
        return 'bank-'+self.bank_type

    @property
    def loglevel(self):
        level = self.config['global']['loglevel']
    
        if level:
            if level.lower() == 'debug':
                return logging.DEBUG
            elif level.lower() == 'info':
                return logging.INFO
            elif level.lower() == 'warn':
                return logging.WARN
            elif level.lower() == 'error':
                return logging.ERROR
            elif level.lower() == 'fatal':
                return logging.FATAL
            else:
                print('Unknown value in settings.ini for log_level =', level)
        
        print('Setting log level to default: WARN')
        return logging.WARN        

    @property
    def bank_type(self):
        result = self.config.get('global', 'bank_type', fallback=None)
        if not result:
            raise UserError("bank_type is not set in the config file: section: global, key: bank_type")
        return result

    @property
    def mmex_dbfile(self):
        result = self.config.get('mmex', 'dbfile', fallback=None)
        if not result:
            raise UserError("Location to the MMex DB file is missing in the config file: section: mmex, key: dbFile")
        return result
    
    @property
    def transactions_url(self):
        result = self.config.get(self.__getbanksection(), 'transactions_url', fallback=None)
        if not result:
            raise UserError("transactionsUrl is missing in [bank] section in the configuration file")
        self.__validateUrl(result)
        return result
    
    @property
    def revertbyid_url(self):
        result = self.config.get(self.__getbanksection(), 'revertbyid_url', fallback=None)
        if not result:
            raise UserError("revertByIDUrl is missing in [bank] section in the configuration file")
        self.__validateUrl(result)
        return result

    def __validateUrl(self, url):
        scheme = urlparse(url)[0]
        if scheme != 'https':
            raise UserError("Only https scheme is supported in url to the bank")
        
    @property
    def certificate_file(self):
        result = self.config.get(self.__getbanksection(), 'certificate_file', fallback=None)
        if not result:
            raise UserError("certificateFile is missing in [bank] section in the configuration file")
        if not os.path.isfile(result):
            raise UserError("Certificate file " + result + " not found")
        return result
    
    @property
    def force_revert_to_id(self):
        result = self.config.get(self.__getbanksection(), 'force_revert_to_id', fallback=None)
        return result
        
    @property
    def revert_to_last_success(self):
        return self.config.get(self.__getbanksection(), 'revert_to_last_success', fallback=False)
        
    @property
    def account_number(self):
        result = self.config.get('mmex', 'account_number', fallback=None)
        if not result:
            raise UserError("account_number is missing in [mmex] section in the configuration file")
        return result
    
    @property
    def categories(self):
        result = []
        cat_sections = (sec for sec in self.config.sections() if sec.startswith('category-'))
        for sec in cat_sections:
            categories = sec[9:].split(':', 2)
            categories.append(None)
            status = self.config[sec]['status']
            conditions = []
            counter = 1
            while 'field'+str(counter) in self.config[sec]:
                conditions.append((self.config[sec]['field'+str(counter)],
                                   self.config[sec]['operator'+str(counter)],
                                   self.config[sec]['value'+str(counter)]))
                counter = counter + 1
            result.append({'category':categories[0], 'subcategory':categories[1],
                           'status':status, 'conditions':conditions})
        return result