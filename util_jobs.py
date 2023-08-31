import datetime as dt

"""
Get current date time, formatted as a string
"""
def get_current_datetime():
    
    now = dt.datetime.now()
    return now.strftime("%m-%d-%Y @ %H:%M:%S")

"""
Get current date, formatted as a string
"""
def get_current_date():
    
    now = dt.datetime.now()
    return now.strftime("%m-%d-%Y")

if __name__ == "__main__":

    print("Current date and time: ", get_current_datetime() )
