import tkinter as tk
from time import sleep
from pages.utils.db_open import df_menu, create_transaction_id , to_db
from pages.utils.validate import validate_string, validate_look_up
from pandas import DataFrame
from tkinter.messagebox import showinfo

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
    # vars
    self.cart = {}

    # entry
    self.user_order_e=tk.Entry(self,width=20,font=("Times",20))
    
    # list boxes
    self.menu_lb=tk.Listbox(self,height=20,width=30,font=(20),exportselection=False,selectmode='MULTIPLE')
    self.cart_lb=tk.Listbox(self,height=20,width=30,font=(20),exportselection=False,selectmode='MULTIPLE')

    # buttons
    self.delete_cart_b=tk.Button(self,width=10,text='Delete',font=('Helvetica',16,'bold'),fg='red',bg='#bfbfbf'
                                 , command= lambda self=self: TakeawayPage.delete_all(self))
    self.confirm_cart_b= tk.Button(self,height=1,width=10,text='Confirm',font=('Helvetica',16,'bold'),fg='blue',bg='#bfbfbf'
                                 , command= lambda self=self: TakeawayPage.buy(self = self,tran_type= "TakeAway"))
    # labels
    self.menu_l = tk.Label(self,height = 1, width = 10 ,text=('Menu'),font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.error_visor=tk.Label(self,height = 1, width = 35 ,text='',font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.total_l = tk.Label(self,text='0',font=('Helvetica',24,'bold'),bg='#bfbfbf') 

    # placements
    self.menu_l.place(x=15,y=20)
    self.user_order_e.place(x=15,y=60)
    self.menu_lb.place(x=15,y=110)    
    self.cart_lb.place(x=550,y=110)
    self.delete_cart_b.place(x=380,y=60)    
    self.error_visor.place(x=350,y=10)
    self.confirm_cart_b.place(x=580,y=60)
    self.total_l.place(x=1090,y=60)

    # bindings        
    self.menu_lb.bind('<<ListboxSelect>>',lambda x, self =self: TakeawayPage.fillout(self))
    self.user_order_e.bind("<KeyRelease>",lambda x, self =self: TakeawayPage.find_match(self))
    self.menu_lb.bind('<Double-Button-1>',lambda x, self =self: TakeawayPage.add_item(self))
    self.cart_lb.bind('<Double-Button-1>',lambda x, self=self: TakeawayPage.remove_item(self))
    
    # fill in the menu
    TakeawayPage.listbox_update(self,df_menu['name'].tolist())


  def display_total(self):
    total = 0

    for i in self.cart.values():
      total+= i['total']

    self.total_l.config(text=total)

  def listbox_update(self,item):
    """
    Function that updates the listbox with the passed argument items
    without any manipulation.
    parameters
      item: list object that contains the items to be filled
    """

    self.menu_lb.delete(0,tk.END)

    for i in item:
      self.menu_lb.insert(tk.END,i)


  def delete_all(self,*args):
    if(not self.cart_lb.size()):
      return False
    
    self.cart = {}
    self.cart_lb.delete(0,tk.END)

    TakeawayPage.display_total(self)
    return True

  def fill_cart(self):
    self.cart_lb.delete(0,tk.END)

    for i in self.cart.keys():
      self.cart_lb.insert(tk.END,f"{i} * {self.cart[i]['amount']} = {self.cart[i]['total']}")

    TakeawayPage.display_total(self)

    self.user_order_e.focus()

  def remove_item(self,*args):

    idx = self.cart_lb.curselection()

    if(not self.cart_lb.size()):
       return False
    
    elif(not idx):
      idx = self.last_selected_idx
    
    else:
      self.last_selected_idx = idx


    idx = self.cart_lb.get(idx[0]).split('*')[0].strip()

    if(not idx):
        return False
    
    if(self.cart[idx]["amount"] <= 1):
      del self.cart[idx]
    else:
      self.cart[idx]["amount"] -=1
      self.cart[idx]["total"] -= self.cart[idx]["price"] 

    TakeawayPage.fill_cart(self)
    return True

  def fillout(self):
    
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


  def add_item(self, *args):
      """
      This function adds items to the cart listbox specified by the user,
      also handels repeated item entries and incorrect user inputs
      """

      item_name = self.user_order_e.get()
      item_price = int(df_menu[df_menu['name']== item_name].reset_index(drop = True).price_ta)
      item_id = int(df_menu[df_menu['name'] == item_name].reset_index(drop=True).id)

      if(self.cart.get(item_name ,False)):
        self.cart[self.user_order_e.get()]["amount"] += 1
        self.cart[self.user_order_e.get()]["total"] += item_price

      else:
        self.cart[self.user_order_e.get()] = {"price": item_price, "amount" : 1, "total":item_price, "id":item_id}
        
    
      TakeawayPage.fill_cart(self)

  def find_match(self):
      
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
      TakeawayPage.listbox_update(self,displayed_data)
      self.menu_lb.select_set(0)

  def recipt(self):
    
    pop_up = tk.Tk()

    msg = [['Name/اسم','Price/سعر','Amount/عدد','Total',self.total_l['text']]]
    
    for i in self.cart:
      msg.append([i , self.cart[i]['price'] , self.cart[i]['amount'] , self.cart[i]['total']])

    for i in range(len(self.cart)+1):
      for j in range(4):
                
        e = tk.Entry(pop_up, width=20, fg='black',
                              font=('Arial',16,'bold'))
                
        e.grid(row=i, column=j)
        e.insert(tk.END, msg[i][j])

    e = tk.Entry(pop_up, width=20, fg='red',
                          font=('Arial',16,'bold'))
            
    e.grid(row=0, column=4)
    e.insert(tk.END, msg[0][4])

  def buy(self,tran_type,*args):

      """
      This function is run after the confirm function check out the cart.
      This handels other transaction columns, and calls the summary_page
      to prompt the user with the recipt.
      parameters:
      df: pandas dataframe that holds transaction information
      """
      if not self.cart:
          self.error_visor.config(text="You haven't ordered anything!/لم تطلب شئ")
          return -1  
      
      TakeawayPage.recipt(self)


      new_id =create_transaction_id(tran_type)
      item_ids = []

      if(self.cart.get('wifi')):
         del self.cart['wifi']

      for i in self.cart.values():
          item_ids.append(i['id'])

      df_dict = { "item_id": item_ids}

      df = DataFrame(df_dict)
      df['tran_id'] = new_id

      to_db("order_group",df,"append")
      TakeawayPage.delete_all(self)

      return new_id
