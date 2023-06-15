import tkinter as tk
from tkinter import ttk
from pages.TakeawayPage import *
from tkcalendar import Calendar
import datetime as dt
from pages.utils.db_open import run
from pages.utils.db_open import load_json

class AnalysisPage(tk.Frame):
  """
  This page handels the analysis of our database and report making.
  """
  def __init__(self, parent, stacker,bg=None,fg=None):
    tk.Frame.__init__(self, parent,bg=bg,fg=fg)
    self.stacker = stacker     
    self.queries = load_json("queries")

    # Calenders
    self.from_cal = Calendar(self, selectmode = 'day', date_pattern= "y-mm-dd",
               year = dt.date.today().year, month = dt.date.today().month,
               day = dt.date.today().day)
    
    self.to_cal = Calendar(self, selectmode = 'day',date_pattern= "y-mm-dd",
               year = dt.date.today().year, month = dt.date.today().month,
               day = dt.date.today().day)
    

    # Frames
    self.report_f = tk.Frame(self,bg ="white",width=400,height=250)
    self.moreinfo_f = tk.Frame(self,bg ="white",width=400,height=250)

    # List box with scroll bar
    self.moreinfo_tv = ttk.Treeview(self.moreinfo_f ,height=12,show= 'headings',selectmode='browse')
    self.moreinfo_sb = tk.Scrollbar(self.moreinfo_f)

    # labels
    self.from_cal_l = tk.Label(self,text='From/من',height=1,justify='center',relief='flat' ,font=('Helvetica',18,'bold'),fg='black',bg='light grey')
    self.to_cal_l = tk.Label(self,text='To/إلى',height=1,justify='center',relief='flat' ,font=('Helvetica',18,'bold'),fg='black',bg='light grey')
    self.report_info_l = tk.Label(self.report_f,text='Report/جرد',height=1,justify='center',relief='flat' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.count_l = tk.Label(self.report_f,text='Count/عدد',height=1,justify='center',relief='flat' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.total_l =tk.Label(self.report_f,text='Total/اجمالى',height=1,justify='center',relief='flat' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')

    self.count_instore_l =tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.count_takeaway_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.count_library_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.count_profit_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')

    self.total_instore_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.total_takeaway_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.total_library_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    self.total_profit_l=tk.Label(self.report_f,text='',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')
    
    self.profit_b =tk.Label(self.report_f,text='Profit/مكسب',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey')

    # buttons
    self.instore_b = tk.Button(self.report_f,text='Instore/بالداخل',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey',
                               command=lambda self=self : AnalysisPage.get_more_info(self,"Instore"))
    
    self.takeaway_b = tk.Button(self.report_f,text='TakeAway/بالخارج',height=1,justify='center' ,font=('Helvetica',12,'bold'),fg='black',bg='light grey',
                                command=lambda self=self : AnalysisPage.get_more_info(self,"TakeAway"))
    
    self.print_b = tk.Button(self.report_f,text='Library/مكتبة',height=1,justify='center',font=('Helvetica',12,'bold'),fg='black',bg='light grey',
                                command=lambda self=self : AnalysisPage.get_more_info(self,"Print"))
    
    self.refresh_b =tk.Button(self,text='Refresh\nإعادة الحساب',height=2,justify='center' ,font=('Helvetica',18,'bold'),fg='green',bg='light grey',
                              command=lambda self=self : AnalysisPage.plot_report(self))

    # Vars
    
    self.report_vars = {"counts":{self.count_instore_l:self.queries['count_instore'],
                                  self.count_takeaway_l:self.queries['count_takeaway'] , 
                                  self.count_library_l:self.queries['count_library'],
                                  self.count_profit_l:self.queries['count_profit']},
                        "totals":{self.total_instore_l:self.queries['total_instore'],
                                  self.total_takeaway_l:self.queries['total_takeaway'],
                                  self.total_library_l:self.queries['total_library']}
                        }        
    
    # Bindings
    self.moreinfo_tv.config(yscrollcommand =  self.moreinfo_sb.set)
    self.moreinfo_sb.config(command = self.moreinfo_tv.yview)

    # Placements
    self.from_cal.place(x=10,y=60)
    self.to_cal.place(x=290,y=60)
    self.from_cal_l.place(x=10,y=20)
    self.to_cal_l.place(x=290,y=20)
    self.report_f.place(x=850,y=10)
    self.report_info_l.place(x=10,y=10)
    self.count_l.place(x=190, y=10)
    self.total_l.place(x=300, y=10)
    self.instore_b.place(x=10,y=60)
    self.takeaway_b.place(x=10,y=110)
    self.print_b.place(x=10,y=160)
    self.profit_b.place(x=10,y=210)
    self.count_instore_l.place(x=190,y=60)
    self.count_takeaway_l.place(x=190,y=110)
    self.count_library_l.place(x=190,y=160)
    self.count_profit_l.place(x=190,y=210) 
    self.total_instore_l.place(x=300,y=60)
    self.total_takeaway_l.place(x=300,y=110) 
    self.total_library_l.place(x=300,y=160) 
    self.total_profit_l.place(x=300,y=210) 
    self.refresh_b.place(x=670,y=100)
    self.moreinfo_f.place(x= 10, y= 280)
    self.moreinfo_tv.pack(side="left",fill="both")
    self.moreinfo_sb.pack(side="right",fill="both")


    self.plot_report()

  def get_more_info(self,type):

    self.plot_report()

    command = self.queries[type].replace("[TO]",self.to_cal.get_date()).replace("[FROM]",self.from_cal.get_date())

    print("More info Command: \n",command,"\n\n")

    df = run(command)
    
    for item in self.moreinfo_tv.get_children():
      self.moreinfo_tv.delete(item)

    if(df.empty):
      return
    
    self.moreinfo_tv['columns'] = list(df.columns)

    for i in self.moreinfo_tv['columns']:
      self.moreinfo_tv.heading(i, text =i)

    df = df.astype(str)
    for row in df.values:
      self.moreinfo_tv.insert("", 'end',
             values =list(row))
 
 
  def plot_report(self):

    total_profit = 0

    for i in self.report_vars["counts"]:
      command = self.report_vars["counts"][i].replace("[TO]",self.to_cal.get_date()).replace("[FROM]",self.from_cal.get_date())
      i.config(text=run(command).iloc[0][0])
      print("Count Command: \n",command,"\n\n")


    for i in self.report_vars["totals"]:
      command = self.report_vars["totals"][i].replace("[TO]",self.to_cal.get_date()).replace("[FROM]",self.from_cal.get_date())
      result = run(command).iloc[0][0]

      total_profit += result
      i.config(text=result)
      print("Total Command: \n",command,"\n\n")


    
    self.total_profit_l.config(text= total_profit)
