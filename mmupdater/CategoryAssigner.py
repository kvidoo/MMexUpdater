'''
Created on Sep 24, 2013

@author: novpa01
'''
from mmupdater.UserError import UserError
import logging

class CategoryAssigner():
    '''
    Reads the transactions and assigns MoneyManager categories appropriately.
    '''
    categories = None

    __logger = logging.getLogger('MMexDB')
    
    def __init__(self, settings, db):
        '''
        Constructor
        '''
        self.categories = settings.categories
        for cat in self.categories:
            if cat["category"] != '*':
                cat["category_id"] = db.get_categoryid(cat["category"])
                if cat["subcategory"]:
                    cat["subcategory_id"] = db.get_subcategoryid(cat["category_id"], cat["subcategory"])

    
    def assign(self, transactions):
        matches = 0
        for trans in transactions:
            match = self.__find_match(trans)
            if match:
                self.__apply_match(trans, match)
                matches += 1
        self.__logger.debug("Matches found: " + str(matches))
            
    def __find_match(self, trans):
        for cat in self.categories:
            if cat['category'] != '*':
                for field, operator, value in cat['conditions']:
                    if operator != 'contains':
                        raise UserError('Only contains operator is supported right now')
                    if not field in trans:
                        raise UserError('Field %s is not supported' % field)
                    if trans[field].find(value) >= 0:
                        return cat
        return None
    
    def __apply_match(self, trans, match):
        if 'category_id' in match:
            trans['CATEGID'] = match['category_id']
        if 'subcategory_id' in match:
            trans['SUBCATEGID'] = match['subcategory_id']
        if 'status' in match:
            trans['STATUS'] = match['status']
            
    def get_name(self, category_id, subcategory_id):
        for cat in self.categories:
            if cat['category_id'] == category_id and (not(subcategory_id) or cat['subcategory_id'] == subcategory_id):
                return cat['category'] + ":" + cat['subcategory']
        return ""    