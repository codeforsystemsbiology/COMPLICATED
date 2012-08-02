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
                                        'Local':3, 'local':3}[data_loc]
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

        if data_loc == 3:
            self.local_cache = self.data_uri
            self.data_uri = None
        else:
            self.local_cache = None

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

    def write(self, data_pref, uri, key = None):
        if key == None and self.Comm is not None:
            key = self.Comm.ApiKey
        if data_pref not in [1,2,3]:
            try:
                data_pref = {'addama':1,'Addama':1,'S3':2,'s3':2,
                                        'Local':3, 'local':3}[data_pref]
            except:
                return False

        if data_pref == 3 and self.data_uri is not None:
            try:
                self._toFile(uri)
                return True
            except:	
                print('write Error - Could not write to file: ' + uri)
                return False
        
        elif data_pref == 1 and self.local_cache is not None:
            if key is None:
                print('write Error: missing Addama apikey')
                return False
            try:
                _toAddama(uri, key)
                return True
            except:
                print('write Error - Could not write to uri: '+ uri)
                return False
        else:
            return False

    def _toAddama(self, addama_dir, key):
        """
        Take the current data obj, 
        """
        if key is not self.ApiKey:
            self.Comm = AddamaHandler(key)
            self.ApiKey = key
        self.Comm.writeFile(addama_dir, open(self.local_cache, "rb"))


    def _discoverLocation(self):
        """

	    *pop a couple of HEADs then check status*

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
        if local_cache == '' and self.local_cache is not None:
            output = open(self.local_cache, 'rb')
        elif self.Comm is None and self.local_cache is None:
            print('getData Error: No uri or local cache to pull from')
            return None
        else:
            output = self.Comm.readFile(self.data_uri)

        if local_cache == '':
            return output
        if local_cache == '.':
            fname = self.data_uri.split('/')[-1]	
        elif local_cache.count('.'):
            fname = local_cache
        elif local_cache.endswith('/'):
            fname = local_cache+self.data_uri.split('/')[-1]
        else:
            fname = local_cache+'/'+self.data_uri.split('/')[-1]

        f = open(fname, 'wb')
        f.write(output)
        f.close()
        self.local_cache = fname
        return output

    def _toFile(self, local_cache):
        """
	    Transfers web data to local cache
        """
        f = open(local_cache, 'wb')
        f.write(self.Comm.readFile(self.data_uri))
        f.close()
        self.local_cache = local_cache

    def _fromFile(self,filepath, filename):
        """
        Given a local path and filename, returns useable data object
        """
        

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
            return None
        
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
            return None

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
            retout = None
        
        conn.close()
        return retout
	

    def writeFile(self, uri, data):
        if isinstance(data, str):
            try:
                data = open(data, "rb")
            except:
                print("Error opening data file: " + data)
                return False
        try:
            headers = {"x-addama-apikey": self.ApiKey,"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain" }
            conn = httplib.HTTPSConnection(self.Host)
            uri = uri.lstrip(self.Host)
            conn.request("POST", uri, data, headers)
        except:
            print("Addama readFile Connection/Request Error:", 
                          sys.exc_info()[0])
            try:
                conn.close()
            except:
                pass
            return False
        out = conn.getresponse()
        out = out.read()
        conn.close()
        return out
	

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



