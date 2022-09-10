# Created By Mohamed Galal Elgemeie
# all rights reserved
import pandas as pd
import os
from sqlalchemy import create_engine
import mysql.connector as mc
def truncate(table):
    """
    Used to truncate the specified table contents from the
    database.
    parameters:
        table: database's table name to be selected 
    """
    with  mc.connect(host="localhost",user='root',passwd="KOKOWaWa1Ak9mysql",database='db_bookstore') as db:
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
    print("-\n"*6,df.info(),"-\n"*5)
    # start connection to database
    with engine.begin() as connection:
        df.to_sql(table,con=connection,if_exists=exist,index=False)
if __name__ != "__main__":
    cur_dir=os.path.dirname(os.path.abspath(__file__))
    engine = create_engine("mysql+pymysql://root:KOKOWaWa1Ak9mysql@localhost:3306/db_bookstore")
    amount=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    # Menu
    df_pd=look("items")
    # Stock
    df_st=look("stock")
    # books
    df_se=look("books")
# Created By Mohamed Galal Elgemeie
# all rights reserved
