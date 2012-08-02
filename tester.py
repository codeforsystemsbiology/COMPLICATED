#!/usr/bin/env python

import DataClasses
import os


line = 7

tdatMT = DataClasses.Data()
if tdatMT.synid == None and tdatMT.data_uri == None:
	print "correct", tdatMT.synid, tdatMT.data_uri
else:
	print "*FAIL* line:", line, tdatMT.synid, tdatMT.data_uri
line = line + 7

testData = DataClasses.Data("syn4489", "thisguy.com/is/so very cool/yes.html")
if testData.synid == "syn4489" and testData.data_uri == "thisguy.com/is/so%20very%20cool/yes.html":
	print "correct", testData.synid, testData.data_uri
else:
	print "*FAIL* line:", line, testData.synid, testData.data_uri
line = line + 7

tData = DataClasses.Data("https://What does this do?")
if tData.synid == None and tData.data_uri == "What%20does%20this%20do%3F":
	print "correct", tData.synid, tData.data_uri
else:
	print "*FAIL* line:",line , tData.synid, tData.data_uri
line = line + 7

tdat = DataClasses.Data("syn630639")
if tdat.synid == "syn630639" and tdat.data_uri == None:
	print "correct", tdat.synid, tdat.data_uri
else:
	print "*FAIL* line:", line, tdat.synid, tdat.data_uri
line = line + 7

Adata = DataClasses.Data('https://price-external.appspot.com/addama/workspaces/fileshare/Welcome.txt', data_loc=1, key='price-external.apikey')
AddOut = Adata.getData('.')
AddFILE = open('Welcome.txt', 'r')
AddFtxt = AddFILE.read()
if AddOut == AddFtxt:
	os.system('rm Welcome.txt')
	print "correct - file written properly in current directory"
else:
	print "*FAIL* file did not write correctly. line:", line+1, AddOut
	print "Welcome.txt not deleted"
if AddOut == 'This is the Price Lab External File Share.\n':
	print "corect -", repr(AddOut)
else:
	print "*FAIL* Addama getData (line:", line, ") output is incorrect:\n", AddOut
line = line + 16

