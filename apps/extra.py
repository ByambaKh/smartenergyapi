import datetime

def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])

def GetConvertedFileType(filetype):
    if filetype == "image/png":
        return 2
    elif filetype == "image/jpeg":
        return 2
    elif filetype == "application/pdf":
        return 1
    else:
        return 0

def get_years():
    year_array = []
    current_year = datetime.datetime.now().date().year
    for num in range(0,5):
        year_array.append(str(current_year - num))
    return year_array

def get_months():
    month_array = []
    for num in range(1,13):
        month_array.append(str(num))
    return month_array


def get_number_of_days(start_date, end_date):
    delta = start_date.date() - end_date
    b = int(delta.days)
    if b < 0:
        b = b * -1
    return b

def isEmpty(val):    
    if not val and val=='':
        return True
    return False