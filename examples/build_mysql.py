""" 
Make sure .env is setup with following variables:
MYSQL_HOST=ipadress or webhost
MYSQL_PORT=3306
MYSQL_DB ='trading'
MYSQL_USER=''
MYSQL_PW='' 
"""

import os

from pymysql import IntegrityError
from dotenv import load_dotenv
load_dotenv()

import mysql.connector
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from hobbytrader.github import Github
from hobbytrader.database import generate_ID

class DBObject:
    def __init__(self) -> None:
        self.host = os.getenv("MYSQL_HOST")
        self.port = os.getenv("MYSQL_PORT")
        self.database = os.getenv("MYSQL_DB")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PW")
        self.connection = None
        self.cursor = None

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except mysql.connector.Error as error:
            print("Error connecting to MySQL database:", error)
            return False        
        

    def _cursor(self):
        if not self.connection:
            self.cursor = None
            return False
        self.cursor = self.connection.cursor()
        return True

    def _disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def add_and_ignore_duplicate(self, id, dt_time, symbol, open, high, low, close, volume):
        # Make sure self.connection is not None
        sql_insert = """
            INSERT IGNORE INTO prices (ID, Datetime, Symbol, Open, High, Low, Close, Volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        if self.cursor is None:
            return False
        try:
            self.cursor.execute(sql_insert, (id, dt_time, symbol, open, high, low, close, volume ))
            return True
        except mysql.connector.Error as error:
            print("Error inserting record into MySQL Users:", error)
            return False        
    

def main(github_repo, sub_folder, starts_with):
    print(f'\n\nStep 01: Starting DB generation/update process')

    # Step 00 : Establish database connection
    db = DBObject()
    
    # Step 01 : Get csv files to load
    github_object = Github(repository=github_repo)
    files_to_load = github_object.file_links(folder=sub_folder, starts_with=starts_with)
    print(f'Step 01: {len(files_to_load)} files detected in github repo: {github_repo}/{sub_folder}')
    print(f'         First file: {files_to_load[0]}, last file: {files_to_load[-1]}')

    # BUG Seems to fail when double on ID exist
    # -----------------------------------------
    if not db._connect():
        print('No database connection established... STOPING')
        return
    
    if not db._cursor():
        print('No database cursor established... STOPING')
        return

    #for file in files_to_load[0:5]:
    for file in files_to_load:
        data_df = github_object.load_csv(file)
        data_df = generate_ID(data_df)

        data_df = data_df.set_index('ID')
        data_df.Datetime = pd.to_datetime(data_df.Datetime)
        data_df = data_df[['Datetime','Symbol','Close','High','Low','Open','Volume']] # Get rid of 'Adj Close'
        print(f'{len(data_df):09}, {file}')
        
        if db.cursor is not None:
            count = 0
            commits_count = 0
            for index, row in data_df.iterrows():
                #print(index, row.Datetime)
                db.add_and_ignore_duplicate(index, row.Datetime, row.Symbol, row.Open, row.High, row.Low, row.Close, row.Volume)
                if count > 1000:
                    db.connection.commit()
                    count = 0
                    commits_count += 1000
                    print(f'Commits: {commits_count}')
                else:
                    count += 1
            db.connection.commit()
        
    db._disconnect()

if __name__ == '__main__':
    file_list = [
        #'TSX-2023-09-22',
        'TSX-2023-09-23',
        'TSX-2023-09-24',
        'TSX-2023-09-25',
        'TSX-2023-09-26',
        'TSX-2023-09-27',
        'TSX-2023-09-28',
        'TSX-2023-09-29',        
        'TSX-2023-09-30'
    ]
    
    
    repo = 'DATASETS'
    subfolder = '/DAILY'
    starts_with = 'TSX-2023-08-0'
    #starts_with = name
    main(repo, subfolder, starts_with)  

    