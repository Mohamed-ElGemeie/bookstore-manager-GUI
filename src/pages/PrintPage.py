import tkinter as tk
from datetime import datetime as dt
from pages.utils.db_open import to_db
from pages.utils.validate import validate_int, validate_string
from pandas import DataFrame

class PrintPage(tk.Frame):
  
  """
  This class writes transactions of the books and printed paper into
  the books table from db.
  * recive user input of book name, book price, printed paper amount
  * write the transaction details into the books table from db
  """

  def __init__(self,parent,stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker

    def buy_paper():
      
      """
      Function that handels the printed paper amount transaction.
      * checks for any user errors
      * calculates the price of the amount 
      * stores the transaction into the books table
      """

      # retrive paper amount from entry box
      paper = validate_int(paper_amount_e.get(),
                           self.error_visor,
                           "The paper amount has to be a number/عدد الورق يجب ان يكن رقم")
      
      if paper != None:      

        # create paper transaction row
        temp_df= DataFrame({'name': ["paper"],
                            'price': [paper*0.75],
                            'start_time': dt.now()})

        to_db("print",temp_df,exist="append")

        paper_amount_e.delete(0,tk.END)
        self.error_visor.config(text='تم التسجبل')


    def buy_book():
      """
       Function that handels the sold book transactions.
      * checks for any user errors 
      * stores the transaction into the books table
      """

      
      name = validate_string(book_name_e.get(),
                             self.error_visor,
                             "The name has to have letter/الاسم يجب ان يكن متكون من حروف")
      
      price = validate_int(book_price_e.get(),
                           self.error_visor,
                           "The price has to be a number/السعر يجب ان يكن رقم")
      
      
      if name and price:

        temp_df= DataFrame({'name': [name],
                            'price': [price],
                            'start_time': dt.now()})


        to_db("print",temp_df,exist="append")

        book_name_e.delete(0,tk.END)
        book_price_e.delete(0,tk.END)

        self.error_visor.config(text='تم التسجبل')


    #vars
    self.book_name=tk.StringVar()
    self.book_price=tk.StringVar()
    self.paper_amount=tk.StringVar()

    #entry
    book_name_e=tk.Entry(self,textvariable=self.book_name,font=("Helvetica",20),width=30)
    book_price_e=tk.Entry(self,textvariable=self.book_price,font=("Helvetica",20),width=30)
    paper_amount_e=tk.Entry(self,textvariable=self.paper_amount,font=("Helvetica",20),width=30)

    #buttons
    buy_b=tk.Button(self,font=('Helvetica',20,'bold'),text=('Confirm'),command=lambda:buy_book())
    print_b=tk.Button(self,font=('Helvetica',20,'bold'),text=('Confirm'),command=lambda:buy_paper())
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