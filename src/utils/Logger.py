

"""
Logger for Debugging purposes
"""

Debug = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    INFO = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def Info(text):
    """
    Sends Color in green for informational purposes
    :param text: the text that needs to be colored
    :return:
    """
    if Debug == True:
        return print(bcolors.INFO + text + bcolors.END)

def Print_Values(value):
    """
    Print values for debugging purposes and leave a space after
    :param value: value to write
    :return:
    """
    if Debug == True:
        print(value)
        print("")
        return

def Print_Values_no_Space(value):
    """
    Print values for debugging purposes without a space after (usually for loops etc.)
    :param value: value to be written
    :return:
    """
    if Debug == True:
        print(value)
        return

def Warning(text):
    """
    Send Color in yellow for Warning purposes (optional properties not correctly set)
    :param text: text to be written
    :return:
    """
    if Debug == True:
        return print(bcolors.WARNING + text + bcolors.END)

def Fail(text):
    """
    Sends Color in red for Failing purposes (usually for exceptions debugging before writing the exception)
    :param text: text to be written
    :return:
    """
    if Debug == True:
        return print(bcolors.FAIL + text + bcolors.END)
