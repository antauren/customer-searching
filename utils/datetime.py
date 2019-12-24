import datetime as dt


def get_the_beginning(date):
    return dt.datetime(year=date.year, month=date.month, day=date.day, hour=0)
