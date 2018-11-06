import logging
import logging.handlers
import os



root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "/home/mdiaz-isotrol/afcloud/afcloud.log"))

formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

fileHandler = logging.handlers.RotatingFileHandler('/home/mdiaz-isotrol/afcloud/afcloud.log', maxBytes=200000, backupCount=5)
fileHandler.setFormatter(formatter)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
        
        
handler.setFormatter(formatter)
root.addHandler(fileHandler)
root.addHandler(streamHandler)



def getLogger():

    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.addHandler(handler)

    return root


