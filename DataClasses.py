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

import socket
import sys
import os
import urllib
import urllib2
import urlparse
import httplib
import ConfigParser
import mimetypes
import mimetools
import pycurl
from cStringIO import StringIO

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
        if data_loc not in [None, Data.Addama, Data.S3, Data.Local]:
            try:
                data_loc = {'addama':1,'Addama':1,'S3':2,'s3':2,
                                        'Local':3, 'local':3}[data_loc]
            except:
                data_loc = None

        (self.synid, self.data_uri) = self._inputCheck(synid, data_uri)

        if self.data_uri is not None:
            self.data_uri = self.data_uri.split('https%3A//')[-1]
            self.data_uri = self.data_uri.split('http%3A//')[-1]

        (self.local_cache, self.data_uri) = self._localCacheSetup(data_loc, self.data_uri)

        self.Comm = self._CommSetup(data_loc, key)

    def _inputCheck(self, synid, uri):
        if uri == None:
            if synid == None:
                return None, None
            elif synid.startswith("syn") and not synid.count("."):
                return synid, None
            else:
                return None, urllib.quote(synid)
        else:
            return synid, urllib.quote(uri)

    def _localCacheSetup(self, data_loc, uri):
        if data_loc == Data.Local:
            return uri, None
        else:
            return None, uri

    def _CommSetup(self, data_loc, key):
        if data_loc == None:
            data_loc = self._discoverLocation()

        if data_loc == Data.Addama:
            return AddamaHandler(key)
        elif data_loc == Data.S3:
            return S3Handler(key)
        else: # do local?
            return None

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
            #try:
            return self._toAddama(uri, key)
            #except:
            #    print('write Error - Could not write to uri: '+ uri)
            #    return False
        else:
            return False

    def _toAddama(self, addama_dir, key):
        """
        Take the current data obj, 
        """
        if (self.Comm is None) or (key is not self.Comm.ApiKey):
            self.Comm = AddamaHandler(key)
            self.ApiKey = key
        return self.Comm.writeFile(addama_dir, open(self.local_cache, "rb")) 

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
        #try:
        ghead = {"x-addama-apikey": self.ApiKey}
        gcon = httplib.HTTPSConnection(self.Host)
        gparams = urllib.urlencode({})
        uri = uri.lstrip(self.Host)
        gcon.request("GET", uri, gparams, ghead)
        gout = gcon.getresponse().read()
        guri = gout.split('"')[1]
        filename = 'example.txt'
        filesize = os.path.getsize(filename)
        values = [
            ("field1", "this is test and stuff"),
            ("field2", (pycurl.FORM_FILE, filename)),
            ('field3', (pycurl.FORM_CONTENTS, 'this is wei\000rd, but fun.'))
        ]
        print guri
        eguri = guri.split('https://')[-1]
        print guri
        #guri = guri.lstrip(self.Host)
        print repr(guri)
        headers = {"Content-type": get_content_type(filename), "Content-Length": filesize, "Accept": "text/plain"}
        #conn = httplib.HTTPConnection(('price-external.systemsbiology.net/'))
        #conn.request("POST", guri.split('price-external.systemsbiology.net/')[-1], data, ghead)
        gurips = eguri.split('.net',1)
        gurips[0] = gurips[0] + '.net'
        print gurips
        conn = httplib.HTTPSConnection(gurips[0])
        #conn = httplib.HTTPSConnection(guri)
        #pparams = urllib.urlencode({})
        #conn.request("GET", gurips[1], pparams, ghead)
        #pparams = urllib.urlencode({'name':'example.txt', 'file':data})
        from multipart import Multipart
        m = Multipart()
        m.file('hello','hello.txt', 'Ijustwantthis to work', {'Content-Type':'text/text'})
        ct, tbody = m.get()
        print ct
        print tbody
        request = urllib2.Request(url = guri, headers={'Content-Type':ct}, data=tbody)
        print urllib2.urlopen(request).read()
        conn.request("GET", gurips[1], data.read(), ghead)
        """
        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        #c.setopt(c.HTTPPOST, [('title', filename), (('file', (c.FORM_FILE, filename)))])
        #c.setopt(c.READFUNCTION, FileReader(open(filename, 'rb')).read_callback)
        bodyOutput = StringIO()
        headersOutput = StringIO()
        c.setopt(c.WRITEFUNCTION, bodyOutput.write)
        #c.setopt(c.HTTPHEADER, ["Content-type: text/plain"])
        print guri
        c.setopt(c.VERBOSE, 1)
        #c.setopt(c.UPLOAD, 1)
        c.setopt(c.URL, guri)
        c.setopt(c.HTTPPOST, values)
        c.setopt(c.INFILESIZE, filesize)
        c.perform()
        print bodyOutput.getvalue()
        
        f1 = 'example', 'example.txt', data
        netu = f1,

        print post_multipart(guri, gurips[1], None, netu )
        print data.read()
        """
        #except:
        #    print("Addama readFile Connection/Request Error:", 
        #                  sys.exc_info()[0])
        #    try:
        #        conn.close()
        #    except:
        #        pass
        #    return False
        out = conn.getresponse()
        #print out.status
        out = out.read()
        print out
        gcon.close()
        #conn.close()
        return None #out
	
class FileReader:
    def __init__(self,fp):
        self.fp = fp
    def read_callback(self, size):
        return self.fp.read(size)

## {{{ http://code.activestate.com/recipes/146306/ (r1)
import httplib, mimetypes

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    print errcode, errmsg, headers
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    """    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    """
    print files
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value.read())
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
## end of http://code.activestate.com/recipes/146306/ }}}


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



