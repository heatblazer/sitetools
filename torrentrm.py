#verbosity
import warnings

#sys stuff
import os
import subprocess 
import sys
import socket
import datetime

#xml pareser
import xml.etree.ElementTree as ET

#json
import json

class Utils(object):
    """ Utulity functions - static class """

    sresult = [] 

    @staticmethod
    def is_json(d):
        """poorman validator of possible json """
        if d is None:
            return False
        d = str(d)
        return d[0] == '{' and d[len(d)-1] == '}'

    @staticmethod
    def unlink(fname):
        os.system("rm {}".format(fname))

    @staticmethod 
    def rmdir(dir_path):
        pass


    @staticmethod
    def parse_xml(xmlfile):
        try:
            tree = ET.parse(xmlfile)
            root = tree.getroot()
            return root
        except:
            return None


    @staticmethod
    def getListOfFiles(dirName, opt=None):
        # create a list of file and sub directories 
        # names in the given directory 
        listOfFile = os.listdir(dirName)
        allFiles = list()
        for entry in listOfFile:            
            fullPath = os.path.join(dirName, entry)                
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath):
                allFiles = allFiles + Utils.getListOfFiles(fullPath, opt)
            else:
                if opt is not None and opt(fullPath) is False:
                    allFiles.append(fullPath)
                elif opt is None:
                    allFiles.append(fullPath)
                
        return allFiles


    @staticmethod
    def home_dir():
        return os.path.dirname(os.path.realpath(__file__))


    @staticmethod
    def home():
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        return os.path.dirname(os.path.realpath(__file__))


    @staticmethod
    def dir_exists_ex(path, wdata=True):
        """wdata: mark False if only check for pathname, or default for path w contents"""
        res = False
        if os.path.isdir(path):
            if wdata is True:              
                res = len(os.listdir(path)) > 1
            res = True
        return res
    

    @staticmethod
    def find_file(dir, match):
        listOfFile = os.listdir(dir)
        allfiles = list()
        for entry in listOfFile:
            fullpath = os.path.join(dir, entry)
            if entry == match:
                Utils.sresult.append(fullpath)
            elif os.path.isdir(fullpath):
                allfiles = allfiles + Utils.find_file(fullpath, match)
            else:
                allfiles.append(fullpath)
        return allfiles


    @staticmethod
    def quick_cmp(str1, str2):
        l1 = len(str1)
        l2 = len(str2)
        strlen = l2 if l1 > l2 else l1
        i=0
        for i in range(0, strlen):
            if str1[i] != str2[i]:
                break
        return str1[i] > str2[i]
        




    @staticmethod
    def btoi(bdat, endiness=False):
        integerpart = []
        for b in bdat:
            integerpart.append(int(b))
        if endiness is False:
            integerpart.reverse()
        result = 0
        for i in range(0, len(integerpart)):
            result |= integerpart[i] << (i * 8)                    
        return result 


class Cmp:

    def __init__(self, what) -> None:
        self.match = what

    def __call__(self, what):
        if what.endswith(self.match):
            return False
        else:
            return True


if __name__ == "__main__":

    c = Cmp(".torrent")
    torrentfiles = Utils.getListOfFiles(Utils.home_dir(), c)
    for t in torrentfiles:
        Utils.unlink(t)
    
