import tkinter as tk
from pages.TakeawayPage import *
from PIL import ImageTk, Image
from .utils.settings import load_json, update_json
from datetime import datetime as dt, timedelta
from threading import Thread


class SessionPage(TakeawayPage,tk.Frame):
  """
  This page handels the quick take-away order, and the creation of sessions
  from the session class.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    super().__init__(stacker=stacker,parent= parent,bg=bg,fg=fg)
    self.stacker = stacker

    print(self.menu_f)
    self.tables_b = {}   
    self.tables = load_json('table_carts')
    self.table_times = load_json('table_times')
    self.selected_table = '-1'

    self.tables_pos = [(310,20),(310,70),(310,120),(310,170),(180,20),
                       (180,70),(180,120),(100,110),(100,160),(310,320),
                       (310,370),(310,420),(310,460),(180,305),(180,345),
                       (180,385),(180,425),(180,465),(100,345),(100,425)]
    # images
    self.map = ImageTk.PhotoImage(Image.open("src\\assets\\table_map.png").resize((367,510)))

    # Threads
    self.timer_thread = Thread(target=self.get_time_passed,args=())
    
    # labels
    self.map_l = tk.Label(self,image=self.map)
    self.wifi_l = tk.Label(self,text='0',font=('Helvetica',24,'bold'),bg='#bfbfbf') 
    self.time_passed_l = tk.Label(self,text='',font=('Helvetica',24,'bold'),bg='#bfbfbf') 
    self.wifi_change_l = tk.Label(self,text='0',font=('Helvetica',24,'bold'),bg='#bfbfbf') 
    self.wifi_change_info_l = tk.Label(self,text='Wifi change/تغير الواى فاى',font=('Helvetica',12,'bold'),bg='#bfbfbf')
    self.wifi_info_l = tk.Label(self,text='Wifi',font=('Helvetica',16,'bold'),bg='#bfbfbf')
    self.total_info_l = tk.Label(self,text='Total',font=('Helvetica',16,'bold'),bg='#bfbfbf')

    # buttons
    self.delete_cart_b.config(command= lambda self=self: SessionPage.delete_all(self))
    self.confirm_cart_b.config(command= lambda self=self: SessionPage.buy(self))

    self.raise_wifi_b = tk.Button(self,text='<',font=('Helvetica',16,'bold'),fg='black',bg='#bfbfbf'
                                 , command= lambda self=self: SessionPage.increment_wifi(self,-1))
    self.lower_wifi_b = tk.Button(self,text='>',font=('Helvetica',16,'bold'),fg='black',bg='#bfbfbf'
                                 , command= lambda self=self: SessionPage.increment_wifi(self,1))
    
    self.start_time_b = tk.Button(self,text='Start Time/ابدأ الوقت',font=('Helvetica',16,'bold'),fg='green',bg='#bfbfbf'
                                 , command= lambda self=self: SessionPage.start_time(self))
    
    self.reset_time_b = tk.Button(self,text='reset Time/إعادة الوقت',font=('Helvetica',10,'bold'),fg='red',bg='#bfbfbf'
                                 , command= lambda self=self: SessionPage.delete_time(self))
  
    
    for i in range(20):
        self.tables_b[i] = tk.Button(self.map_l,command=lambda self=self, table_num = str(i): SessionPage.select_table(self,table_num)
                                   ,width=3 ,text=(f'{i}'),font=('Helvetica',12,'bold'),fg="black")
        self.tables_b[i].place(x = self.tables_pos[i][0], y= self.tables_pos[i][1])

    # bindings        
    self.menu_lb.bind('<<ListboxSelect>>',lambda x, self =self: SessionPage.fillout(self))
    self.user_order_e.bind("<KeyRelease>",lambda x, self =self: SessionPage.find_match(self))
    self.menu_lb.bind('<Double-Button-1>',lambda x, self =self: SessionPage.add_item(self))
    self.cart_lb.bind('<Double-Button-1>',lambda x, self=self: SessionPage.remove_item(self))    

    # placements
    self.menu_l.place(x=15,y=20)
    self.user_order_e.place(x=15,y=60)
    self.menu_f.place(x=15,y=110)    
    self.cart_f.place(x=370,y=110)
    self.delete_cart_b.place(x=380,y=60)    
    self.error_visor.place(x=250,y=10)
    self.confirm_cart_b.place(x=580,y=60)
    self.map_l.place(x=730,y=110)
    self.start_time_b.place(x=750,y=60)
    self.reset_time_b.place(x=750,y=20)
    self.total_l.place(x=1120, y =280)
    self.total_info_l.place(x=1120, y=250)
    self.time_passed_l.place(x=970, y=60)
    self.wifi_l.place(x=1120,y=180)
    self.wifi_info_l.place(x=1120,y=150)
    self.raise_wifi_b.place(x=1120, y=400)
    self.lower_wifi_b.place(x=1160, y=400)
    self.wifi_change_l.place(x=1140, y=450)
    self.wifi_change_info_l.place(x=1100, y=500)

    SessionPage.refresh_table_colors(self)
    self.timer_thread.start()


  def increment_wifi(self, incremnet):
    self.wifi_change_l.config(text= int(self.wifi_change_l.cget('text')) + (5*incremnet))

  def get_time_passed(self):

    while True:
      sleep(0.25)
      if int(self.selected_table) == -1:
        self.time_passed_l.config(text='0:00:00')
        self.wifi_l.config(text=0)

      elif(not self.table_times.get(self.selected_table)):
        self.time_passed_l.config(text='0:00:00')
        self.wifi_l.config(text=0)

      else: 
        time_passed = dt.now() - dt.strptime(self.table_times[self.selected_table],'%Y-%m-%d %H:%M:%S.%f')
        time_passed_display = time_passed - timedelta(microseconds=time_passed.microseconds)


        hours = time_passed.total_seconds()/3600
        wifi = 0

        if hours >= 5:
          wifi = 25
        elif hours > 0 and hours < 5:
          wifi = (int(hours) * 5) + 5

        self.wifi_l.config(text=wifi)
        self.time_passed_l.config(text= str(time_passed_display))
     
  def delete_time(self):
    if self.selected_table == '-1':
      self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")
      return False
    
    self.table_times[self.selected_table] = {}

    self.wifi_change_l.config(text='0')

    update_json(self.table_times,'table_times')


  def start_time(self):
    if self.selected_table == '-1':
      self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")
      return False
    
    self.table_times[self.selected_table] = str(dt.now())
    
    self.wifi_change_l.config(text='0')

    update_json(self.table_times,'table_times')

  def update_cart_json(self):
     
     if self.selected_table == '-1':
        self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")

        return False
     
     self.tables[self.selected_table] = self.cart

     update_json(self.tables,'table_carts')

     return True
     
  def refresh_table_colors(self):

    self.tables = load_json('table_carts')

    for i in self.tables_b:
      self.tables_b[i].config(fg="black",bg = "white")

      if(len(self.tables.get(str(i))) != 0):
        
        self.tables_b[i].config(fg="black",bg = "green")

      if(len(self.table_times.get(str(i)))):
        self.tables_b[i].config(fg='orange')


      

  def select_table(self,table_num):
    
    SessionPage.refresh_table_colors(self)
    self.wifi_change_l.config(text='0')
    
    self.tables_b[int(table_num)].config(fg = "green",bg = "red")

    if(self.tables.get(table_num)):
       self.cart = self.tables[table_num]

    else:
       self.cart = {}

   
    self.selected_table = table_num
    
    SessionPage.fill_cart(self)

  def add_item(self):
      """
      This function adds items to the cart listbox specified by the user,
      also handels repeated item entries and incorrect user inputs
      """
      if self.selected_table == '-1':
         self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")

         return
      
      
      super().add_item()

      SessionPage.update_cart_json(self)

  def remove_item(self):
    if self.selected_table == '-1':
        self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")

        return False
    

    if(not self.cart_lb.size()):
      return False
    
    if super().remove_item():

      SessionPage.update_cart_json(self)

    return True




  def fill_cart(self):
    self.cart_lb.delete(0,tk.END)
    for i in self.cart.keys():
      self.cart_lb.insert(tk.END,f"{i} * {self.cart[i]['amount']} = {self.cart[i]['total']}")

    SessionPage.display_total(self)

    self.user_order_e.focus()


  def delete_all(self):
    if self.selected_table == '-1':
        self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")

        return False
    
    if super().delete_all():

      SessionPage.update_cart_json(self)
    
    return True




  def buy(self):

      """
      This function is run after the confirm function check out the cart.
      This handels other transaction columns, and calls the summary_page
      to prompt the user with the recipt.
      parameters:
      df: pandas dataframe that holds transaction information
      """
      if self.selected_table == '-1':
        self.error_visor.config(text="Please Select one of the tables/الرجاء اختيار طاولة")

        return False  
      
      wifi = int(self.wifi_change_l.cget('text')) + int(self.wifi_l.cget('text'))

      self.cart['wifi'] = {"price": int(self.wifi_l.cget('text')),
            "amount": f"{int(self.wifi_change_l.cget('text'))} زيادة ",
            "total": wifi,
            "id": -1}

      new_id = super().buy(tran_type= "Instore") 
      
      if new_id == -1:
        return False
      
      df_dict = {'tran_id':[new_id], 'table_num': [self.selected_table],
                   'end_time':[dt.now()],'wifi':[wifi]}
      df = DataFrame(df_dict)


      print(df)
      
      to_db('instore', df, 'append')
      SessionPage.update_cart_json(self)
      self.wifi_change_l.config(text='0')

      self.table_times[self.selected_table] = {}
      update_json(self.table_times, 'table_times')

      return True



