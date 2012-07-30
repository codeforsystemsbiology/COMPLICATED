#! /usr/bin/python

"""
Congrats, on c-dev branch
Suggested reading (or thinking).

Large Files
http://stackoverflow.com/questions/728118/python-downloading-a-large-file-to-a-local-path-and-setting-custom-http-headers?rq=1 

Being able to restart read or write without starting over.
http://stackoverflow.com/questions/5064879/how-to-download-large-file-with-binary-mode-in-python


Suggested don't worry about.  
Internal data organization, 
What the written file looks like.  Act like it is a long string of bytes.

"""


class Data:
    """
    A base class for CoMPLICATD data objects
    """
    Addama = 1
    S3 = 2
    Local = 3
 
    #should be able to pass the data URI or the synid or both.
    def __init__(self, synid=None, data_uri=None):
        if synid == None and data_uri == None:
		self.synid = synid
		self.data_uri = data_uri
	elif data_uri == None and synid.startswith("syn") and not synid.count("."):
		self.synid = synid
		self.data_uri = None
	elif data_uri == None:
		self.data_uri = synid
		self.data_uri = self.data_uri.strip()
		self.data_uri = self.data_uri.replace(" ", "%20")
		self.synid = None
	else:
		self.synid = synid
		self.data_uri = data_uri
		self.data_uri = self.data_uri.strip()
		self.data_uri = self.data_uri.replace(" ", "%20")
	

    def write(self, data_pref):
	pass

    def _writeToAddama(self, addama_dir):
        """
        Take the current data obj, 
        """
        
    def _discoverLocation(self, uri):
        """
        From the uri, returns where the data is stored as class variable
        Data.Addama
        Data.S3
        Data.Local
        """

    def getData(self, local_cache):
        """
        Retrieves data from data_uri and stores it in the local cache.
        """
        

    def _toFile(self):
        """
        returns a file type object that can be stored.

        i.e. don't worry about this.  Will be overrridden
        """
        pass

    def _fromFile(self,filepath, filename):
        """
        Given a local path and filename, returns useable data object
        """
        pass

class CommHandler:
    """
    Base class for handling communications with external data stores.
    """
    def __init__(self):
        pass

    def writeFile(self, myfile, uri):
        raise Exception("CommHandler is an abstract base class.")

    def readFile(self, uri):
        raise Exception("CommHandler is an abstract base class.")

class AddamaHandler(CommHandler):
    def __init__(self, apicrap):
        """
        Read auth settings from file
        """
        pass


    def _handleAuth(self):
        pass

class S3Handler(CommHandler):
        
    def __init__(self, apicrap):
        """
        Read auth settings from file
        """
        pass


    def _handleAuth(self):
        pass



