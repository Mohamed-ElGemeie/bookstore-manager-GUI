# Created By Mohamed Galal Elgemeie
# all rights reserved

import pandas as pd
from sqlalchemy import create_engine
import mysql.connector as mc
import json
from .settings import load_json
from pandas import DataFrame
from datetime import datetime as dt


def truncate(table):
    """
    Used to truncate the specified table contents from the
    database.
    parameters:
        table: database's table name to be selected 
    """

    config_data = load_json('config')

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

def create_transaction_id(type):

    start_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    temp_df= DataFrame({'start_time': [start_time], 'type': [type]})
    print(temp_df)
    to_db("transactions",temp_df,exist="append")

    response = run(f"SELECT * FROM transactions WHERE start_time = '{start_time}'")

    return int(response["id"])


if __name__ != "__main__":

    db_info = load_json('database_config')
    
    link = f"mysql+pymysql://{db_info['user']}:{db_info['sql_server_passcode']}@{db_info['host']}:{db_info['port']}/{db_info['db_name']}"
    engine = create_engine(link)
    # Menu
    df_menu=look("item")



# Created By Mohamed Galal Elgemeie
# all rights reserved
