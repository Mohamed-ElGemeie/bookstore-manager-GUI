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

      self.menu_lb.delete(0,tk.END)

      for i in item:
        self.menu_lb.insert(tk.END,i)

    def delete_all():
      self.cart = {}
      self.cart_lb.delete(0,tk.END)

    def fill_cart():
      self.cart_lb.delete(0,tk.END)

      for i in self.cart.keys():
        self.cart_lb.insert(tk.END,f"{i} * {self.cart[i]['amount']} = {self.cart[i]['total']}")


      self.user_order_e.focus()

    def remove_item(e):
      
      idx = self.cart_lb.curselection()[0]
      idx = self.cart_lb.get(idx).split('*')[0].strip()
      if(self.cart[idx]["amount"] <= 1):
        del self.cart[idx]
      else:
        self.cart[idx]["amount"] -=1
        self.cart[idx]["total"] -= self.cart[idx]["price"] 

      fill_cart()

    def add_item(e):
        """
        This function adds items to the cart listbox specified by the user,
        also handels repeated item entries and incorrect user inputs
        """

        item_name = self.user_order_e.get()
        item_price = int(df_menu[df_menu['name']== item_name].reset_index(drop = True).price_ta)

        if(self.cart.get(item_name ,False)):
          self.cart[self.user_order_e.get()]["amount"] += 1
          self.cart[self.user_order_e.get()]["total"] += item_price

        else:
          self.cart[self.user_order_e.get()] = {"price": item_price, "amount" : 1, "total":item_price}
           
      
        fill_cart()


    
    def fillout(e):
      
      """
      Event function that is run when the user selects an item from the list box,
      this function auto completes the user input.
      * user clicks an item from the list box , which runs this function.
      * the selected item then is auto filled into the user entry box.
      """

      self.user_order_e.delete(0,tk.END)

      # add selected item to user's entry box     
      if self.menu_lb.get(self.menu_lb.curselection()):
        self.user_order_e.insert(0,self.menu_lb.get(self.menu_lb.curselection()))   

    def find_match(e):
        
        """
        Event function that takes all the item in the dataframe
        that contain a substring of the user's input, then it auto fills
        those item only to the list box.
        * makes it easier for the user to find thier item easily
        * uses python's 'in' operator
        """

        user_input = self.user_order_e.get().lower()
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
        self.menu_lb.select_set(0)

    def buy():

        """
        This function is run after the confirm function check out the cart.
        This handels other transaction columns, and calls the summary_page
        to prompt the user with the recipt.
        parameters:
        df: pandas dataframe that holds transaction information
        """

        print(self.cart)
    

    # vars
    self.cart = {}

    # entry
    self.user_order_e=tk.Entry(self,width=20,font=("Times",20))
    
    # list boxes
    self.menu_lb=tk.Listbox(self,height=20,width=30,font=(20),exportselection=False,selectmode='MULTIPLE')
    self.cart_lb=tk.Listbox(self,height=20,width=30,font=(20),exportselection=False,selectmode='MULTIPLE')

    # buttons
    self.delete_cart_b=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='#bfbfbf'
                                 , command=delete_all)
    self.confirm_cart_b= tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='blue',bg='#bfbfbf'
                                 , command=buy)
    # labels
    self.menu_l = tk.Label(self,height = 1, width = 10 ,text=('Menu'),font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',16,'bold'),bg='#bfbfbf')


    # placements
    self.menu_l.place(x=15,y=20)
    self.user_order_e.place(x=15,y=60)
    self.menu_lb.place(x=15,y=110)    
    self.cart_lb.place(x=550,y=110)
    self.delete_cart_b.place(x=380,y=110)    
    self.error_visor.place(x=350,y=50)

    # bindings        
    self.menu_lb.bind('<<ListboxSelect>>',fillout)
    self.user_order_e.bind("<KeyRelease>",find_match)
    self.menu_lb.bind('<Double-Button-1>', add_item)
    self.cart_lb.bind('<Double-Button-1>', remove_item)

    # fill in the menu
    listbox_update(df_menu['name'].tolist())



    # Confirm button that checks out the order
    # confirm_button=tk.Button(self,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='dark blue',bg='#bfbfbf',command=lambda: Confirm(self=self,
    #                 tk_or_sess=True,stay_name=self.session_name.cget('text')
    #                 ,func = orders_page.finalize))
    # confirm_button.place(x=380,y=500)
    # error window label for incorrect user input

    # session name label


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