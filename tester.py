#!/usr/bin/env python

import DataClasses

line = 7

tdatMT = DataClasses.Data()
if tdatMT.synid == None and tdatMT.data_uri == None:
	print "correct", tdatMT.synid, tdatMT.data_uri
else:
	print "*FAIL* line:", line, tdatMT.synid, tdatMT.data_uri
line = line + 7

testData = DataClasses.Data("syn4489", "http://thisguy.com/is/so very cool/yes.html")
if testData.synid == "syn4489" and testData.data_uri == "http://thisguy.com/is/so%20very%20cool/yes.html":
	print "correct", testData.synid, testData.data_uri
else:
	print "*FAIL* line:", line, testData.synid, testData.data_uri
line = line + 7

tData = DataClasses.Data("    What does this do?    ")
if tData.synid == None and tData.data_uri == "What%20does%20this%20do?":
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





