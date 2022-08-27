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
  print(temp_df)
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
    print(tb_pd)
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
        print(query,query_book) 
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
        print(query,query_book)
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
  This class handels transactions of the books and printed paper into
  the books table from db. nig
  """
  def __init__(self,parent,stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    def printed():
      paper=paper_amount_e.get()
      if paper_amount_e:
        try:
          paper=int(paper)

        except:
          self.error_visor.config(text="The paper amount has to be a number/عدد الورق يجب ان يكن رقم")
          return
        temp_df=pd.DataFrame({'name': [paper],'price': [paper*0.75],
            'stay': ["paper"],
            'start_time': dt.now()})
        print(temp_df)
        to_db("books",temp_df,exist="append")
        paper_amount_e.delete(0,tk.END)
        self.error_visor.config(text='تم التسجبل')
      else:
        self.error_visor.config(text="one of the fields is empty/احد  الإدخالات فارغ")

    def buy():
      global book_counter
      name=book_name_e.get()
      price=book_price_e.get()
      if name and price:
        try:
          int(price)
          if(name.isdigit()):
            self.error_visor.config(text="The name has to have letter/الاسم يجب ان يكن متكون من حروف")
            return
        except:
          self.error_visor.config(text="The price has to be a number/السعر يجب ان يكن رقم")
          return
        temp_df=pd.DataFrame({'name': [name],'price': [price],
                  'stay': [f"book {book_counter}"],
                  'start_time': dt.now()})
        book_counter+=1
        config_data['book_num']=book_counter
        json_update()
        print(temp_df)
        to_db("books",temp_df,exist="append")
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

  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    # placed here to avoid refrence before assignment errors
    self.stock_amount=tk.IntVar()
    self.stock_amount.set(1)
    self.stock_entry=tk.Entry(self,font=("Helvetica",28),width=30)
    self.error_visor=tk.Label(self,height = 2, width = 40 ,text="Errors are shown here",font=('Helvetica',15,'bold'),bg='light grey')
    def exit_seq():
      global df_st
      df_st=look("stock")
      stock_page.listbox_update(self)
      stock_page.warn(self)
      stacker.show_frame('startpage')
    def add_price():
      global df_st
      global stock_counter
      if(self.stock_entry.get()==''):
        self.error_visor.config(text='Enter the stock price/أدخل سعر السلعة')
        return
      try:
        price=int(self.stock_entry.get())
      except:
        self.error_visor.config(text='Only enter the stock price Number/ادخل اركام فقط')
        return
      if df_st.equals(look("stock")):
        self.error_visor.config(text="You didn't change the Stock/أنت لم تغير المخزون")
        return
      if price<0:
        self.error_visor.config(text="Price can't be less than zero!/لا يمكن أن يكون السعر أقل من صفر!")
        return      
      temp_df=pd.DataFrame({'item_id':[-1],'item_count': [0],'item_total': [0],
                'order_total': [0],'table': [False],'stay': [f"stock {stock_counter}"],
                'start_time': dt.now(),'end_time':dt.now(),'time':dt.now()-dt.now(),
                'wifi':[0],'paid_total':[-price]})
      stock_counter+=1
      config_data['stock_num']=stock_counter
      json_update()

      print(temp_df)
      to_db("transactions",temp_df,exist="append")
      truncate('stock')
      to_db('stock',df_st,'append')
      self.error_visor.config(text='')
      self.stock_entry.delete(0,"end")
      self.stock_entry.focus()
      self.stock_amount.set(1)
    def change(add):
      y=int(self.stock_amount.get())
      z=self.stock_entry.get().strip()
      #handlling of empty input error + entry not in menu error
      zlen=(df_st['item_name']==z).sum()
      if not z:
        self.error_visor.config(text='Please Select an Item!')
      elif not zlen:      
        self.error_visor.config(text='Incorrect Item, Please Select from the List') 
      else:
       # temp_id=df_st[df_st['item_name']==z].reset_index(drop = True)
#        df_st[df_st['item_name']==z]['item_stock']=
        if add:
          df_st.loc[df_st['item_name']==z,['item_stock']]+=y
        else:
          if df_st.loc[df_st['item_name']==z,['item_stock']].values==0:
            self.error_visor.config(text="You don't have that Item! Please buy some")
            self.stock_entry.focus()
            return()
          elif (df_st.loc[df_st['item_name']==z,['item_stock']].values-y)<0:
            self.error_visor.config(text=f"You can't delete {y} if you only have {df_st.loc[df_st['item_name']==z,['item_stock']].values}")
            self.stock_entry.focus()
            return()
          else:
            df_st.loc[df_st['item_name']==z,['item_stock']]-=y
        stock_page.listbox_update(self)
        stock_page.warn(self)
        self.error_visor.config(text='')
      self.stock_entry.focus()

     #   displayed_data.append() 
      #clear the box list:
      #add the items to the box:
     # for i in item:
     #   self.stock_menu.insert(tk.END,i)

    #update function
    def fillout(e):
      self.stock_entry.delete(0,tk.END)
      #add list item to entry box
      if self.stock_menu.get(self.stock_menu.curselection()):
        x=self.stock_menu.get(self.stock_menu.curselection())
        self.stock_entry.insert(0,x[:x.find('-')])   
   
    def tab_handler(e):
      box_size=self.stock_menu.size()
      #makes tab take the lastest item from the list box of items
      if self.stock_entry.get() and box_size:
        self.stock_menu.selection_clear(0, 'end')
        self.stock_entry.delete(0,tk.END)        
        self.stock_menu.select_set(0) 
        x=self.stock_menu.get(self.stock_menu.curselection())
        self.stock_entry.insert(0,x[:x.find('-')])                        
       # self.stock_entry.insert(0,self.stock_menu.get(self.stock_menu.curselection()))
      self.stock_entry.focus()  
      
    def check(e):
      inthere=self.stock_entry.get().lower().strip()
      if inthere== '':
        stock_page.listbox_update(self)  
      else:
        self.stock_menu.delete(0,tk.END)
        for i,g in zip(df_st['item_name'].values,df_st['item_stock'].values):
          if inthere in i.lower():
            self.stock_menu.insert(tk.END,f'{i}-  {g}')

      self.stock_menu.select_set(0)    

    go_back=tk.Button(self,font=20,text=('Go Back <(----'),command=lambda: exit_seq())
    self.stock_menu=tk.Listbox(self,font=("Helvetica",16),justify='right',relief='solid',height=26,width=30,exportselection=False,selectmode='SINGLE')
    
    add_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#07D712',bg='#f5f5f5',height=1,text="Add Stock",command=lambda: change(True))
    remove_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#D72C2C',bg='#f5f5f5',height=1,text="Del Stock ",command=lambda: change(False))
    change_btn=tk.Button(self,font=('Helvetica',16,'bold'),fg='#E68C00',bg='#f5f5f5',width=12,height=1,text="Confirm",command=lambda: add_price())

    self.warning=tk.Label(self,height=19,justify='left', width = 50 ,text="Warnings are shown here",font=('Helvetica',15),bg='light grey')
    
    self.stock_amount_option = tk.OptionMenu(self, self.stock_amount, *amount)
    #bind list box
     
    stock_page.listbox_update(self)     
    stock_page.warn(self)

    self.stock_menu.bind('<<ListboxSelect>>',fillout)
    self.stock_entry.bind("<KeyRelease>",check)
    self.stock_entry.bind('<Tab>', tab_handler)
    #---
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
    warning=''
    for i,g in zip(df_st['item_stock'].values,df_st['item_name'].values):
      if(i<8):
        warning+=f"Now! {g} - You have {i}\n"    
      elif(i<15):
        warning+=f"Tomorrow! {g} - You have {i}\n"
    self.warning.config(text=warning[:-1])
  def listbox_update(self):
    self.stock_menu.delete(0,tk.END)
    for i,g  in zip(df_st['item_name'].values,df_st['item_stock'].values):
        self.stock_menu.insert(tk.END,f'{i}-  {g}')
  
class session_order_page(tk.Frame):

  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker
    self.table_count=table_counter
    self.take_count=take_away_counter 
    self.table=tk.IntVar()
    self.table.set(0)
    def listbox_update(item):
      #clear the box list:
      entries_boxllist.delete(0,tk.END)
      #add the items to the box:
      for i in item:
        entries_boxllist.insert(tk.END,i)
    #double click deltetion handler 
    def dble_clk_del(e):
      if not self.cart_boxlist.curselection():
        sleep(0.3)
      else:
        self.cart_boxlist.delete(self.cart_boxlist.curselection())
        
    #tab handler: for felxibilty in typing
    def tab_handler(e):
      box_size=entries_boxllist.size()
      #makes tab take the lastest item from the list box of items
      if order_items.get() and box_size:
        entries_boxllist.selection_clear(0, 'end')
        order_items.delete(0,tk.END)        
        entries_boxllist.select_set(0)                      
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))
      order_items.focus()        
    #deletion function to empty the cart from button
    def empty_cart(*args):
      self.cart_boxlist.delete(0,'end')
      pass
    #add item to table Cart
    def add_item(*args):
      y=int(order_amount_var.get())
      z=order_items.get()

      #handlling of empty input error + entry not in menu error
      zlen=(df_pd['item_name']==z).sum()
      try:
        #print('wow cool',int(g[g.find("nt:(")+4:g.find(")-")]),y,stock)
        stock=int(df_st.loc[df_st['item_name']==z,['item_stock']].values)
        if stock<1:
          self.error_visor.config(text='That item is out of stock!')
          return()
        if stock-y<0:
          self.error_visor.config(text='You need more of that item!')
          return()
        stocked=True
      except:
        stocked=False       

      if not z:
        self.error_visor.config(text='Please Select an Item!')
      elif not zlen:      
        self.error_visor.config(text='Incorrect Item, Please Select from the List') 
      else:
        x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
        x=x.price_ta
        table='0 Take Away'
      add_var=False
      in_stock=True
      for i in range(self.cart_boxlist.size()):
        g=self.cart_boxlist.get(i)
        if z in g:
          if int(g[g.find('-')+1]) == self.table.get():
            if stocked:
              if stock-(y+int(g[g.find("nt:(")+4:g.find(")-")]))>=0:
                print('already here, adding counts..')
                add_var=True
                break
              else:
                in_stock=False
                break
            else:
              add_var=True
      if add_var and in_stock:
        y+=int(g[g.find("nt:(")+4:g.find(")-")])
        self.cart_boxlist.delete(i)
        self.cart_boxlist.insert(i,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')
        self.error_visor.config(text='')
      elif in_stock:
        self.cart_boxlist.insert(tk.END,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')  
        self.error_visor.config(text='')
      else:
        self.error_visor.config(text='You need more of that item!') 
      order_items.focus()
      
    #update function
    def fillout(e):
      order_items.delete(0,tk.END)
      #add list item to entry box
      if entries_boxllist.get(entries_boxllist.curselection()):
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))   
    #check entry box
    def check(e):
      inthere=order_items.get()
      if inthere== '':
        displayed_data=df_pd['item_name'].tolist()
      else:
        displayed_data=[]
        for i in df_pd['item_name'].tolist():
          if inthere.lower() in i.lower():
            displayed_data.append(i)
      listbox_update(displayed_data)
      entries_boxllist.select_set(0)
    def finalize(tb_pd):
          app.frames['session_order_page'].take_count+=1
          config_data['tk_num']=app.frames['session_order_page'].take_count
          json_update()
          # .strftime('%I:%M:%S-%p')
          tb_pd['start_time'] = dt.now()
          tb_pd['end_time']=dt.now()
          tb_pd['time']=dt.now()-dt.now()
          tb_pd['start time display'] = dt.now().strftime('%I:%M:%S-%p')
          tb_pd['end time display']=dt.now().strftime('%I:%M:%S-%p')
          tb_pd['time display']="0:00:00"

          tb_pd['wifi']=0
          tb_pd['paid_total']=tb_pd['order_total']
          summary_page.transfrom_enter(tb_pd)           
          stacker.show_frame('summary_page') 
    #label top
    item_label=tk.Label(self,height = 1, width = 15 ,text=('Quick Take Away'),font=('Helvetica',18),bg='light grey')
    item_label.place(x=10,y=10)
    #entry box
    order_items=tk.Entry(self,font=("Times",25))
    order_items.place(x=10,y=60)
    #enter amount
    order_amount_var=tk.StringVar()
    order_amount_var.set(1)
    order_amount_menu = tk.OptionMenu(self, order_amount_var, *amount)
    order_amount_menu.place(x=360,y=70)      
    #item list box
    entries_boxllist=tk.Listbox(self,font=('italic',15),width=30,exportselection=False,selectmode='MULTIPLE')
    entries_boxllist.place(x=10,y=110)    
    #bind from list box to entry box
    listbox_update(df_pd['item_name'].tolist())        
    entries_boxllist.bind('<<ListboxSelect>>',fillout)
    #bind entry box
    order_items.bind("<KeyRelease>",check)
    order_items.bind('<Tab>', tab_handler)
    order_items.bind('<Return>',add_item)
    #enter button for item
    btn_insert_item=tk.Button(self,width=10,text=('Add Item'),font=('Helvetica',16,'bold'),bg='light grey',command=add_item)
    btn_insert_item.place(x=350,y=120)
    #delete all button
    delete_cart_btn=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='light grey', command=empty_cart)
    delete_cart_btn.place(x=350,y=200)    
    #box list of cart
    self.cart_boxlist=tk.Listbox(self,width=70,height=11,font=('Helvetica',15),exportselection=True,selectmode='SINGLE')
    self.cart_boxlist.bind('<Double-1>',dble_clk_del)
    self.cart_boxlist.bind('<BackSpace>', empty_cart)
    self.cart_boxlist.place(x=8,y=360)
    #Confirm button for items in cart
    confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='light grey',
                    command=lambda: Confirm(self=self,tk_or_sess=False,stay_name=f'Take-away {self.take_count}'
                    ,func = finalize))
                    
    confirm_button.place(x=350,y=280)
    #updates widnow for errors
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',15,'bold'),bg='light grey')
    self.error_visor.place(x=300,y=20)      
    #---------------------------------------------------------------------------------------------------------------------------------------#
    #session creater section
    #delete session function
    def delete_session():
      size=len(self.session_boxlist.curselection())
      if size:
          index=self.session_boxlist.curselection()[0]
          name=self.session_boxlist.get(index)        
          print('selected delete',index,name)
          self.session_boxlist.delete(index)  
          del session_dict[name]
         # del config_data[name]
        #  json_update()
      else:
        print('empty delete')        
        sleep(0.3)    
      session_update() 
      #to_db("sessions",pd.DataFrame(session_dict),exist="replace")

    #create session function
    def create_session():
      self.table_count+=1
      x=f'Session {self.table_count}'
      session_dict[x]=sessions(dt.now(),x)

      self.session_boxlist.insert('end',x)
      config_data['session_num']= self.table_count
      json_update()
      session_update()
      """ vars_open = open(f'{cur_dir}\-vars.txt','r+') 
      vars1=vars_open.read()
      vars1=str(self.table_count)+vars1[vars1.find(','):]
      vars_open.seek(0)
      vars_open.truncate(0)
      vars_open.write(vars1)
      vars_open.close()"""
      
    #function from double click on session instance to enter the orders page
    def enter_session(e):
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
    #session creater list label
    session_label=tk.Label(self,height=1,width=12,text='Session List',font=('Helvetica',16,'bold'),bg='light grey')
    session_label.place(x=900,y=60)
    #list box for sessions creation
    self.session_boxlist=tk.Listbox(self,height=20,width=20,font=(16),exportselection=False,selectmode='SINGLE')
    self.session_boxlist.bind('<Double-1>',enter_session)
    self.session_boxlist.place(x=900,y=100)      
    #list session box create button
    creater_button=tk.Button(self,height=1,width=3,text='C',font=('Helvetica',20,'bold'),
                             fg='dark green',bg='light grey',command=create_session)
    creater_button.place(x=830,y=100)
    #deleter button
    deleter_button=tk.Button(self,height=1,width=3,text='D',font=('Helvetica',20,'bold'),
                             fg='dark red',bg='light grey',command=delete_session)
    deleter_button.place(x=830,y=170)    
    #---------------------------------------------------------------------------------------------------------------------------------------#    
    #seperation line middle line
    middle_line=tk.Canvas(self,width=5,height=680,bg='black')
    middle_line.place(x=800,y=10)
    #return button
    go_back=tk.Button(self,width=40,font=20,text=('Go Back <(----'),command=lambda: stacker.show_frame('startpage'),bg='light grey')
    go_back.place(x=8,y=650)       
#session creater class
class sessions():
  def __init__(self,start_time,session_name,cart=[]):
    self.start_time=start_time
    self.session_name= session_name
    self.cart=cart
  def enter_session(self):  
    app.frames['orders_page'].transform_enter(self.session_name,self.cart)
  def calculate_nps(self):
    self.end_time=dt.now()#.strftime('%I:%M:%S-%p')
   # self.end_time= datetime.strptime(end_time,'%I:%M:%S-%p')
    #start_time= datetime.strptime(self.start_time,'%I:%M:%S-%p')
    if type(self.start_time)==str:
      self.start_time = parser.parse(self.start_time)
    if type(self.start_time)==np.datetime64:
      timestamp = ((self.start_time - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
      self.start_time=dt.utcfromtimestamp(timestamp)
    
    Time=self.end_time-self.start_time
    hours=Time.seconds//3600
    Time_disp=Time
    #Time-=timedelta(days=Time.days,microseconds=Time.microseconds)
    Time=str(Time)
    Time_disp-=timedelta(days=Time_disp.days,microseconds=Time_disp.microseconds)
    print(self.cart)
   # print(ordered)
    #Time.days=0
    if hours > 0 and hours < 5:
      hours-=1
      Wifi=(hours*5)+5
    elif hours <= 0:
      Wifi=5
    elif hours >= 5:
      Wifi=25
    else:
      raise Exception("Start and End time of the session has resulted in a non intger diffrence (NPS)")

    return({'start time display':self.start_time.strftime('%I:%M:%S-%p'),'end time display': self.end_time.strftime('%I:%M:%S-%p')
    ,'time display': str(Time_disp),'wifi':Wifi,'start_time':self.start_time,'end_time':self.end_time,'time':Time})
    
#orders page
class orders_page(tk.Frame):
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker     
    #transporter for table object from session class
    self.table=tk.IntVar()
    self.table.set(1)
    No_table = tk.Radiobutton(self, text="Take-Away / No table",font=('Helvetica',16,'bold'),
                              variable=self.table, value=0,borderwidth=3,cursor='exchange',bg='#ffd9d9',fg='black')
    Yes_table = tk.Radiobutton(self, text="In store / Yes table",font=('Helvetica',16,'bold'), 
                               variable=self.table, value=1,borderwidth=3,cursor='heart',bg='#ffd9d9',fg='black')
    Yes_table.place(x=15,y=5)
    No_table.place(x=15,y=50)
    #input items of order(search and  autofill box):
    #The items in the menu
    def listbox_update(item):
      #clear the box list:
      entries_boxllist.delete(0,tk.END)
      #add the items to the box:
      for i in item:
        entries_boxllist.insert(tk.END,i)
    #double click deltetion handler 
    def dble_clk_del(e):
      if not self.cart_boxlist.curselection():
        sleep(0.3)
      else:
        self.cart_boxlist.delete(self.cart_boxlist.curselection())
        
    #tab handler: for felxibilty in typing
    def tab_handler(e):
      z=entries_boxllist.size()
      #makes tab take the lastest item from the list box of items
      if order_items.get() and z:

        entries_boxllist.selection_clear(0, 'end')
        order_items.delete(0,tk.END)        
        entries_boxllist.select_set(0)                      
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))
      order_items.focus()        
    #deletion function to empty the cart from button
    def empty_cart(*args):
      self.cart_boxlist.delete(0,'end')
      pass
    
    #add item to table Cart
    def add_item():
      y=int(order_amount_var.get())
      z=order_items.get()
      #handlling of empty input error + entry not in menu error + entry out of stock
      zlen=(df_pd['item_name']==z).sum()
      try:
        #print('wow cool',int(g[g.find("nt:(")+4:g.find(")-")]),y,stock)
        stock=int(df_st.loc[df_st['item_name']==z,['item_stock']].values)
        if stock<1:
          self.error_visor.config(text='That item is out of stock!')
          return()
        if stock-y<0:
          self.error_visor.config(text='You need more of that item!')
          return()
        stocked=True
      except:
        stocked=False       

      if not z:
        self.error_visor.config(text='Please select an order')
      elif not zlen:      
        self.error_visor.config(text='Incorrect order, Pick from the list') 
      else:
        if self.table.get():
          x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
          x=x.price
          table='1 In Store'
        else:
          x=df_pd[df_pd['item_name']==z].reset_index(drop = True)
          x=x.price_ta
          table='0 Take Away'
        #check for duplicates to sum up counts of the same item
        print('-'*50)
        add_var=False
        in_stock=True
        for i in range(self.cart_boxlist.size()):
          g=self.cart_boxlist.get(i)
          if z in g:
            if int(g[g.find('-')+1]) == self.table.get():
              if stocked:
                if stock-(y+int(g[g.find("nt:(")+4:g.find(")-")]))>=0:
                  print('already here, adding counts..')
                  add_var=True
                  break
                else:
                  in_stock=False
                  break
              else:
                add_var=True
        if add_var and in_stock:
          y+=int(g[g.find("nt:(")+4:g.find(")-")])
          self.cart_boxlist.delete(i)
          self.cart_boxlist.insert(i,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')
          self.error_visor.config(text='')
        elif in_stock:
          self.cart_boxlist.insert(tk.END,f'{z}-{table} | Price:({x[0]}) Amount:({y})--Total = {int(y)*int(x[0])}')  
          self.error_visor.config(text='')
        else:
          self.error_visor.config(text='You need more of that item!') 
        order_items.focus()
      
    #update function
    def fillout(e):
      order_items.delete(0,tk.END)
      #add list item to entry box
      if entries_boxllist.get(entries_boxllist.curselection()):
        order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))   
    #check entry box
    def check(e):
      inthere=order_items.get()
      if inthere== '':
        displayed_data=df_pd['item_name'].tolist()
      else:
        displayed_data=[]
        for i in df_pd['item_name'].tolist():
          if inthere.lower() in i.lower():
            displayed_data.append(i)
      listbox_update(displayed_data)
      entries_boxllist.select_set(0)
    #--------------
    #button exit function
    def go_back():
        app.frames['orders_page'].transform_save(self.cart_boxlist.get(0,'end'))
        session_boxlist=app.frames['session_order_page'].session_boxlist
       # size=len(session_boxlist.curselection())
        index=session_boxlist.curselection()[0]
        name=session_boxlist.get(index)        
        print('Saved and left',index,name)
        self.cart_boxlist.delete(0,'end')
        stacker.show_frame('session_order_page')
        self.table.set(1)  
      #--------------
    #label top
    item_label=tk.Label(self,height = 1, width = 10 ,text=('Orders'),font=('Helvetica',16,'bold'),bg='#bfbfbf')
    item_label.place(x=15,y=110)
    #entry box
    order_items=tk.Entry(self,width=20,font=("Times",20))
    order_items.place(x=15,y=150)
    #enter amount
    #amounts=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    order_amount_var=tk.StringVar()
    order_amount_var.set(1)
    order_amount_menu = tk.OptionMenu(self, order_amount_var, *amount)
    order_amount_menu.place(x=300,y=153)      
    #item list box
    entries_boxllist=tk.Listbox(self,width=30,font=(16),exportselection=False,selectmode='MULTIPLE')
    entries_boxllist.place(x=15,y=200)    
    #bind from list box to entry box
    listbox_update(df_pd['item_name'].tolist())        
    entries_boxllist.bind('<<ListboxSelect>>',fillout)
    #bind entry box
    order_items.bind("<KeyRelease>",check)
    order_items.bind('<Tab>', tab_handler)
    #enter button for item
    btn_insert_item=tk.Button(self,width=10,text=('Add'),font=('Helvetica',16,'bold'),bg='#bfbfbf',command=add_item)
    btn_insert_item.place(x=380,y=148)
    #delete all button
    delete_cart_btn=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='#bfbfbf', command=empty_cart)
    delete_cart_btn.place(x=570,y=147)    
    #box list of cart
    self.cart_boxlist=tk.Listbox(self,height=12,width=66,font=(18),exportselection=True,selectmode='SINGLE')
    self.cart_boxlist.bind('<Double-1>',dble_clk_del)
    self.cart_boxlist.bind('<BackSpace>', empty_cart)
    self.cart_boxlist.place(x=380,y=200)
    
    #Confirm button for items in cart
    confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='#bfbfbf',command=lambda: Confirm(self=self,
                    tk_or_sess=True,stay_name=self.session_name.cget('text')
                    ,func = orders_page.finalize))
    confirm_button.place(x=380,y=500)
    #updates widnow for errors
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.error_visor.place(x=350,y=50)
    #session name window
    self.session_name=tk.Label(self,height = 1, width = 20 ,text='',font=('Helvetica',20,'bold'),bg='#bfbfbf')
    self.session_name.place(x=400,y=10)        
    #return button
    go_back=tk.Button(self,width=30,font=15,text=('Go Back <(----'),pady=10,bg='#bfbfbf',command=go_back)
    go_back.pack(side='bottom')  
    
  def transform_enter(self,session_name,cart_in):
    if len(cart_in)>1:
      for i in range(len(cart_in)):
        app.frames['orders_page'].cart_boxlist.insert('end',cart_in[i].strip())#.replace("'",'').split(',') # 
    elif len(cart_in)==1:
      app.frames['orders_page'].cart_boxlist.insert('end',cart_in[0].strip())#.replace("'",'').split(',') # 
    else:
      app.frames['orders_page'].cart_boxlist.delete(0,'end')
    app.frames['orders_page'].session_name.config(text=session_name)
    print('entered:', session_name)

  def transform_save(self,cart):
    session_name=app.frames['orders_page'].session_name.cget('text')
    if len(cart)!=0:
      session_dict[session_name].cart=cart
    else:
      session_dict[session_name].cart=''
    print('saved:',session_dict[session_name])
#    to_db("sessions",pd.DataFrame(session_dict),exist="replace")

    session_update()
  def finalize(df):
      # df.to_csv(table_path,mode='a', index=False,header=False)
        #leaveing sequence  ['item_Name','item_price','item_count','order_total','table','Stay','start_time','end_time','Time','Wifi','Paid Total']
        session_boxlist=app.frames['session_order_page'].session_boxlist
        index=session_boxlist.curselection()[0]
        sess_name=session_boxlist.get(index)  
        no_order=df['order_total'].sum()==0

      #  df={'Start Time':'','End Time':'','item_total':int(),
      #                 'NPS':int(),'NPS Price': int(),'paid total':int()} 
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
        summary_page.transfrom_enter(df)      
        app.frames['orders_page'].stacker.show_frame('summary_page')       
        # deletion sequence
        app.frames['orders_page'].cart_boxlist.delete(0,'end')
        session_boxlist.delete(index)      
        del session_dict[sess_name]
        app.frames['orders_page'].table.set(1)   
        #to_db("sessions",pd.DataFrame(session_dict),exist="replace")

        session_update()       

#recipt summary page
class summary_page(tk.Frame):
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker 

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
    self.info_time.place(x=20,y=20)  
    self.info_names.place(x=20,y=200)
    self.info_p.place(x=480,y=200)
    self.info_c.place(x=600,y=200)
    self.info_t.place(x=720,y=200)  
    self.info_h.place(x=20,y=160)
    self.info_paid.place(x=800,y=160)

    btn_paid = tk.Button(self,width=10,height=2,text='Paid'
                      ,bg='#0a6300',font=('lucida','12','bold'),fg='#d9d9d9',command=lambda :summary_page.paid(self.curr_data))

    btn_paid.place(x=500,y=20)
  def paid(df):
   # df.drop_duplicates(inplace=True)  
    df.drop(['item_name','item_price','start time display','end time display','time display'],axis=1,inplace=True)  
    to_db("transactions",df,exist="append")
    #to_csv(transaction_path,mode='a', index=False,header=False)        
    app.frames['summary_page'].stacker.show_frame('session_order_page')
    print(df)
  def transfrom_enter(df):
    # self arrtibute to be transferd to the init fucntion button btn_paid
    app.frames['summary_page'].curr_data= df
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
  #cur_dir=os.path.dirname(os.path.abspath(__file__))

  with open(f'{cur_dir}\config.json','r+') as json_file:
    config_data = json.load(json_file)
  # empty dataframe to delete
  empty = pd.DataFrame(list())  

  if config_data['today'] == dt.now().strftime('%Y-%m-%d'):
    table_counter= config_data['session_num']
    take_away_counter=config_data['tk_num']
    stock_counter=config_data['stock_num']
    book_counter=config_data['book_num']
    today=config_data['today']

 #   transaction_path=f"{cur_dir}\-transactions\-transactions({today}).csv"
    # test if the csv exists
    """try:
      tr=pd.read_csv(transaction_path)
    except:     
      empty.to_csv(transaction_path)"""         
  else: 
    # Change config file's date to today's date
    config_data['today']=dt.now().strftime('%Y-%m-%d')
    config_data['session_num'], config_data['tk_num'],config_data['stock_num']=0, 0 , 0
    truncate("sessions")
    # write the new change into the config.json file
    with open(f"{cur_dir}\config.json", "w") as outfile:
      json.dump(config_data,outfile,indent=4)
      
    table_counter= config_data['session_num']
    take_away_counter=config_data['tk_num']
    stock_counter=config_data['stock_num']
    book_counter=config_data['book_num']

    today=config_data['today']

   # transaction_path=f"{cur_dir}\-transactions\-transactions({today}).csv"
    # test if the csv exists
    """try:
      tr=pd.read_csv(transaction_path)
    except:     
      empty.to_csv(transaction_path)"""     
  """session_path=f"{cur_dir}\sessions.csv"
  services_path=f"{cur_dir}\services.csv"
  #create empty csv file to store the files
  #empty.to_csv(table_path)   
  try:
    tr=pd.read_csv(session_path)
  except:     
    empty.to_csv(session_path)   
  try:
    tr=pd.read_csv(services_path)
  except:     
    empty.to_csv(services_path) """  
  
  #information     
  print(f"{config_data['today']}: {config_data['session_num']} sessions")

  #driver
  app = main_app()
  open_sessions()

  app.mainloop()
