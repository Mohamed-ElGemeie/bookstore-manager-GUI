

if __name__ != "__main__":


    def validate_int(num, error_window, message):

        if num:
            try:
                num = int(num)
                return num
            except:
                error_window.config(text=message)
        else:
            error_window.config(text="The number field is empty/خانة الرقم فارغ")

        return None
    
    def validate_string(string, error_window, message):

        if string:
            if(not string.isdigit()):
                return string
            
            else:
                error_window.config(text=message)

        else:
            error_window.config(text="The text field is empty/خانة الحروف فارغ")

        return None
    
    def validate_look_up(string, error_window, message, col):

        if col.str.contains(string):
            return True
        
        else:
            error_window.config(text = message)
    
        return None