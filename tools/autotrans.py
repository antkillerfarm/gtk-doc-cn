#! /usr/bin/env python
# -*- encoding:utf-8 -*-
# FileName: trans.py

"This file is part of ____"
 
__author__   = "yetist"
__copyright__= "Copyright (C) 2009 yetist <yetist@gmail.com>"
__license__  = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import re
import sys
import urllib
import simplejson
 
baseUrl = "http://ajax.googleapis.com/ajax/services/language/translate"

def getSplits(text,splitLength=4500):
    '''
    Translate Api has a limit on length of text(4500 characters) that can be translated at once, 
    '''
    return (text[index:index+splitLength] for index in xrange(0,len(text),splitLength))
 
 
def translate(text,src='en', to='zh'):
    '''
    A Python Wrapper for Google AJAX Language API:
    * Uses Google Language Detection, in cases source language is not provided with the source text
    * Splits up text if it's longer then 4500 characters, as a limit put up by the API
    '''
 
    params = ({'langpair': '%s|%s' % (src, to),
             'v': '1.0'
             })
    retText=''
    for text in getSplits(text):
            params['q'] = text
            resp = simplejson.load(urllib.urlopen('%s' % (baseUrl), data = urllib.urlencode(params)))
            try:
                    retText += resp['responseData']['translatedText']
            except:
                return ""
    return retText

def stop():
    raw_input("")

def get_message(data, line, atype="msgstr"):
        # if not translate
        if atype=="msgid":
            break_str="msgstr"
        else:
            break_str="\"Project-Id-Version:"
        message=""
        n = line
        if data[line].find(atype) >=0 and len(data[line].split('"')) > 2:
            if data[line].split('"')[1] != '':
                message += data[line].split('"')[1]+"\n"
            else:
                # if the next line is not empty, and
                while n+1< len(data) and len(data[n+1].strip()) > 0 and data[n+1].split('"')[1] != "":
                    message += data[n+1].split('"')[1]+"\n"
                    n = n+1
        return (message, line, n-line)

def _do_po_file (file_name):
    _merge_data = {}
    print ">>>", file_name
    data = open (file_name).readlines()
    newdata=data[:]
    first_msgstr = True
    baseline = 0
    for i in range(5, len(data)):
        if data[i].startswith("msgid"):
            (msgid, n1, cnt1) = get_message(data, i, "msgid")
            (msgstr, n2, cnt2) = get_message(data, n1+cnt1+1, "msgstr")
            if len(msgstr) > 0: #如果已经翻译则继续
                continue
            if len(msgid) > 0:
                newdata[baseline+n1:baseline+n1] = ["#, fuzzy\n"]
                baseline = baseline+1
                if cnt1 == 0:
                    newdata[baseline+n2] = ["msgstr \"" + translate(msgid).encode("utf-8") + "\"\n"]
                else:
                    c=baseline+n2
                    newdata[baseline+n2:baseline+n2+1] = ["msgstr \"\"\n", '"'+translate(msgid).encode("utf-8")+'"', "\n"]
                    baseline = baseline+2

            pot_fd = open(file_name, "w")
            for i in newdata:
                if i:
                    pot_fd.writelines (i)
            pot_fd.close()
 
def test(filename):
    _do_po_file(filename)
 
if __name__=='__main__':
    if len(sys.argv) == 2 and sys.argv[1].endswith(".po"):
        file = os.path.abspath(sys.argv[1])
        if os.path.isfile(file):
            test(file)
        else:
            print "File don't exists"
    else:
        print "File is not po"
