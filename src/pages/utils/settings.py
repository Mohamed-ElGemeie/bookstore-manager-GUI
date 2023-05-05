import json

def update_config(data):
  """
  Function that update the config.json file with the config_data dictionary
  * if any changes were made to config_data, they will be saved externally to config.json
  """
  with open(config_path, "w") as outfile:

    json.dump(data,outfile,indent=4)

def load_config():

    with open(f'{config_path}','r+') as json_file:

        return json.load(json_file)
    
if __name__ != "__main__":
   
   config_path = 'src\config\config.json'
   config_data = load_config()
