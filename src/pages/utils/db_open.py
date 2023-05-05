# Created By Mohamed Galal Elgemeie
# all rights reserved

import pandas as pd
from sqlalchemy import create_engine
import mysql.connector as mc
import json
from .settings import config_data


def truncate(table):
    """
    Used to truncate the specified table contents from the
    database.
    parameters:
        table: database's table name to be selected 
    """
    with  mc.connect(host="localhost",user='root',passwd=config_data['sql_server_passcode'],database=config_data['db_name']) as db:
        cursor=db.cursor()
        cursor.execute(f"TRUNCATE TABLE {table}")


def run(command):
    """
    Used to return the result of a SQL command query
    as a pandas dataframe object
    parameters:
        command: database's table name to be selected 
    return:
        query: pandas dataframe object
    """
    query=pd.read_sql(sql=command,con=engine)
    return query


def look(table):
    """
    Used to return the specified table's content from the
    database and returns a pandas dataframe of that table.
    parameters:
        table: database's table name to be selected 
    return:
        query: pandas dataframe object
    """    
    query=pd.read_sql(sql=f"SELECT * FROM {table}",con=engine)
    return query


def to_db(table,df,exist):
    """
    Used to append/overwrite a pandas dataframe object onto 
    a SQL table from database
    """

    # start connection to database
    with engine.begin() as connection:
        df.to_sql(table,con=connection,if_exists=exist,index=False)



if __name__ != "__main__":

    with open(f'src\config\db_config.json','r+') as json_file:
        db_info = json.load(json_file)
    
    link = f"mysql+pymysql://{db_info['user']}:{db_info['sql_server_passcode']}@{db_info['host']}:{db_info['port']}/{db_info['db_name']}"
    engine = create_engine(link)
    amount=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    # Menu
    df_pd=look("items")
    # Stock
    df_st=look("stock")



# Created By Mohamed Galal Elgemeie
# all rights reserved