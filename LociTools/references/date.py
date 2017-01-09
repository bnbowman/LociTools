
import calendar

def month_to_int( month ):
    months = {m.lower(): idx for idx, m in enumerate(calendar.month_name)}
    try:
        return months[month.lower()]
    except:
        return -1

def parse_date_str( date_str ):
    parts = date_str.strip().split()
    year  = int(parts[0])
    month = month_to_int( parts[1] )
    day   = int(parts[2])

    # Return the date as a numeric tuple for easy ordering
    return (year, month, day)
