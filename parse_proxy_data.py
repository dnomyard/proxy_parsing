#!/usr/bin/env python
import os.path, os
import sys
import optparse

from squidRecord import *


"""
todo:
- still need to back out one level while iterating through directories
- parse command line arg . . .
    -c location of squid cache files
    -l location of squid log files
"""

def parseSquidCacheFiles():
    """ 
    Given location of squid cache, iterates through subdirectories and creates 
    data structure (dictionary) keyed by squid key and containing filename
    and URI of cached data
    """

    # parse command line options.  Using the "old" optparse instead of argparse
    # for better backward compatibility.
    parser = optparse.OptionParser(description='Proxy parsing arguments')
    parser.add_option('-c', action="store", dest="cacheFilePath", 
                        default="/var/spool/squid/", help="path to cached squid objects")
    parser.add_option('-l', action="store", dest="logFilePath", default="/var/log/squid/",
                        help="path to squid log files")

    options, remainder = parser.parse_args()
    listing = os.listdir(options.cacheFilePath)

    # call function to iterate through directories in squid proxy cache
    iterateDirectories(options.cacheFilePath, listing)


def iterateDirectories(path, subdirs):

    # make sure last character of path is "/"
    if path[-1] != "/":
        path = path + "/"
        
    # iterate through highest level of squid cache hierarchy
    for subdir in subdirs:
        newPath = path + subdir
        
        # be sure to list subdirs, don't try to get directory listings of files!
        if os.path.isdir(newPath):

            # list the subdirectories within the cache             
            listing = os.listdir(newPath)
      
            # now, loop through subdirs
            for subsubdir in listing:
                newNewPath = newPath + "/" + subsubdir
        
                if os.path.isdir(newNewPath):

                    sublisting = os.listdir(newNewPath)

                    # loop through cache objects in each non-empty folder and parse
                    if sublisting != []:
                        parseSquidCacheObject(newNewPath, sublisting)


def parseSquidCacheObject(newPath, listing):

    d1 = {}

    for infile in listing:
    
        fileName = newPath + "/" + infile

        f = open(fileName, 'rb')
    
        # parse squid proxy secret number from cache file
        #   - in squid cache file, key is offset 0x0a - 0x19 of file
        line1 = ""
        
        index = 0
    
        # read up to the beginning of the URI in the squid cache entry
        while  index < 0x3c:
            line1 = line1 + str(f.read(8))
            index = index + 1
    
        key = line1[0x0a:0x19]
        
        url = ""
        stop = 0 
    
        # parse out URI from squid proxy cache header data
        while line1[index].encode("hex") != "00":
            # print str(index) + " " + url
            line1 = line1 + str(f.read(8))    
            url = url + line1[index]
            index = index + 1
            #print url
    
        # print fileName + " " + key.encode("hex") + " " + url

        d1[str(key.encode("hex"))] = squidRecord(str(key.encode("hex")),
                                        fileName, url)

    for key, item in d1.items():
        print key, item.path, item.uri


if __name__ == "__main__":

    parseSquidCacheFiles()


