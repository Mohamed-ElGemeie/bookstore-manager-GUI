# Created By Mohamed Galal Elgemeie
# all rights reserved
import tkinter as tk
import pandas as pd
from datetime import datetime as dt, timedelta
from time import sleep
from csv import writer,reader 
import json
from db_open import *
from dateutil import parser
import numpy as np
def open_sessions():
  """
  Function called on start and exit of every session that saves the session's
  name,start time, and cart in case the program closes unexpectedly

   * open 'sessions' table from the DB
   * tranfrom all the records into session class objects
   * insert session objects into session_dict library
   * insert the saved session names into the session box list in the session_orders_page class
   """
  global session_dict
  global app
  #open the session table from the DB
  df=look("sessions")
  # list that holds diffrent cart item strings 
  cart_str=[]
  # loops over all the session table columns
  for n,i,st in zip(df['name'].values,df['cart'].values,df['start_time'].values):
    try:
      # this check wether we saved one or two or more item in the cart
      cart_str=i.split(',')
      # if more than one then it could be easily casted a list
      if len(cart_str)>1:
        session_dict[n]=sessions(session_name=n,cart=list(cart_str),start_time=st)
      # if one item and non-empty, then we append the current item which is a string 
      # we don't cast the string into a list as it will convert it into a char array
      elif len(cart_str)==1 and cart_str[0]!='':
        # clear the list
        cart_str.clear()
        # append only that string
        cart_str.append(i)
        session_dict[n]=sessions(session_name=n,cart=list(cart_str),start_time=st)
      else:
        # if both cases above don't apply then the list is empty and we assign an empty list
        session_dict[n]=sessions(session_name=n,cart=[],start_time=st)
    except:
      # in case we can't split the cart_str indicates that the sessions never had 
      # an item in its cart before, in that case we don't asssign a cart, as 
      # sometimes it inserts an undesired empty row in the session's cart.
      session_dict[n]=sessions(session_name=n,start_time=st)
    # empty the cart_str for the next loop
    cart_str=''
    # insert the session name into the session_order_page box list.
    app.frames['session_order_page'].session_boxlist.insert('end',n)
    print("\nOpened sessions\n")
def session_update():
  """
  This function converts the session_dict library that holds all the sessions into a dataframe that 
  contains every sessions': name, cart, start_time.
  Then saves it into the sessions table from DB
  * create variables to hold every record's data
  * iterate and store every sessions' data in the variables
  * convert the variables into a dataframe
  * overwrite the session table with the dataframe 
  """
  # carts: list that holds all the cart items of each session
  # cart_str: list the convert to string that holds every item in the cart as a temporary string
  # start_time: list to hold all the start times of each session
  carts=[]
  cart_str=[]
  start_times=[]
  # loops over the session_dict that hold all the sessions
  for i in session_dict.values():
    # if the cart isn't empty, iterate over all the items
    if len(i.cart)!=0:
      for g in i.cart:
        cart_str.append(g)
    # convert the cart_str list into string, then clean to remove and unwanted space or commas
    # then append to the carts list.
    carts.append(str(cart_str)[1:-1].replace("'",'').strip())
    # empty for next loop
    cart_str=[]
    start_times.append(i.start_time) 
  # delete the session table's content  
  truncate("sessions")
  # convert the three lists into a dataframe
  temp_df=pd.DataFrame({'name':[*session_dict.keys()],'cart':carts,'start_time':start_times})
  # overwrite with the dataframe into the sessions table
  to_db("sessions",temp_df,exist="append")
  print("\nSaved all current open sessions\n")
def json_update():
  """
  Function that update the config.json file with the config_data dictionary
  * if any changes were made to config_data, they will be saved externally to config.json
  """
  with open(f"{cur_dir}\config.json", "w") as outfile:
    json.dump(config_data,outfile,indent=4)
def carto_dict(payload):
  """
  This function takes an item row and finds whether that item row is a take-away item or 
  an instore item.
  parameters: 
    payload: 1 row of item in the item cart
  returns:
    0: if that item row is a take-away item
    1: if that item row is an instore item
  * finds the store/take-away flag
  * returns the value.
  """
  # if find() returns -1 that mean that the instore flag wasn't found
  # so we assign table with zero in that case and 1 otherwise
  if payload.find('1 In Store')!=-1:
    table=1
  else:
    table=0
  return(table)
def Confirm(self,tk_or_sess,stay_name,func):
  """
  global function assigned to the confirm button on the summary_page and orders_page that checks out
  the order in the cart and converts it into a dataframe, while updating the stock table and handleing
  certain errors, also used for both quick takeaway orders and session orders
  parameters:
    self: The tkinter frame page object which could be (orders_page, session_orders_page)
    tk_or_sess: holds true if the order is a session order, and false if its a quick-takeaway
    stay_name: holds the session's or take-away name
    func: function that is called on exit that completes the rest of the check out, as 
          the take-away and session orders have diffrent procedures
  * check if the cart is empty, and create table_instance dictionary
  * convert the table_instance into a pandas dataframe and convert the columns into their sutible types
  * check if the ordered items excist in the stock, and remove the required amount from the stock table on db
  * call the passed function (func).  
  """
  # trial1 used to force the user to press the confirm button twice for execution
  global trial1
  # app dictionary that holds all the tkinter frame pages
  global app
  # first press on confirm assigns trail1 with 1 for execution on next press
  if not trial1:
    # prompt the user to press again
    self.error_visor.config(text='Sure? Press confirm again')
    trial1=1
  else:
    # raises error if cart is empty and the order is a take-away(Not Session)
    if self.cart_boxlist.size()==0 and not tk_or_sess:
      self.error_visor.config(text='Cart is empty!')
      return()
    # true if the cart is empty and the order is a session
    # and so you can have sessions with empty carts
    if self.cart_boxlist.size()==0 and tk_or_sess:
      self.error_visor.config(text='')
      # assigns default values for an empty order
      # table_instance converts into a dataframe that is written in the 
      # transactions table from db.
      # -2 in the item_id column indicates that the session had no items
      table_instance={'item_id':[-2],'item_name': [''],'item_price': [0],
            'item_count': [0],'item_total': [0],'order_total': [0],
            'table': [True],
            'stay': [stay_name]} 
    else:
      #empty the warning box
      self.error_visor.config(text='')
      #iterate all values in cart + empty the cart
      table_instance={'item_id':[],'item_name':[],'item_price':[],
                      'item_count':[],'item_total':[],
                      'order_total':[],'table':[],'stay':stay_name}
      # loop on the page's cart
      for i in range(self.cart_boxlist.size()):                              
        # get the first item row
        payload=self.cart_boxlist.get(0)
        # delete the first item row
        self.cart_boxlist.delete(0)
        # use find and certain flags used to extract the order's records from the string row
        # append the extracted records to the table_instance dictionary
        table_instance['item_name'].append(str(payload[0:payload.find('-')]))
        temp_id=df_pd[df_pd['item_name']==str(payload[0:payload.find('-')])].reset_index(drop = True)
        table_instance['item_id'].append(temp_id['item_id']) 
        table_instance['item_price'].append(str(payload[payload.find(":(")+2:payload.find(")")]))
        table_instance['item_count'].append(str(payload[payload.find("nt:(")+4:payload.find(")-")]))
        table_instance['item_total'].append(int(payload[payload.find('=')+2:]))   
        # check if the items orderd exist in the stock table
        try:
          # check if the item_name matches
          df_st.loc[df_st['item_name']==str(payload[0:payload.find('-')]),['item_stock']]-=int(payload[payload.find("nt:(")+4:payload.find(")-")])    
          # overwrites the stock table with the new dataframe that contains the updated stock counts (df_st)
          truncate('stock')
          to_db('stock',df_st,'append')  
        except:
          pass
        # diffrentiate between takeways and instore orders made from the orders_page
        # this handels when a session orders both instore and take away orders
        if tk_or_sess == True:         
          tk_or_sess=bool(carto_dict(payload))
        table_instance['table'].append(tk_or_sess)
    # updates user warnings on low stock
    stock_page.warn(app.frames['stock_page'])
    # updates the stock page listbox
    stock_page.listbox_update(app.frames['stock_page'])
    table_instance['order_total']=sum(table_instance['item_total'])
    #create dataframe to hold the transactions
    tb_pd=pd.DataFrame(table_instance)
    #cleanning the dateframe
    tb_pd['item_price'] = pd.to_numeric(tb_pd['item_price'])
    tb_pd['item_count']=pd.to_numeric(tb_pd['item_count'])  
    tb_pd['item_id']=tb_pd['item_id'].astype(int)  
    # resets the trial1 variable and calls the function
    trial1=0
    func(tb_pd)
#confirm button rewinder 
trial1=0   
#session holder
session_dict={}
class main_app(tk.Tk):
  """
  Main Gui app
  Class that inheritances the Tkinter window class. this is used to run all the tkinter frames/pages
  and specifies the background color, resolution of the program"""
  # inherate everything from tkinter
  def __init__(self,*args,**kwargs):
    # create tkinter window
    tk.Tk.__init__(self,*args,**kwargs)
    # resolution of the window
    self.geometry('1280x700+20+20')
    # stacker of pages
    stacker=tk.Frame(self)
    stacker.pack(side="top",fill='both',expand=True)
    #change stacker row and column sizes
    stacker.grid_rowconfigure(0,weight=1)
    stacker.grid_columnconfigure(0,weight=1)
    # self.frames: holds all the tkinter frames
    # {tkinter page-name string : tkinter page object}
    self.frames={}
    # holds all the classes the inherante the tkiner frame
    pages = (startpage,stock_page,analysis_page,orders_page,summary_page,session_order_page,book_page)
    for i in pages:
      #put all the pages in the same location      
      page_name=i.__name__
      # assign background color, and other parameters if prefered
      frame= i(stacker,self,bg='#48788a')
      self.frames[page_name]= frame
      frame.grid(row=0,column=0,sticky='nsew')
    # opens the startpage on start up
    self.show_frame("startpage")
  def show_frame(self,page_name):
    """
    Takes a tkinter frame object (page) and displays it on top, front to the user
    parameters:
      page_name: name of the page's tkinter frame class
    """
    frame=self.frames[page_name]
    frame.tkraise()
class startpage(tk.Frame):
  """
  Start Page that displays the buttons to all the other pages
  inheritance tkinter frame
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    # assigns background,foreground color if passed
    # other tkinter frame arrtibutes could be defined here
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker 
    label = tk.Label(self, text="Titi Book Store",
                             font=('Helvetica',18,'bold'),bg='#bfbfbf')   
    label.pack(side="top", fill="x", pady=10)
    # orders button
    go_orders=tk.Button(self,height = 1, width = 10 ,text=('Orders/طلبات'),font=('Helvetica',25),command=lambda: stacker.show_frame('session_order_page'),bg='#bfbfbf')
    go_orders.place(x=100,y=100)
    # stock button
    go_stock=tk.Button(self,height = 1, width = 13 ,text=('Stock/مخزن'),font=('Impact',25),command=lambda: stacker.show_frame('stock_page'),bg='#bfbfbf')
    go_stock.place(x=500,y=100)    
    # analysis button
    go_analysis=tk.Button(self,height = 1, width = 16 ,text=('Analytics-Profit/تقرير'),font=('Helvetica',25),command=lambda: stacker.show_frame('analysis_page'),bg='#bfbfbf')
    go_analysis.place(x=500,y=200) 
    # books button
    go_book=tk.Button(self,height = 1, width = 13 ,text=('Books/كتب'),font=('Helvetica',25),command=lambda: stacker.show_frame('book_page'),bg='#bfbfbf')
    go_book.place(x=100,y=300) 
class analysis_page(tk.Frame):
  """
  This page displays a quick summation of the user's inputed date profit and revenue.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    # go back button
    go_back=tk.Button(self,font=45,text=('Go Back <(----'),command=lambda: stacker.show_frame('startpage'))
    def reporter(df,df_library):
      """
      Function that fills a report of the profit from each source with the user's specified date
      parameters:
        df: holds a dataframe query with the certain date of the transactions on that date
        df_library: holds a dataframe query with the certain date of the books/print sold on that date
      * assign summation of certain column to each variable.
      * config the labels to hold those summation values.
      """
      # filter to only paper transactions
      df_print=df_library[df_library['stay']=='paper']
      # convert the column to type int
      df_print['name'] = pd.to_numeric(df_print['name'])
      # filter to only session, and take-away transactions
      df_orders=df[df['stay'].str.contains('Session|Take-')]
      # filter to only books sold
      df_book=df_library[df_library['stay']!='paper']
      # filter to only stock transactions, get sum of stock transactions
      temp_stock=df[df['stay'].str.contains("stock")]['paid_total'].sum()
      # create string that holds wifi charges, order totals, and sum of both.
      temp_cafe=f"Wifi ({df_orders['wifi'].sum()}) + Orders ({df_orders['order_total'].sum()}) = {df_orders['paid_total'].sum()}"
      # create string that holds sum of books sold and for how much, and same for the printed papaer
      temp_library=f"{df_book[df_book.columns[0]].count()} book = {df_book['price'].sum()}  -  {df_print['name'].sum()} print = {df_print['price'].sum()}"
      # assign all the varibales to their respected labels
      self.info_stock.config(text=temp_stock)
      self.info_cafe.config(text=temp_cafe)
      self.info_library.config(text=temp_library)
      self.info_profit.config(text=df_orders['paid_total'].sum()+temp_stock+df_library['price'].sum())
    def select_range():
      """
      Function that take from the user a date or a range between two dates.
      checks for any user errors, and calls an SQL  query with the user date, to 
      call the reporter fucntion passing the queries.
      """
      # get all the entry boxes content
      year=year_e.get()
      month=month_e.get()
      day=day_e.get()
      # get the entery boxes content seprated with '-' if the user specifies a range
      sp_year=year.split('-')
      sp_month=month.split('-')
      sp_day=day.split('-')
      # true if the user only inputed one date (year-month-day) 
      if(len(sp_year)==1 and len(sp_month)==1 and len(sp_day)==1):
        # checks if the input is an int
        try:
          year=int(year)
          month=int(month)
          day=int(day)
        except:
          # raises error otherwise
          self.error_visor.config(text='Only enter Number/ادخل اركام فقط')
          return 
        # runs a query with the user dates
        # once with the transactions table, and once with the books table
        query=run(f"SELECT * FROM db_bookstore.transactions t WHERE day(t.start_time) = {day} and month(t.start_time) ={month} and year(t.start_time) ={year} GROUP BY t.stay;")   
        query_book=run(f"SELECT * FROM db_bookstore.books t WHERE day(t.start_time) = {day} and month(t.start_time) ={month} and year(t.start_time) ={year};")   
        # call the reporter function
        reporter(query,query_book)
      # true if the user passes two dates
      #(yaer-year)(month-month)(day=day)
      elif(len(sp_year)==2 and len(sp_month)==2 and len(sp_day)==2):
        # check if int
        try:
          for i in sp_year+sp_day+sp_month:
            int(i)
        # error otherwise
        except:
          self.error_visor.config(text='Only enter Number/ادخل اركام فقط')
          return 
        query=run(f"SELECT * FROM db_bookstore.transactions t WHERE t.start_time between '{sp_year[0]}-{sp_month[0]}-{sp_day[0]}' and '{sp_year[1]}-{sp_month[1]}-{sp_day[1]}' GROUP BY t.stay;")
        query_book=run(f"SELECT * FROM db_bookstore.books t WHERE day(t.start_time) = {day} and month(t.start_time) ={month} and year(t.start_time) ={year};")   
        reporter(query,query_book)
      # true if above cases weren't satisfied
      else:
        self.error_visor.config(text='-أدخل فقط سنة - شهر - يوم في كلا المدخلين أو أحدهما')
        return 
    # frame that holds the reports content
    bg_grey=tk.Frame(self,height=550,width=900,bg='light grey')
    #labels
    range_label=tk.Button(self,text='Select Range/اختيار النتاق',height = 1, width = 20 ,font=('Helvetica',15,'bold'),bg='light grey',
                                                                                                         command=lambda: select_range())
    year_label=tk.Label(self,text='Year-Year/سنة',height = 1 ,font=('Helvetica',12,'bold'),bg='light grey')
    month_label=tk.Label(self,text='Month-Month/شهر',height = 1 ,font=('Helvetica',12,'bold'),bg='light grey')
    day_label=tk.Label(self,text='Day-Day/يوم',height = 1 ,font=('Helvetica',12,'bold'),bg='light grey')
    report_label=tk.Label(self,text='Report/جرد',height = 1 ,font=('Helvetica',20,'bold'),bg='light grey')
    self.error_visor=tk.Label(self,text='Errors are showen here/أخطاء المستخدم',width= 40 ,font=('Helvetica',15,'bold'),bg='light grey')
    #buttons
    library=tk.Label(bg_grey,text='Library/المكتبة:',height=1,width= 12,justify='left',relief='flat' ,font=('Helvetica',18,'bold'),bg='white')
    cafe=tk.Label(bg_grey,text='Cafe/كافيه:',height=1,width= 12,justify='left',relief='flat' ,font=('Helvetica',18,'bold'),bg='white')
    stock=tk.Label(bg_grey,text='Stock/المخزن:',height=1,width= 12,justify='left',relief='flat' ,font=('Helvetica',18,'bold'),bg='white')
    profit=tk.Label(bg_grey,text='Profit/المكسب:',height=1,width= 12,justify='left',relief='flat' ,font=('Helvetica',18,'bold'),bg='white')
    # info labels
    self.info_library=tk.Label(bg_grey,text='',height=1,width= 30,justify='center',relief='flat' ,font=('Helvetica',24),bg='white')
    self.info_cafe=tk.Label(bg_grey,text='',height=1,width= 30,justify='center',relief='flat' ,font=('Helvetica',24),bg='white')
    self.info_stock=tk.Label(bg_grey,text='',height=1,width= 30,justify='center',relief='flat' ,font=('Helvetica',24),bg='white')
    self.info_profit=tk.Label(bg_grey,text='',height=1,width= 30,justify='center',relief='flat' ,font=('Helvetica',24),bg='white') 
    #entry
    in_year=tk.StringVar()
    in_month=tk.StringVar()
    in_day=tk.StringVar()
    year_e=tk.Entry(self,textvariable=in_year,font=("Helvetica",20),width=10)
    month_e=tk.Entry(self,textvariable=in_month,font=("Helvetica",20),width=10)
    day_e=tk.Entry(self,textvariable=in_day,font=("Helvetica",20),width=10)
    # placement
    range_label.place(x=25,y=115) 
    year_label.place(x=25,y=160)  
    year_e.place(x=25,y=190)
    month_label.place(x=25,y=230)  
    month_e.place(x=25,y=260)
    day_label.place(x=25,y=300)  
    day_e.place(x=25,y=330)
    self.error_visor.place(x=500,y=30)
    report_label.place(x=45,y=40)
    # info section
    bg_grey.place(x=300,y=100)
    library.place(x=10,y=10)
    cafe.place(x=10,y=120)
    stock.place(x=10,y=230)
    profit.place(x=10,y=350)
    # info labels
    self.info_library.place(x=220,y=15)
    self.info_cafe.place(x=220,y=125)
    self.info_stock.place(x=220,y=235)
    self.info_profit.place(x=220,y=355)
    go_back.pack(side='bottom')  
class book_page(tk.Frame):
  """
  This class writes transactions of the books and printed paper into
  the books table from db.
  * recive user input of book name, book price, printed paper amount
  * write the transaction details into the books table from db
  """
  def __init__(self,parent,stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    def printed():
      """
      Function that handels the printed paper amount transaction.
      * checks for any user errors
      * calculates the price of the amount 
      * stores the transaction into the books table
      """
      # retrive paper amount from entry box
      paper=paper_amount_e.get()
      # true if the entry box isn't empty
      # false if the user didn't input anything
      if paper_amount_e:
        try:
          paper=int(paper)
        # raises error if the user inputs anything else other than int
        except:
          self.error_visor.config(text="The paper amount has to be a number/عدد الورق يجب ان يكن رقم")
          return
        # create paper transaction row
        temp_df=pd.DataFrame({'name': [paper],'price': [paper*0.75],
            'stay': ["paper"],
            'start_time': dt.now()})
        # append row to books table
        to_db("books",temp_df,exist="append")
        # empty the user entry box
        paper_amount_e.delete(0,tk.END)
        self.error_visor.config(text='تم التسجبل')
      else:
        self.error_visor.config(text="one of the fields is empty/احد  الإدخالات فارغ")
    def buy():
      """
       Function that handels the sold book transactions.
      * checks for any user errors 
      * stores the transaction into the books table
      """
      # global variable counter to make each transaction have a unique name
      global book_counter
      # retrive user input
      name=book_name_e.get()
      price=book_price_e.get()
      # true if the user inputs in both boxes and false otherwise
      if name and price:
        try:
          # check if the price is int, and the name is string
          int(price)
          if(name.isdigit()):
            self.error_visor.config(text="The name has to have letter/الاسم يجب ان يكن متكون من حروف")
            return
        except:
          self.error_visor.config(text="The price has to be a number/السعر يجب ان يكن رقم")
          return
        # creats the transaction row
        temp_df=pd.DataFrame({'name': [name],'price': [price],
                  'stay': [f"book {book_counter}"],
                  'start_time': dt.now()})
        # enumerate by one
        book_counter+=1
        # store the new counter
        config_data['book_num']=book_counter
        # save the new counter to config.json
        json_update()
        # append the transaction to the book table
        to_db("books",temp_df,exist="append")
        # empty user entry boxes
        book_name_e.delete(0,tk.END)
        book_price_e.delete(0,tk.END)
        self.error_visor.config(text='تم التسجبل')
      else:
        self.error_visor.config(text="one of the fields is empty/احد  الإدخالات فارغ")
    #vars
    self.book_name=tk.StringVar()
    self.book_price=tk.StringVar()
    self.paper_amount=tk.StringVar()
    #entry
    book_name_e=tk.Entry(self,textvariable=self.book_name,font=("Helvetica",20),width=30)
    book_price_e=tk.Entry(self,textvariable=self.book_price,font=("Helvetica",20),width=30)
    paper_amount_e=tk.Entry(self,textvariable=self.paper_amount,font=("Helvetica",20),width=30)
    #buttons
    buy_b=tk.Button(self,font=('Helvetica',20,'bold'),text=('Confirm'),command=lambda:buy())
    print_b=tk.Button(self,font=('Helvetica',20,'bold'),text=('Confirm'),command=lambda:printed())
    go_back=tk.Button(self,font=45,text=('Go Back <(----'),command=lambda: stacker.show_frame('startpage'))
    #labels 
    book_name_l=tk.Label(self,text='Book Name/اسم الكتاب',height=1,justify='center',relief='flat' ,font=('Helvetica',22,'bold'),fg='black',bg='light grey')
    book_price_l=tk.Label(self,text='Book Price/سعر الكتاب',height=1,justify='center',relief='flat' ,font=('Helvetica',22,'bold'),fg='black',bg='light grey')
    self.error_visor=tk.Label(self,text='Errors are showen here/أخطاء المستخدم',width= 60 ,font=('Helvetica',18,'bold'),bg='light grey')
    paper_amount_l=tk.Label(self,text='Printed paper/عدد الورق للطباعة',height=1,justify='center',relief='flat' ,font=('Helvetica',22,'bold'),fg='black',bg='light grey')
    #placments
    go_back.pack(side='bottom')
    buy_b.place(x=150,y=320)
    book_name_e.place(x=50,y=120)
    book_name_l.place(x=50,y=70)
    book_price_e.place(x=50,y=270)
    book_price_l.place(x=50,y=220)
    paper_amount_l.place(x=800,y=70)
    paper_amount_e.place(x=800,y=120)
    print_b.place(x=900,y=170)
    self.error_visor.place(x=200,y=30)
class stock_page(tk.Frame):
  """
  This page handels the stock transactions and manages the stock,
  some stock also exists in the menu and so this class handels 
  automatic decrease of stock on purchase.
  *
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    # labels and vars
    # placed here to avoid refrence before assignment errors
    self.stock_amount=tk.IntVar()
    self.stock_amount.set(1)
    self.stock_entry=tk.Entry(self,font=("Helvetica",28),width=30)
    self.error_visor=tk.Label(self,height = 2, width = 40 ,text="Errors are shown here",font=('Helvetica',15,'bold'),bg='light grey')
    def exit_seq():
      """
      Function run on exit of the page.
      * updates the stock dataframe from the stock table
      * write the stock items and thier counts
      * upadte the warning box of missing or low amount stock
      """
      global df_st
      df_st=look("stock")
      stock_page.listbox_update(self)
      stock_page.warn(self)
      # go back to startpage
      stacker.show_frame('startpage')
    def add_price():
      """
      Function that handels the user input and changes the stock dataframe 
      with the new stock amount specified by the user and writes that to the 
      stock table from db
      """
      # stock dataframe
      global df_st
      # stock counter for unique transactions
      global stock_counter
      # true the user doesn't input anything
      if(self.stock_entry.get()==''):
        self.error_visor.config(text='Enter the stock price/أدخل سعر السلعة')
        return
      try:
        # check if int
        price=int(self.stock_entry.get())
      except:
        self.error_visor.config(text='Only enter the stock price Number/ادخل اركام فقط')
        return
      # true if the user didn't change the stock
      # return as the stock needs to be changed in order for a transaction to be done
      if df_st.equals(look("stock")):
        self.error_visor.config(text="You didn't change the Stock/أنت لم تغير المخزون")
        return
      # you can't buy stock with a negative number and so this returns if true
      if price<0:
        self.error_visor.config(text="Price can't be less than zero!/لا يمكن أن يكون السعر أقل من صفر!")
        return      
      # create stock transaction row
      temp_df=pd.DataFrame({'item_id':[-1],'item_count': [0],'item_total': [0],
                'order_total': [0],'table': [False],'stay': [f"stock {stock_counter}"],
                'start_time': dt.now(),'end_time':dt.now(),'time':dt.now()-dt.now(),
                'wifi':[0],'paid_total':[-price]})
      stock_counter+=1
      # save the new stock counter to config.json
      config_data['stock_num']=stock_counter
      json_update()
      # append the new transaction row
      to_db("transactions",temp_df,exist="append")
      truncate('stock')
      # overwrite the stock table
      to_db('stock',df_st,'append')
      # empty and default all entries
      self.error_visor.config(text='')
      self.stock_entry.delete(0,"end")
      self.stock_entry.focus()
      self.stock_amount.set(1)
    def change(add):
      """
      This function handels all the change the user makes on the stock amounts
      in real time.
      parameters:
        add: if true, the stock is increased with the count the user specifies
             if false, the stock is decreased with the count the user specifies
      * get the stock item, and the number to change its count by.
      * check for user input
      * update stock dataframe without changing the stock table from db.
      """
      # get user input
      y=int(self.stock_amount.get())
      z=self.stock_entry.get().strip()
      # handlling of empty input + input not existing in the stock dataframe
      # zlen: the amount of items that are equal to the user input
      # zlen will always equal 1 or zero
      zlen=(df_st['item_name']==z).sum()
      if not z:
        self.error_visor.config(text='Please Select an Item!')
      elif not zlen:      
        self.error_visor.config(text='Incorrect Item, Please Select from the List') 
      else:
        # true if the user wants to increase the count
        if add:
          # increase the dataframe's stock item count with the user specified count 
          df_st.loc[df_st['item_name']==z,['item_stock']]+=y
        # true if the user wants to decrease the count
        else:
          # handels the decrease on a zero amount item
          if df_st.loc[df_st['item_name']==z,['item_stock']].values==0:
            self.error_visor.config(text="You don't have that Item! Please buy some")
            self.stock_entry.focus()
            return()
          # handels if the user wants to decrease a larger number
          # resulting in a negative stock
          elif (df_st.loc[df_st['item_name']==z,['item_stock']].values-y)<0:
            self.error_visor.config(text=f"You can't delete {y} if you only have {df_st.loc[df_st['item_name']==z,['item_stock']].values}")
            self.stock_entry.focus()
            return()
          # decrease the dataframe's stock item count
          else:
            df_st.loc[df_st['item_name']==z,['item_stock']]-=y
        # update all fields
        stock_page.listbox_update(self)
        stock_page.warn(self)
        self.error_visor.config(text='')
      self.stock_entry.focus()
    def fillout(e):
      """
      Event function that is run when the user selects an item from the list box,
      this function auto completes the user input.
      * user clicks an item from the list box , which runs this function.
      * the selected item then is auto filled into the user entry box.
      """
      # delete the user input
      self.stock_entry.delete(0,tk.END)
      # true if the user selected anything on the list box
      if self.stock_menu.get(self.stock_menu.curselection()):
        x=self.stock_menu.get(self.stock_menu.curselection())
        # assign the entry box with the selected item
        self.stock_entry.insert(0,x[:x.find('-')])   
    def tab_handler(e):
      """
      Event function run on pressing tab while selecting the entry box,
      this function selects the first item that appears on the list box
      and assign that to the user's entry box
      """
      # get the list box's size
      box_size=self.stock_menu.size()
      # true if the box size isn't zero, and an input exists
      if self.stock_entry.get() and box_size:
        # clear the user's selection on the list box
        self.stock_menu.selection_clear(0, 'end')
        # delete the user's entry box
        self.stock_entry.delete(0,tk.END)        
        # select the first item form the listbox
        self.stock_menu.select_set(0) 
        # assign that item to the user's entry box
        x=self.stock_menu.get(self.stock_menu.curselection())
        self.stock_entry.insert(0,x[:x.find('-')])
      self.stock_entry.focus()  
    def check(e):
      """
      Event function that takes all the item in the dataframe
      that contain a substring of the user's input, then it auto fills
      those item only to the list box.
      * makes it easier for the user to find thier item easily
      * uses python's 'in' operator
      """
      # get user input
      inthere=self.stock_entry.get().lower().strip()
      # writes the whole stock dataframe to the list box
      # incase the user didn't have any input
      if inthere== '':
        stock_page.listbox_update(self)  
      else:
        self.stock_menu.delete(0,tk.END)
        # check for each item and appends it if it contains a substring of the 
        # user's input 
        for i,g in zip(df_st['item_name'].values,df_st['item_stock'].values):
          if inthere in i.lower():
            self.stock_menu.insert(tk.END,f'{i}-  {g}')
      # select the first item in the list box
      self.stock_menu.select_set(0)    
    # listboxes
    self.stock_menu=tk.Listbox(self,font=("Helvetica",16),justify='right',relief='solid',height=26,width=30,exportselection=False,selectmode='SINGLE')
    # buttons
    go_back=tk.Button(self,font=20,text=('Go Back <(----'),command=lambda: exit_seq())
    add_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#07D712',bg='#f5f5f5',height=1,text="Add Stock",command=lambda: change(True))
    remove_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#D72C2C',bg='#f5f5f5',height=1,text="Del Stock ",command=lambda: change(False))
    change_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#E68C00',bg='#f5f5f5',width=12,height=1,text="Confirm",command=lambda: add_price())
    # labels
    self.warning=tk.Label(self,height=19,justify='left', width = 50 ,text="Warnings are shown here",font=('Helvetica',15),bg='light grey')
    # option menus
    self.stock_amount_option = tk.OptionMenu(self, self.stock_amount, *amount)
    # function run on start up to fill the fields
    stock_page.listbox_update(self)     
    stock_page.warn(self)
    # bindings
    self.stock_menu.bind('<<ListboxSelect>>',fillout)
    self.stock_entry.bind("<KeyRelease>",check)
    self.stock_entry.bind('<Tab>', tab_handler)
    # placments
    self.error_visor.place(x=130,y=10)
    self.warning.place(x=60,y=190)
    add_btn.place(x=700,y=130)
    remove_btn.place(x=700,y=83)
    change_btn.place(x=680,y=220)
    self.stock_menu.place(x=900,y=25)
    self.stock_entry.place(x=60,y=80)
    self.stock_amount_option.place(x=830,y=105)
    go_back.pack(side='bottom')    
  def warn(self):
    """
    Function that updates the warning box, this functions
    is used to warn the user of any low count stock that 
    should be refilled after a certain number
    """
    warning=''
    # loop over the stock dataframe and check if any items have low counts
    for i,g in zip(df_st['item_stock'].values,df_st['item_name'].values):
      # counts less that 8
      if(i<8):
        warning+=f"Now! {g} - You have {i}\n"    
      # counts less than 15
      elif(i<15):
        warning+=f"Tomorrow! {g} - You have {i}\n"
    # write that warining string to the warning label
    self.warning.config(text=warning[:-1])
  def listbox_update(self):
    """
    Fucntion that updates the listbox with the stock dataframe items
    with out any manipulation
    """
    # delete the list box contents
    self.stock_menu.delete(0,tk.END)
    # loop and append
    for i,g  in zip(df_st['item_name'].values,df_st['item_stock'].values):
        self.stock_menu.insert(tk.END,f'{i}-  {g}')
class session_order_page(tk.Frame):
  """
  This page handels the quick take-away order, and the creation of sessions
  from the session class.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    # global variable counters that ensure unique id for each session and takeaway transaction
    self.table_count=table_counter
    self.take_count=take_away_counter 
    # varible that holds wether the order is take-away or not
    self.table=tk.IntVar()
    # set to zero as any orders on this page are take-away orders
    self.table.set(0)
    def listbox_update(item):
      """
      Function that updates the listbox with the passed argument items
      without any manipulation.
      parameters
        item: list object that contains the items to be filled
      """
      # clear the list box
      entries_boxllist.delete(0,tk.END)
      # append the items to the list box
      for i in item:
        entries_boxllist.insert(tk.END,i)
    def dble_clk_del(e):
      """
      Event function that delets an item row from the list box cart when double clicked on
      by the user.
      """
      # true if a selection exists 
      if self.cart_boxlist.curselection():
        # remove the selection
        self.cart_boxlist.delete(self.cart_boxlist.curselection())
      else:
        sleep(0.3)
    def tab_handler(e):
      """
      Event function run on pressing tab while selecting the entry box,
      this function selects the first item that appears on the list box
      and assign that to the user's entry box
      """
      # get the list box's size
      box_size=entries_boxllist.size()
      # true if the box size isn't zero, and an input exists
      if order_items.get() and box_size:
        # clear the user's selection on the list box
        entries_boxllist.selection_clear(0, 'end')
        # delete the user's entry box
        order_items.delete(0,tk.END)  
        # select the first item form the listbox      
        entries_boxllist.select_set(0)    
        # assign that item to the user's entry box          
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))
      order_items.focus()        
    def empty_cart(*args):
      """
      Event function and button function that removes all the items from the cart list box
      """
      self.cart_boxlist.delete(0,'end')
    def add_item(*args):
      """
      This function adds items to the cart listbox specified by the user,
      and handels any changes in stock if that item were to exist in both
      the menu and the stock dataframes. Also handels repeated item entries
      and incorrect user inputs
      """
      # get user input, amount, item
      y=int(order_amount_var.get())
      z=order_items.get()
      # amount of menu items that are equal to the user input
      # can only be one or 0
      zlen=(df_pd['item_name']==z).sum()
      # handle items existing in both the menu and the stock dataframe
      try:
        # will not cause errors
        # if there exists and item with the same name in the stock dataframe
        # as the item selected by the user
        stock=int(df_st.loc[df_st['item_name']==z,['item_stock']].values)
        # true if the user tries to buy a non existing item
        if stock<1:
          self.error_visor.config(text='That item is out of stock!')
          return()
        # true if the user tries to buy more items that he currently has
        if stock-y<0:
          self.error_visor.config(text='You need more of that item!')
          return()
        # if all above is false, this variable later declares that this item's stock amount in 
        # the stock table will be changed if assinged to true
        stocked=True
      except:
        stocked=False       
      # true if the user doesn't have any input
      if not z:
        self.error_visor.config(text='Please Select an Item!')
      # true if the input isn't any items from the menu
      elif not zlen:      
        self.error_visor.config(text='Incorrect Item, Please Select from the List') 
      else:
        x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
        # price_ta is the take-away price of that item
        x=x.price_ta
        table='0 Take Away'
      # add_var: is used to decide if the item already exists in the list box 
      # or not, this ensures that repeated items share the same row
      add_var=False
      # in_stock: this is used to take into account the amount of the item's count
      # in the cart list box, to avoid having negative stock
      in_stock=True
      # loop over the cart boxlist
      for i in range(self.cart_boxlist.size()):
        g=self.cart_boxlist.get(i)
        # true if the user's inputted item is in the selected row from the list box
        if z in g:
          # true if the item's table type (no table-0, yes table-1) is the same as
          # the selected item
          if int(g[g.find('-')+1]) == self.table.get():
            if stocked:
              # true if the item's amount in stock -- minus -- the
              # additional amonut + the amount already existing in the cart
              # is more than or equal to zero. To avoid negative stock errors 
              if stock-(y+int(g[g.find("nt:(")+4:g.find(")-")]))>=0:
                print('already here, adding counts..')
                # set true to add the user's specified amount to the already existing row
                add_var=True
                break
              else:
                in_stock=False
                break
            else:
              add_var=True
      # true if item exists in stock, and could be increased
      if add_var and in_stock:
        y+=int(g[g.find("nt:(")+4:g.find(")-")])
        self.cart_boxlist.delete(i)
        # change the row
        self.cart_boxlist.insert(i,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')
        self.error_visor.config(text='')
      # true if the item doesn't exist in the stock dataframe
      # and also true if the item exists in the stock dataframe, but wasn't added before to the cart box list
      elif in_stock:
        self.cart_boxlist.insert(tk.END,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')  
        self.error_visor.config(text='')
      else:
        self.error_visor.config(text='You need more of that item!') 
      order_items.focus()
    def fillout(e):
      """
      Event function that is run when the user selects an item from the list box,
      this function auto completes the user input.
      * user clicks an item from the list box , which runs this function.
      * the selected item then is auto filled into the user entry box.
      """
      order_items.delete(0,tk.END)
      if entries_boxllist.get(entries_boxllist.curselection()):
        # append the selected item into the menu list box
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))   
    def check(e):
      """
      Event function that takes all the item in the dataframe
      that contain a substring of the user's input, then it auto fills
      those item only to the list box.
      * makes it easier for the user to find thier item easily
      * uses python's 'in' operator
      """
      inthere=order_items.get()
      # assigns the whole dataframe if the input is empty
      if inthere== '':
        displayed_data=df_pd['item_name'].tolist()
      else:
        displayed_data=[]
        for i in df_pd['item_name'].tolist():
          # finds similr items
          if inthere.lower() in i.lower():
            displayed_data.append(i)
      # display the item onto the menu listbox
      listbox_update(displayed_data)
      # select the first row item
      entries_boxllist.select_set(0)
    def finalize(tb_pd):
      """
      This function is run after the confirm function check out the cart.
      This handels other transaction columns, and calls the summary_page
      to prompt the user with the recipt.
      parameters:
        tb_pd: pandas dataframe that holds transaction information
      """
      # change the unique id for the take-away orders
      app.frames['session_order_page'].take_count+=1
      # overwrite and update to config.json
      config_data['tk_num']=app.frames['session_order_page'].take_count
      json_update()
      # update the transaction's time info
      # this is used to be written onto the transaction database
      tb_pd['start_time'] = dt.now()
      tb_pd['end_time']=dt.now()
      tb_pd['time']=dt.now()-dt.now()
      # this is used for the recipt display
      tb_pd['start time display'] = dt.now().strftime('%I:%M:%S-%p')
      tb_pd['end time display']=dt.now().strftime('%I:%M:%S-%p')
      tb_pd['time display']="0:00:00"
      # wifi charge is zero since this is a take-away order
      tb_pd['wifi']=0
      tb_pd['paid_total']=tb_pd['order_total']
      summary_page.transfrom_enter(tb_pd)           
      stacker.show_frame('summary_page') 
    # label top
    item_label=tk.Label(self,height = 1, width = 15 ,text=('Quick Take Away'),font=('Helvetica',18),bg='light grey')
    item_label.place(x=10,y=10)
    # entry box
    order_items=tk.Entry(self,font=("Times",25))
    order_items.place(x=10,y=60)
    # enter amount
    order_amount_var=tk.StringVar()
    order_amount_var.set(1)
    order_amount_menu = tk.OptionMenu(self, order_amount_var, *amount)
    order_amount_menu.place(x=360,y=70)      
    # item list box
    entries_boxllist=tk.Listbox(self,font=('italic',15),width=30,exportselection=False,selectmode='MULTIPLE')
    entries_boxllist.place(x=10,y=110)    
    # bind from list box to entry box
    listbox_update(df_pd['item_name'].tolist())        
    entries_boxllist.bind('<<ListboxSelect>>',fillout)
    # bind entry box
    order_items.bind("<KeyRelease>",check)
    order_items.bind('<Tab>', tab_handler)
    order_items.bind('<Return>',add_item)
    # enter button for item
    btn_insert_item=tk.Button(self,width=10,text=('Add Item'),font=('Helvetica',16,'bold'),bg='light grey',command=add_item)
    btn_insert_item.place(x=350,y=120)
    # delete all button
    delete_cart_btn=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='light grey', command=empty_cart)
    delete_cart_btn.place(x=350,y=200)    
    # box list of cart
    self.cart_boxlist=tk.Listbox(self,width=70,height=11,font=('Helvetica',15),exportselection=True,selectmode='SINGLE')
    self.cart_boxlist.bind('<Double-1>',dble_clk_del)
    self.cart_boxlist.bind('<BackSpace>', empty_cart)
    self.cart_boxlist.place(x=8,y=360)
    # confirm button for items in cart
    confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='light grey',
                    command=lambda: Confirm(self=self,tk_or_sess=False,stay_name=f'Take-away {self.take_count}'
                    ,func = finalize))      
    confirm_button.place(x=350,y=280)
    # updates widnow for errors
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',15,'bold'),bg='light grey')
    self.error_visor.place(x=300,y=20)      
    def delete_session():
      """
      This function handels the deletion of sessions.
      """
      # get the position on the listbox
      size=len(self.session_boxlist.curselection())
      if size:
          index=self.session_boxlist.curselection()[0]
          name=self.session_boxlist.get(index)        
          print('selected delete',index,name)
          self.session_boxlist.delete(index)  
          # delete the session object from session_dict
          del session_dict[name]
      else:
        print('empty delete')        
        sleep(0.3)
      # update the sessions table from database    
      session_update() 
    def create_session():
      """
      This function create the session object.
      """
      # change the unique id
      self.table_count+=1
      # create the unique session name
      x=f'Session {self.table_count}'
      # create the session object assigned with the session's name, and 
      # a date time object that accounts for the start time of this session's creation
      session_dict[x]=sessions(dt.now(),x)
      # append the name into the session list box
      self.session_boxlist.insert('end',x)
      # update the config.json file
      config_data['session_num']= self.table_count
      json_update()
      # update the session's table from database
      session_update()
    def enter_session(e):
      """
      This function handels the entring sequence when double clicking
      on a session.
      """
      size=len(self.session_boxlist.curselection())
      if size:
        index=self.session_boxlist.curselection()[0]
        name=self.session_boxlist.get(index)        
        print('selected',index,name)
        sessions.enter_session(session_dict[name])
        stacker.show_frame('orders_page')
      else:
        print('empty')        
        sleep(0.3)       
    # session creater list label
    session_label=tk.Label(self,height=1,width=12,text='Session List',font=('Helvetica',16,'bold'),bg='light grey')
    session_label.place(x=900,y=60)
    # list box for sessions creation
    self.session_boxlist=tk.Listbox(self,height=20,width=20,font=(16),exportselection=False,selectmode='SINGLE')
    self.session_boxlist.bind('<Double-1>',enter_session)
    self.session_boxlist.place(x=900,y=100)      
    # list session box create button
    creater_button=tk.Button(self,height=1,width=3,text='C',font=('Helvetica',20,'bold'),
                             fg='dark green',bg='light grey',command=create_session)
    creater_button.place(x=830,y=100)
    # deleter button
    deleter_button=tk.Button(self,height=1,width=3,text='D',font=('Helvetica',20,'bold'),
                             fg='dark red',bg='light grey',command=delete_session)
    deleter_button.place(x=830,y=170)    
    #seperation middle line
    middle_line=tk.Canvas(self,width=5,height=680,bg='black')
    middle_line.place(x=800,y=10)
    # return button
    go_back=tk.Button(self,width=40,font=20,text=('Go Back <(----'),command=lambda: stacker.show_frame('startpage'),bg='light grey')
    go_back.place(x=8,y=650)       
class sessions():
  """
  This class handels the session object which indiactes that a customer has arrived at the cafe,
  also calculates the wifi charge, and handels certain cart operations for each sessions
  """
  def __init__(self,start_time,session_name,cart=[]):
    """
    each session has to have a start_time, and a name.
    the cart is kept by default empty
    """
    self.start_time=start_time
    self.session_name= session_name
    self.cart=cart
  def enter_session(self):  
    """
    This calls a function (transfrom_enter)
    which auto fills any session information into the orders_page
    """
    app.frames['orders_page'].transform_enter(self.session_name,self.cart)
  def calculate_nps(self):
    """
    This function calculates and returns the wifi charge, start time, end time of the session
    """
    # end time of the session
    self.end_time=dt.now()
    # handels any changes done to the start_time arrtibute of the session
    if type(self.start_time)==str:
      self.start_time = parser.parse(self.start_time)
    if type(self.start_time)==np.datetime64:
      timestamp = ((self.start_time - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
      self.start_time=dt.utcfromtimestamp(timestamp)
    # Time: the amount of time the session has lasted fore
    Time=self.end_time-self.start_time
    hours=Time.seconds//3600
    Time_disp=Time
    # Time is used as the transaction column
    Time=str(Time)
    # Time_disp is used as the display string on the recipt
    Time_disp-=timedelta(days=Time_disp.days,microseconds=Time_disp.microseconds)
    # this calucates the wifi charge based on the cafe requiremnts
    if hours > 0 and hours < 5:
      hours-=1
      Wifi=(hours*5)+5
    elif hours <= 0:
      Wifi=5
    elif hours >= 5:
      Wifi=25
    else:
      raise Exception("Start and End time of the session has resulted in a non intger diffrence (NPS)")
    # return dictionary
    return({'start time display':self.start_time.strftime('%I:%M:%S-%p'),'end time display': self.end_time.strftime('%I:%M:%S-%p')
    ,'time display': str(Time_disp),'wifi':Wifi,'start_time':self.start_time,'end_time':self.end_time,'time':Time})
class orders_page(tk.Frame):
  """
  This page handles the session's user interface, it is responsible for 
  session's cart items. This page's structure doesn't change, only some fields are 
  changed when a new session is entered on this page that might have a differnet 
  cart or name.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker     
    # self.table: holds whether the order row is a take-away or in-store,
    # as you can order take-away orders in a session
    self.table=tk.IntVar()
    self.table.set(1)
    # table button which decide the above variable
    No_table = tk.Radiobutton(self, text="Take-Away / No table",font=('Helvetica',16,'bold'),
                              variable=self.table, value=0,borderwidth=3,cursor='exchange',bg='#ffd9d9',fg='black')
    Yes_table = tk.Radiobutton(self, text="In store / Yes table",font=('Helvetica',16,'bold'), 
                               variable=self.table, value=1,borderwidth=3,cursor='heart',bg='#ffd9d9',fg='black')
    Yes_table.place(x=15,y=5)
    No_table.place(x=15,y=50)
    def listbox_update(item):
      """
      Function that updates the listbox with the passed argument items
      without any manipulation.
      parameters
        item: list object that contains the items to be filled
      """
      # clear the cart box list 
      entries_boxllist.delete(0,tk.END)
      # add the items to the car box list
      for i in item:
        entries_boxllist.insert(tk.END,i)
    def dble_clk_del(e):
      """
      Event function that delets an item row from the list box cart when double clicked on
      by the user.
      """
      # true if a selection exists 
      if self.cart_boxlist.curselection():
        self.cart_boxlist.delete(self.cart_boxlist.curselection()) 
      else:
        sleep(0.3)
    def tab_handler(e):
      """
      Event function run on pressing tab while selecting the entry box,
      this function selects the first item that appears on the list box
      and assign that to the user's entry box
      """
      # get the list box's size
      z=entries_boxllist.size()
      if order_items.get() and z:
        # clear selection, delete the user's entry box
        entries_boxllist.selection_clear(0, 'end')
        order_items.delete(0,tk.END)        
        # select the first index of menu list box and append it to the user's entry box
        entries_boxllist.select_set(0)                      
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))
      order_items.focus()        
    def empty_cart(*args):
      """
      Deletes all the cart list box's row
      """
      self.cart_boxlist.delete(0,'end')
    def add_item():
      """
      This function adds items to the cart listbox specified by the user,
      and handels any changes in stock if that item were to exist in both
      the menu and the stock dataframes. Also handels repeated item entries
      and incorrect user inputs
      """
      # get user input, amount, item
      y=int(order_amount_var.get())
      z=order_items.get()
      # amount of menu items that are equal to the user input
      # can only be one or 0
      zlen=(df_pd['item_name']==z).sum()
      # handle items existing in both the menu and the stock dataframe
      try:
        # will not cause errors
        # if there exists and item with the same name in the stock dataframe
        # as the item selected by the user
        stock=int(df_st.loc[df_st['item_name']==z,['item_stock']].values)
        # true if the user tries to buy a non exsiting item
        if stock<1:
          self.error_visor.config(text='That item is out of stock!')
          return()
        # true if the user tries to buy more items than he currenlty has
        if stock-y<0:
          self.error_visor.config(text='You need more of that item!')
          return()
        # if all above is false, this variable later declares that this item's stock amount in 
        # the stock table will be changed if assinged to true
        stocked=True
      except:
        stocked=False       
      # true if the user doesn't have any input
      if not z:
        self.error_visor.config(text='Please select an order')
      # true if the input isn't any items from the menu
      elif not zlen:      
        self.error_visor.config(text='Incorrect order, Pick from the list') 
      else:
        if self.table.get():
          x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
          # price is the in-store price of that item
          x=x.price
          table='1 In Store'
        else:
          x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
          # price_ta is the take-away price of that item
          x=x.price_ta
          table='0 Take Away'
        # add_var: is used to decide if the item already exists in the list box 
        # or not, this ensures that repeated items share the same row
        add_var=False
        # in_stock: this is used to take into account the amount of the item's count
        # in the cart list box, to avoid having negative stock
        in_stock=True
        # loop over the cart box list
        for i in range(self.cart_boxlist.size()):
          g=self.cart_boxlist.get(i)
          # true if the user's inputted item is in the selected row from the list box
          if z in g:
            # true if the item's table type (no table-0, yes table-1) is the same as
            # the selected item
            if int(g[g.find('-')+1]) == self.table.get():
              if stocked:
                # true if the item's amount in stock -- minus -- the
                # additional amonut + the amount already existing in the cart
                # is more than or equal to zero. To avoid negative stock errors
                if stock-(y+int(g[g.find("nt:(")+4:g.find(")-")]))>=0:
                  print('already here, adding counts..')
                  # set true to add the user's specified amount to the already existing row
                  add_var=True
                  break
                else:
                  in_stock=False
                  break
              else:
                add_var=True
        # true if item exists in stock, and could be increased
        if add_var and in_stock:
          y+=int(g[g.find("nt:(")+4:g.find(")-")])
          self.cart_boxlist.delete(i)
          # change the row
          self.cart_boxlist.insert(i,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')
          self.error_visor.config(text='')
        # true if the item doesn't exist in the stock dataframe
        # and also true if the item exists in the stock dataframe, but wasn't added before to the cart box list
        elif in_stock:
          self.cart_boxlist.insert(tk.END,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')  
          self.error_visor.config(text='')
        else:
          self.error_visor.config(text='You need more of that item!') 
        order_items.focus()
    def fillout(e):
      """
      Event function that is run when the user selects an item from the list box,
      this function auto completes the user input.
      * user clicks an item from the list box , which runs this function.
      * the selected item then is auto filled into the user entry box.
      """
      order_items.delete(0,tk.END)
      # add selected item to user's entry box
      if entries_boxllist.get(entries_boxllist.curselection()):
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))   
    def check(e):
      """
      Event function that takes all the item in the dataframe
      that contain a substring of the user's input, then it auto fills
      those item only to the list box.
      * makes it easier for the user to find thier item easily
      * uses python's 'in' operator
      """
      inthere=order_items.get()
      # assign the whole dataframe if the user's input is empty
      if inthere== '':
        displayed_data=df_pd['item_name'].tolist()
      else:
        displayed_data=[]
        for i in df_pd['item_name'].tolist():
          if inthere.lower() in i.lower():
            # append similr items into a list
            displayed_data.append(i)
      # display the list of similr items onto the menu list box
      listbox_update(displayed_data)
      entries_boxllist.select_set(0)
    def exit_seq():
      """
      Exit sequence function that saves the session's cart on exiting,
      and clears the order_page's fields in order to fill them with other
      session on entry.
      """
      # save the session by passing its cart
      app.frames['orders_page'].transform_save(self.cart_boxlist.get(0,'end'))
      # get the session_orders_page box list
      session_boxlist=app.frames['session_order_page'].session_boxlist
      # print which session was saved
      index=session_boxlist.curselection()[0]
      name=session_boxlist.get(index)        
      print('Saved and left',index,name)
      # delete the cart box in the orders_page
      self.cart_boxlist.delete(0,'end')
      stacker.show_frame('session_order_page')
      self.table.set(1)  
    # top label
    item_label=tk.Label(self,height = 1, width = 10 ,text=('Orders'),font=('Helvetica',16,'bold'),bg='#bfbfbf')
    item_label.place(x=15,y=110)
    # user entry box
    order_items=tk.Entry(self,width=20,font=("Times",20))
    order_items.place(x=15,y=150)
    # count of item option box + vars
    order_amount_var=tk.StringVar()
    order_amount_var.set(1)
    order_amount_menu = tk.OptionMenu(self, order_amount_var, *amount)
    order_amount_menu.place(x=300,y=153)      
    # user's cart list box
    entries_boxllist=tk.Listbox(self,width=30,font=(16),exportselection=False,selectmode='MULTIPLE')
    entries_boxllist.place(x=15,y=200)    
    # fill the menu with the menu dataframe
    listbox_update(df_pd['item_name'].tolist())
    # bindings        
    entries_boxllist.bind('<<ListboxSelect>>',fillout)
    order_items.bind("<KeyRelease>",check)
    order_items.bind('<Tab>', tab_handler)
    # insert item from menu to cart button
    btn_insert_item=tk.Button(self,width=10,text=('Add'),font=('Helvetica',16,'bold'),bg='#bfbfbf',command=add_item)
    btn_insert_item.place(x=380,y=148)
    # delete all items from cart button
    delete_cart_btn=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='#bfbfbf', command=empty_cart)
    delete_cart_btn.place(x=570,y=147)    
    # user's cart list box + bindings
    self.cart_boxlist=tk.Listbox(self,height=12,width=66,font=(18),exportselection=True,selectmode='SINGLE')
    self.cart_boxlist.bind('<Double-1>',dble_clk_del)
    self.cart_boxlist.bind('<BackSpace>', empty_cart)
    self.cart_boxlist.place(x=380,y=200)
    # Confirm button that checks out the order
    confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='#bfbfbf',command=lambda: Confirm(self=self,
                    tk_or_sess=True,stay_name=self.session_name.cget('text')
                    ,func = orders_page.finalize))
    confirm_button.place(x=380,y=500)
    # error window label for incorrect user input
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.error_visor.place(x=350,y=50)
    # session name label
    self.session_name=tk.Label(self,height = 1, width = 20 ,text='',font=('Helvetica',20,'bold'),bg='#bfbfbf')
    self.session_name.place(x=400,y=10)        
    # go back button
    go_back=tk.Button(self,width=30,font=15,text=('Go Back <(----'),pady=10,bg='#bfbfbf',command=exit_seq)
    go_back.pack(side='bottom')  
  def transform_enter(self,session_name,cart_in):
    """
    This function is called from outside the orders_page and so
    it is not placed inside the __init__ constructor. This function
    handles the entering of a session and fills out any beforehand
    saved cart items.
    """
    # true if the session has more than one item in cart
    if len(cart_in)>1:
      for i in range(len(cart_in)):
        app.frames['orders_page'].cart_boxlist.insert('end',cart_in[i].strip())
    # true if the session has 1 item in which we choose the first index 
    # as the saved tuple sometimes has a second empty index 
    elif len(cart_in)==1:
      app.frames['orders_page'].cart_boxlist.insert('end',cart_in[0].strip())#.replace("'",'').split(',') # 
    # if the user didn't add any items before
    else:
      app.frames['orders_page'].cart_boxlist.delete(0,'end')
    app.frames['orders_page'].session_name.config(text=session_name)
    print('entered:', session_name)
  def transform_save(self,cart):
    """
    This function saves the session's cart and overwrites it
    to the session_dict dictionary and then saves that to
    the sessions table from database
    """
    # get the session's name
    session_name=app.frames['orders_page'].session_name.cget('text')
    # save the session's cart into the dict
    if len(cart)!=0:
      session_dict[session_name].cart=cart
    else:
      session_dict[session_name].cart=''
    print('saved:',session_dict[session_name])
    # save the dict to databse
    session_update()
  def finalize(df):
    """
    This function is run after the confirm function check out the cart.
    This handels other transaction columns, and calls the summary_page
    to prompt the user with the recipt.
    parameters:
      df: pandas dataframe that holds transaction information
    """
    session_boxlist=app.frames['session_order_page'].session_boxlist
    index=session_boxlist.curselection()[0]
    sess_name=session_boxlist.get(index)  
    # no_order is used to add an extra 5 pound charge
    # for cutomers who didn't order
    no_order=df['order_total'].sum()==0
    # get the wifi/time related transaction columns
    transaction_time=sessions.calculate_nps(session_dict[sess_name])
    df['start_time']=transaction_time['start_time']
    df['end_time']=transaction_time['end_time']
    df['time']=transaction_time['time']
    df['start time display']=transaction_time['start time display']
    df['end time display']=transaction_time['end time display']
    df['time display']=transaction_time['time display']
    df['wifi']=transaction_time['wifi']
    if(no_order):
      df['wifi']+=5
    df['paid_total'] = df['order_total'][0]+df['wifi'][0]
    # display the recipt
    summary_page.transfrom_enter(df)      
    app.frames['orders_page'].stacker.show_frame('summary_page')       
    # deletion sequence of the session
    app.frames['orders_page'].cart_boxlist.delete(0,'end')
    session_boxlist.delete(index)      
    del session_dict[sess_name]
    app.frames['orders_page'].table.set(1)   
    # update session table from database
    session_update()       
class summary_page(tk.Frame):
  """
  This page shows the final recipt on the take-away orders
  and the session orders.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker 
    # empty labels assigned with each field of the transaction
    self.info_time =tk.Label(self ,text='',font=('Helvetica','16','bold'),
                        justify="left",bg='#bfbfbf',fg='black')
    self.info_names =tk.Label(self ,text='',font=('Helvetica','18'),
                        justify="left",bg='#bfbfbf',fg='black')
    self.info_p =tk.Label(self ,text='',font=('Helvetica','18'),
                        justify="left",bg='#bfbfbf',fg='black')
    self.info_c=tk.Label(self ,text='',font=('Helvetica','18'),
                        justify="left",bg='#bfbfbf',fg='black')
    self.info_t =tk.Label(self ,text='',font=('Helvetica','18'),
                        justify="left",bg='#bfbfbf',fg='black')   
    self.info_h =tk.Label(self ,text='',font=('Helvetica','18','bold'),
                        justify="left",fg='black')   
    self.info_paid =tk.Label(self ,text='',font=('Helvetica','23'),
                        borderwidth=1,relief="groove",justify="left",fg='black',pady=3,padx=3)      
    # placments
    self.info_time.place(x=20,y=20)  
    self.info_names.place(x=20,y=200)
    self.info_p.place(x=480,y=200)
    self.info_c.place(x=600,y=200)
    self.info_t.place(x=720,y=200)  
    self.info_h.place(x=20,y=160)
    self.info_paid.place(x=800,y=160)
    # exit button that records the transaction into the transactions
    # table from database
    btn_paid = tk.Button(self,width=10,height=2,text='Paid'
                      ,bg='#0a6300',font=('lucida','12','bold'),fg='#d9d9d9',command=lambda :summary_page.paid(self.curr_data))
    btn_paid.place(x=500,y=20)
  def paid(df):
    """
    Function that confirms the completion of the transaction and
    appends the transaction information as a row in the transaction
    table from database
    parameters:
      df: pandas dataframe that holds all the transaction columns and info
    """
    # cleaning
    df.drop(['item_name','item_price','start time display','end time display','time display'],axis=1,inplace=True)  
    # append row
    to_db("transactions",df,exist="append")       
    app.frames['summary_page'].stacker.show_frame('session_order_page')
  def transfrom_enter(df):
    """
    This function fills the transaction columns onto 
    the empty labels created in the __init__ constructor
    """
    # curr_data is used as a transportaion variable that holds the dataframe's
    # information from outside the class and then assigns it to the current page
    # object, so that it could be accessed from an inner class
    app.frames['summary_page'].curr_data= df
    # fill the empty fields
    recipt_time="{}\n\nStart Time: {}\nEnded:        {}\nTime Stayed: {}".format(df['stay'][0]
                                                                                ,df['start time display'][0]
                                                                                ,df['end time display'][0],
                                                                                df['time display'][0])
    recipt_names=''
    recipt_p=''
    recipt_c=''
    recipt_t=''
    recipt_head=f"Items{55*' '}Price        Count        Total"
    recipt_paid="Orders: {} \n\nWifi: {} \n\nOrders+Wifi: {}".format(int(df['order_total'][0])
                                                                    ,int(df['wifi'][0])
                                                                    ,int(df['paid_total'][0]))
    for i in range(df.shape[0]):
      recipt_names+=f"{df['item_name'][i]}\n"
      recipt_p+=f"\n{df['item_price'][i]}"
      recipt_t+=f"\n{df['item_total'][i]}"
      recipt_c+=f"\n{df['item_count'][i]}"
    recipt_names=recipt_names[:-1:1]  
    recipt_p=recipt_p[1:]
    recipt_c=recipt_c[1:]
    recipt_t=recipt_t[1:]
    # assignment
    for g, i, in zip((app.frames['summary_page'].info_time,
                      app.frames['summary_page'].info_names,
                      app.frames['summary_page'].info_p,
                      app.frames['summary_page'].info_c,
                      app.frames['summary_page'].info_t,
                      app.frames['summary_page'].info_h,
                      app.frames['summary_page'].info_paid), (recipt_time,recipt_names,
                                                                recipt_p,
                                                                recipt_c,
                                                                recipt_t,
                                                                recipt_head,
                                                                recipt_paid)):
      g.config(text=i)
if __name__ == "__main__":
  # open configration settings
  with open(f'{cur_dir}\config.json','r+') as json_file:
    config_data = json.load(json_file)
  # reset the counters to zero incase the current saved date
  # on the config file doesn't match today
  if config_data['today'] == dt.now().strftime('%Y-%m-%d'):
    table_counter= config_data['session_num']
    take_away_counter=config_data['tk_num']
    stock_counter=config_data['stock_num']
    book_counter=config_data['book_num']
    today=config_data['today']   
  else: 
    # Change config file's date to today's date
    config_data['today']=dt.now().strftime('%Y-%m-%d')
    config_data['session_num'], config_data['tk_num'],config_data['stock_num']=0, 0 , 0
    truncate("sessions")
    # write the new change into the config.json file
    with open(f"{cur_dir}\config.json", "w") as outfile:
      json.dump(config_data,outfile,indent=4)
    # assign the new counters
    table_counter= config_data['session_num']
    take_away_counter=config_data['tk_num']
    stock_counter=config_data['stock_num']
    book_counter=config_data['book_num']
    today=config_data['today']
  print(f"{config_data['today']}: {config_data['session_num']} sessions")
  #driver
  app = main_app()
  open_sessions()
  app.mainloop()
# Created By Mohamed Galal Elgemeie
# all rights reserved
