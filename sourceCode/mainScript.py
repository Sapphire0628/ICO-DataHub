#%%

from DatabaseManager.DbManager import DatabaseManager
from ScraperScript.config import *


# Initialize the DatabaseManager
db_manager = DatabaseManager("DB/data.db")
#DatabaseManager.execute_query(db_manager, "ALTER TABLE tokens ADD creator TEXT;")
#DatabaseManager.drop_table(db_manager, "twitter_users")
#DatabaseManager.create_twitter_users_table(db_manager)
