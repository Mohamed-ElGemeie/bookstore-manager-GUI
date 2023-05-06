import tkinter as tk
from time import sleep
from pages.utils.db_open import df_menu
from pages.utils.validate import validate_string, validate_look_up

class TakeawayPage(tk.Frame):
  """
  This page handles the session's user interface, it is responsible for 
  session's cart items. This page's structure doesn't change, only some fields are 
  changed when a new session is entered on this page that might have a differnet 
  cart or name.
  """

  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker     


    def listbox_update(item):
      """
      Function that updates the listbox with the passed argument items
      without any manipulation.
      parameters
        item: list object that contains the items to be filled
      """

      self.entries_boxllist.delete(0,tk.END)

      for i in item:
        self.entries_boxllist.insert(tk.END,i)

    # def dble_clk_del(e):
    #   """
    #   Event function that delets an item row from the list box cart when double clicked on
    #   by the user.
    #   """

    #   if self.cart_boxlist.curselection():
    #     self.cart_boxlist.delete(self.cart_boxlist.curselection()) 

    #   else:
    #     sleep(0.3)

    # def tab_handler(e):
    #   """
    #   Event function run on pressing tab while selecting the entry box,
    #   this function selects the first item that appears on the list box
    #   and assign that to the user's entry box
    #   """
            
    #   if order_items.get() and entries_boxllist.size():

    #     # clear selection, delete the user's entry box
    #     entries_boxllist.selection_clear(0, 'end')
    #     order_items.delete(0,tk.END)        

    #     # select the first index of menu list box and append it to the user's entry box
    #     entries_boxllist.select_set(0)                      
    #     order_items.insert(0,entries_boxllist.get(entries_boxllist.curselection()))

    #   order_items.focus()  

    def add_item():
        """
        This function adds items to the cart listbox specified by the user,
        also handels repeated item entries and incorrect user inputs
        """

        item_count = int(self.order_amount_var.get())

        item = validate_string(self.order_items.get(),
                             self.error_visor,
                             "Please select an order/الرجاء اختيار طلب")

        in_menu = validate_look_up(item,
                                    self.error_visor,
                                    "Incorrect order, Pick from the list/اختيار غير صحيح ، اختر من القائمة")


        if item and in_menu:

            x=df_menu[df_menu['name']==item].reset_index(drop = True).price_ta
            # add_var: is used to decide if the item already exists in the list box 
            # or not, this ensures that repeated items share the same row
            add_var=False  
            # loop over the cart box list
            for i in range(self.cart_boxlist.size()):
                print(self.cart_boxlist.get(i))
            self.order_items.focus()
      
    def fillout(e):
      
      """
      Event function that is run when the user selects an item from the list box,
      this function auto completes the user input.
      * user clicks an item from the list box , which runs this function.
      * the selected item then is auto filled into the user entry box.
      """

      self.order_items.delete(0,tk.END)

      # add selected item to user's entry box     
      if self.entries_boxllist.get(self.entries_boxllist.curselection()):
        self.order_items.insert(0,self.entries_boxllist.get(self.entries_boxllist.curselection()))   

    def check(e):
        
        """
        Event function that takes all the item in the dataframe
        that contain a substring of the user's input, then it auto fills
        those item only to the list box.
        * makes it easier for the user to find thier item easily
        * uses python's 'in' operator
        """

        user_input = self.order_items.get().lower()
        displayed_data=[]

        # assign the whole dataframe if the user's input is empty
        if user_input:
            for i in df_menu['name'].tolist():
                if user_input in i.lower():
                    displayed_data.append(i)
        
        else:
            displayed_data=df_menu['name'].tolist()

        # display the list of similar items onto the menu list box
        listbox_update(displayed_data)
        self.entries_boxllist.select_set(0)

    def finalize(df):

        """
        This function is run after the confirm function check out the cart.
        This handels other transaction columns, and calls the summary_page
        to prompt the user with the recipt.
        parameters:
        df: pandas dataframe that holds transaction information
        """
        print(df)
    
    # vars
    self.amount=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]

    # top label
    self.item_label = tk.Label(self,height = 1, width = 10 ,text=('Orders'),font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.item_label.place(x=15,y=110)

    # user entry box
    self.order_items=tk.Entry(self,width=20,font=("Times",20))
    self.order_items.place(x=15,y=150)

    # count of item option box + vars
    self.order_amount_var=tk.StringVar()
    self.order_amount_var.set(1)
    self.order_amount_menu = tk.OptionMenu(self, self.order_amount_var, *self.amount)
    self.order_amount_menu.place(x=300,y=153)  

    # user's cart list box
    self.entries_boxllist=tk.Listbox(self,width=30,font=(16),exportselection=False,selectmode='MULTIPLE')
    self.entries_boxllist.place(x=15,y=200)    

    # fill the menu with the menu dataframe
    listbox_update(df_menu['name'].tolist())

    # bindings        
    self.entries_boxllist.bind('<<ListboxSelect>>',fillout)
    self.order_items.bind("<KeyRelease>",check)

    # insert item from menu to cart button
    self.btn_insert_item=tk.Button(self,width=10,text=('Add'),font=('Helvetica',16,'bold'),bg='#bfbfbf',command=add_item)
    self.btn_insert_item.place(x=380,y=148)

    # user's cart list box + bindings
    self.cart_boxlist=tk.Listbox(self,height=12,width=66,font=(18),exportselection=True,selectmode='SINGLE')
    self.cart_boxlist.place(x=380,y=200)
    
    # delete all items from cart button
    self.delete_cart_btn=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='#bfbfbf', command=self.cart_boxlist.delete(0,'end'))
    self.delete_cart_btn.place(x=570,y=147)    



    # Confirm button that checks out the order
    # confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='#bfbfbf',command=lambda: Confirm(self=self,
    #                 tk_or_sess=True,stay_name=self.session_name.cget('text')
    #                 ,func = orders_page.finalize))
    # confirm_button.place(x=380,y=500)
    # error window label for incorrect user input
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.error_visor.place(x=350,y=50)

    # session name label
    self.session_name=tk.Label(self,height = 1, width = 20 ,text='',font=('Helvetica',20,'bold'),bg='#bfbfbf')
    self.session_name.place(x=400,y=10)        


    # session_boxlist=app.frames['session_order_page'].session_boxlist
    # index=session_boxlist.curselection()[0]
    # sess_name=session_boxlist.get(index)  
    # # no_order is used to add an extra 5 pound charge
    # # for cutomers who didn't order
    # no_order=df['order_total'].sum()==0
    # # get the wifi/time related transaction columns
    # transaction_time=sessions.calculate_nps(session_dict[sess_name])
    # df['start_time']=transaction_time['start_time']
    # df['end_time']=transaction_time['end_time']
    # df['time']=transaction_time['time']
    # df['start time display']=transaction_time['start time display']
    # df['end time display']=transaction_time['end time display']
    # df['time display']=transaction_time['time display']
    # df['wifi']=transaction_time['wifi']
    # if(no_order):
    #   df['wifi']+=5
    # df['paid_total'] = df['order_total'][0]+df['wifi'][0]
    # # display the recipt
    # summary_page.transfrom_enter(df)      
    # app.frames['orders_page'].stacker.show_frame('summary_page')       
    # # deletion sequence of the session
    # app.frames['orders_page'].cart_boxlist.delete(0,'end')
    # session_boxlist.delete(index)      
    # del session_dict[sess_name]
    # app.frames['orders_page'].table.set(1)   
    # # update session table from database
    # session_update()       