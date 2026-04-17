from datetime import datetime, timedelta


# Collection of general function, which can be used everywhere.
# TODO: if necessary just make it more general
def add_time(time=str, days=0, minutes=0):
    """
    :param time: enter your time string and add one day to it
    :return:
    """
    time = datetime.strptime(time, '%m/%d/%Y %H:%M')
    time = time + timedelta(days=days) + timedelta(minutes=minutes)
    time = time.strftime('%m/%d/%Y %H:%M')
    return time

def protect(*protected):
    """Returns a metaclass that protects all attributes given as strings"""
    class Protect(type):
        has_base = False
        def __new__(meta, name, bases, attrs):
            if meta.has_base:
                for attribute in attrs:
                    if attribute in protected:
                        raise AttributeError('Overriding of attribute "%s" not allowed.'%attribute)
            meta.has_base = True
            klass = super().__new__(meta, name, bases, attrs)
            return klass
    return Protect