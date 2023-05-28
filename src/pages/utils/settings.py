import json

def update_json(data,name):
  with open(paths[name], "w") as outfile:
    print(data)
    json.dump(data,outfile,indent=4,default=str)

def load_json(name):

  with open(paths[name],'r+') as json_file:

    return json.load(json_file)
  
    
if __name__ != "__main__":
   paths = {'config': "src\config\config.json",
            'table_carts':"src\config\\tables.json",
            'table_times':"src\config\\table_times.json",
            'database_config':"src\config\db_config.json"}
