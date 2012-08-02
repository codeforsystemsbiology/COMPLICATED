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

import sys
import urllib
import httplib
import ConfigParser
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json

class Data:
    """
                header    A base class for CoMPLICATD data objects
    """
    Addama = 1
    S3 = 2
    Local = 3
 
    #should be able to pass the data URI or the synid or both.
    def __init__(self, synid=None, data_uri=None, data_loc=None, key=None):
	if data_loc not in [None,1,2,3]:
		try:
			data_loc = {'addama':1,'Addama':1,'S3':2,'s3':2,
                                    'Local':3, 'local':3}
		except:
			data_loc = None

        if synid == None and data_uri == None:
		self.synid = synid
		self.data_uri = data_uri
	elif data_uri == None and synid.startswith("syn") and not synid.count("."):
		self.synid = synid
		self.data_uri = None
	elif data_uri == None:
		self.data_uri = synid
		self.data_uri = urllib.quote(self.data_uri)
		self.synid = None
	else:
		self.synid = synid
		self.data_uri = data_uri
		self.data_uri = urllib.quote(self.data_uri)

	try:
		self.data_uri = self.data_uri.split('https%3A//')[-1]
		self.data_uri = self.data_uri.split('http%3A//')[-1]
	except:
		pass

	if data_loc == None:
		data_loc = self._discoverLocation()
	if data_loc == 1:
		self.Comm = AddamaHandler(key)
	elif data_loc == 2:
		self.Comm = S3Handler(key)
	else:
		# do local?
		self.Comm = None
		pass

    def write(self, data_pref):
	pass

    def _writeToAddama(self, addama_dir):
        """
        Take the current data obj, 
        """
	pass
        
    def _discoverLocation(self):
        """
        From the uri, returns where the data is stored as class variable
        Data.Addama
        Data.S3
        Data.Local
        """
	return None

    def getData(self, local_cache=''):
        """
        Retrieves data from data_uri and stores it in the local cache.
        """
	if self.Comm is not None and local_cache == '':
		return self.Comm.readFile(self.data_uri)
	elif self.Comm is None:
		return None
	else:
		output = self.Comm.readFile(self.data_uri)

	if local_cache == '.':
		fname = self.data_uri.split('/')[-1]	
	elif local_cache.count('.'):
		fname = local_cache
	elif local_cache.endswith('/'):
		fname = local_cache+self.data_uri.split('/')[-1]
	else:
		fname = local_cache+'/'+self.data_uri.split('/')[-1]
	
	f = open(fname, 'w')
	f.write(output)
	f.close()
	return output

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
    def __init__(self, keypath):
	self.keypath = keypath
	if not self._handleAuth():
		print 'Addama Auth failed- invalid apikey file:', keypath

    def _handleAuth(self):
	try:
		self.authFILE = ConfigParser.RawConfigParser()
		self.authFILE.read(self.keypath)
		self.Host = self.authFILE.get("Connection", "host")
		self.ApiKey = self.authFILE.get("Connection", "apikey")
	except:
		print "Addama Auth Error:", sys.exc_info()[0]
		self.authFILE = None
		self.Host = None
		self.ApiKey = None
		return False
	return True


    def readFile(self, uri):
	if self.Host == None:
		print "readFile Error: No Addama authorization present"
		return []
	
	try:
		headers = {"x-addama-apikey": self.ApiKey }
		params = urllib.urlencode({})
		conn = httplib.HTTPSConnection(self.Host)
		uri = uri.lstrip(self.Host)
		conn.request("GET", uri, params, headers)
	except:
		print("Addama readFile Connection/Request Error:",
                      sys.exc_info()[0])
		try:
			conn.close()
		except:
			pass
		return []

	resp = conn.getresponse()
	if resp.status == 200:
		output = resp.read()
		try:
			retout = json.dumps(json.JSONDecoder().decode(output),
                                            sort_keys=True, indent=4)
		except:
			retout = output
	else:
		print("Addama readFile Error:", resp.status, resp.reason)
		retout = []
	
	conn.close()
	return retout
		

class S3Handler(CommHandler):
        
    def __init__(self, apicrap):
        """
        Read auth settings from file
        """
        pass


    def _handleAuth(self):
        pass

    def readFile(self, uri):
	return []



