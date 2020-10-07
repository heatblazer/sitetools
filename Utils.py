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

#csv
import csv #pip install csv

#deep packet inspection stuff
import dpkt #pip install dpkt

# C like :) 
import struct


# STUN - RFC 3489
# http://tools.ietf.org/html/rfc3489
# Each packet has a 20 byte header followed by 0 or more attribute TLVs.

MAGIC_COOKIE = 0x2112A442


# Message Types
BINDING_REQUEST = 0x0001
BINDING_RESPONSE = 0x0101
SEND_INDICATION = 0x0016
CREATE_PERMISSION = 0x0008
BINDING_ERROR_RESPONSE = 0x0111
CREATE_PERM_ERR_RESPONSE = 0x0118
SHARED_SECRET_REQUEST = 0x0002
SHARED_SECRET_RESPONSE = 0x0102
SHARED_SECRET_ERROR_RESPONSE = 0x0112
ALLOCATE_REQUEST = 0x0003
ALLOCATE_REQUEST_ERROR_RESPONSE = 0x0113

ALLOCATE_SUCCESS_RESPONSE = 0x0103
REFRESH_REQUEST = 0x0004
CHANNEL_BIND_REQUEST = 0x0009
DATA_INDICATION = 0x0017
CREATE_PERMISSION_SUCCESS_RESPONSE = 0x0108
CHANEL_BIND_SUCCESS_RESPONSE = 0x0109
REFRESH_ERROR_RESPONSE = 0x0114

'''
[‎10/‎7/‎2020 11:21 AM]  Stoykov, Stanimir:  
 0x0103	Allocate Success Response
0x0004	Refresh Request
0x0104	Refresh Success Response
0x0009 Channel-Bind request
0x0017 Data Indication
0x0108 Create Permission Success Response
0x0109 Channel-Bind success response
0x0114 Refresh error response 
''' 



# Message Attributes
MAPPED_ADDRESS = 0x0001
RESPONSE_ADDRESS = 0x0002
CHANGE_REQUEST = 0x0003
SOURCE_ADDRESS = 0x0004
CHANGED_ADDRESS = 0x0005
USERNAME = 0x0006
PASSWORD = 0x0007
MESSAGE_INTEGRITY = 0x0008
ERROR_CODE = 0x0009
UNKNOWN_ATTRIBUTES = 0x000a
REFLECTED_FROM = 0x000b
XOR_PEER_ADDRESS = 0x0012
ICE_CONTROLED = 0x8029
ICE_CONTROLLING = 0x802a
XOR_MAPPED = 0x0020
UNKNOWN = 0xc057

class StunStatus:

    messages = {BINDING_REQUEST:"BINDING REQUEST",
                BINDING_RESPONSE:"BINDING RESPONSE",
                BINDING_ERROR_RESPONSE : "BINDING ERROR RESPONSE",
                SHARED_SECRET_REQUEST : "SHARED SECRET REQUEST",
                SHARED_SECRET_RESPONSE : "SHARED SECRET RESPONSE",
                SHARED_SECRET_ERROR_RESPONSE : "SHARED SECRET ERROR RESPONSE",
                CREATE_PERM_ERR_RESPONSE : "CREATE PERMISSIONS ERROR RESPONSE",
                ALLOCATE_REQUEST : "ALLOCATE REQUEST",
                ALLOCATE_REQUEST_ERROR_RESPONSE : "ALLOCATE REQUEST ERROR RESPONSE",
                SEND_INDICATION : "SEND INDICATION",
                CREATE_PERMISSION : "CREATE PERMISSION",
                ALLOCATE_SUCCESS_RESPONSE : "ALLOCATE SUCCESS RESPONSE",
                REFRESH_REQUEST : "REFRESH REQUEST",
                CHANNEL_BIND_REQUEST : "CHANNEL BIND REQUEST",
                DATA_INDICATION : "DATA INDICATION",
                CREATE_PERMISSION_SUCCESS_RESPONSE : "CREATE PREMISSION SUCCESS RESPONSE",
                CHANEL_BIND_SUCCESS_RESPONSE : "CHANEL BIND SUCCESS RESPONSE",
                REFRESH_ERROR_RESPONSE : "REFRESH ERROR RESPONSE"
            }

    attrs =     {MAPPED_ADDRESS : "MAPPED ADDRESS",
                RESPONSE_ADDRESS : "RESPONSE ADDRESS",
                CHANGE_REQUEST : "CHANGE REQUEST",
                SOURCE_ADDRESS : "SOURCE ADDRESS",
                CHANGED_ADDRESS : "CHANGED ADDRESS",
                USERNAME : "USER NAME",
                PASSWORD : "PASSWORD",
                MESSAGE_INTEGRITY : "MESSAGE INTEGRITY",
                ERROR_CODE : "ERROR CODE",
                UNKNOWN_ATTRIBUTES : "UNKNOWN ATTRIBS",
                REFLECTED_FROM : "REFLECTED FROM",
                ICE_CONTROLED : "ICE CONTROLLED",
                ICE_CONTROLLING : "ICE CONTROLLING",
                XOR_MAPPED : " XOR MAPPED ADDRESS ",
                UNKNOWN : "UNKNOWN",
                XOR_PEER_ADDRESS : "XOR PEER ADDRESS"
            }




class STUN(dpkt.Packet):
    """Simple Traversal of UDP through NAT.

    STUN - RFC 3489
    http://tools.ietf.org/html/rfc3489
    Each packet has a 20 byte header followed by 0 or more attribute TLVs.

    Attributes:
        __hdr__: Header fields of STUN.
        TODO.
    """
    
    __hdr__ = (
        ('type', 'H', 0),
        ('len', 'H', 0),
        ('xid', '16s', 0)
    )

#Packet, Time, Address A,Port A,Address B,Port B,STUN Command,Username,Username Sorted,XOR-PEER-ADDRESS

class CsvEnums:             
    rows = ["Packet", "Time","Address A", "Port A", "Address B", "Port B", "STUN Command", "Username", "Username Sorted", "XOR-PEER-ADDRESS"]


class CapCtx:
    def __init__(self, sip, sport, dip, dport, time, counter):
        self.srcip = sip
        self.srcport = sport
        self.dstip = dip
        self.dstport = dport
        self.message_type = None
        self.uname = None
        self.xor_p_address = None
        self.time = time
        self.counter = counter
        self.uname_sorted = None

    def user(self):
        if self.uname is not None:
            try:
                self.uname = self.uname.decode('ascii')
                return self.uname
            except:
                return self.uname
        return None


    def user_fix(self):
        if self.uname is not None:
            try:
                uname = self.uname.split(":")
                if len(uname) == 2:
                    if uname[0][0] > uname[1][0]:
                        t = uname[0]
                        uname[0] = uname[1]
                        uname[1] = t
                    uname  = ":".join(uname)
                    return uname
            except:
                return self.uname
        return None


#Packet, Time, Address A,Port A,Address B,Port B, STUN Command ,Username,Username Sorted,XOR-PEER-ADDRESS

    def ouput(self, csvwriter):
        if csvwriter is not None:
            csvwriter.writerow({CsvEnums.rows[0]:self.counter, 
            CsvEnums.rows[1]:self.time, 
            CsvEnums.rows[2]:self.srcip, 
            CsvEnums.rows[3]:self.srcport, 
            CsvEnums.rows[4]:self.dstip, 
            CsvEnums.rows[5]:self.dstport, 
            CsvEnums.rows[6]:self.message_type,
            CsvEnums.rows[7]:self.user(),
            CsvEnums.rows[8]:self.user_fix(),
            CsvEnums.rows[9]:self.xor_p_address})
             

def tlv(buf):
    n = 4
    t, l = struct.unpack('>HH', buf[:n])
    v = buf[n:n + l]
    pad = (n - l % n) % n
    buf = buf[n + l + pad:]
    return t, l, v, buf


def parse_attrs(buf):
    """Parse STUN.data buffer into a list of (attribute, data) tuples."""
    attrs = []
    while buf:
        t, _, v, buf = tlv(buf)
        attrs.append((t, v))
    return attrs


class Utils(object):
    """ Utulity functions - static class """

    sresult = [] 

    @staticmethod
    def unlink(fname):
        pass

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
        # Iterate over all the entries
        for entry in listOfFile:            
            #if opt is not None and opt(entry) is True:
            #    continue

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
    def parse_stun(snoop):
        def printip(e):
            try:
                ip_hdr = e.data
                dst_ip_addr_str = socket.inet_ntoa(ip_hdr.dst)
                src_ip_addr_str = socket.inet_ntoa(ip_hdr.src)
                dport = ip_hdr.data.dport
                sport = ip_hdr.data.sport
                return (src_ip_addr_str, sport, dst_ip_addr_str, dport)
            except:
                return ("de.ad.be.ef", 0xffff, "de.ad.be.ef", 0xffff)
        
        csvdata = list()
        stun = None
        m = None
        counter = 1
        for ts, pkt in dpkt.pcap.Reader(open(snoop,'rb')):
            ts = str(datetime.datetime.utcfromtimestamp(ts))
            eth=dpkt.ethernet.Ethernet(pkt)             
            try:            
                stun = eth.data.data.data#.__name__                
                ip_port = printip(eth)
                csvi = CapCtx(ip_port[0], ip_port[1], ip_port[2], ip_port[3], ts, counter)            
            
                m = STUN(stun)        
                if m.type in StunStatus.messages:
                    csvi.message_type = StunStatus.messages[m.type]
                    cutoff = int( len(stun) - len(m.data) )
                    transaction_id = []
                    for i in range(8, cutoff):
                        transaction_id.append(hex(stun[i]))
                    #print("[TRANSACTION ID]:", transaction_id)
                    attrs = parse_attrs(m.data)         
                    for a in attrs:
                        '''
                            The format of the XOR-MAPPED-ADDRESS is:
                            0                   1                   2                   3
                            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                            |x x x x x x x x|    Family     |         X-Port                |
                            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                            |                X-Address (Variable)
                            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                        '''
                        
                        if a[0] in StunStatus.attrs:
                            #print("[[[ ", StunStatus.attrs[a[0]], " ]]]")
                            #print (">>> ", a , ">>> len:" ,len(a[1]))
                            attr = int(a[0])
#                            A = "{} : {}".format(ip_port[2], ip_port[3])
#                            B = "{} : {}".format(ip_port[0], ip_port[1])
                            if attr is XOR_PEER_ADDRESS:
                                xport = int ((a[1][2] << 8) | a[1][3])
                                xport = (MAGIC_COOKIE >> 16) ^ xport
                                ip_orig = a[1][4] << 24 | a[1][5] << 16 | a[1][6] << 8 | a[1][7]
                                ip_orig ^= MAGIC_COOKIE
                                ip_xtype = [(ip_orig >> 24) & 0xFF, (ip_orig >> 16) & 0xFF, (ip_orig >> 8) & 0xFF, ip_orig & 0xFF]
                                k =  "{}.{}.{}.{} : {}".format(ip_xtype[0], ip_xtype[1], ip_xtype[2], ip_xtype[3], xport)
                                csvi.xor_p_address = k
                            elif attr is XOR_MAPPED:
                                pass
                            elif attr is USERNAME:
                                csvi.uname = attrs[0][1]
                                if m.type is ALLOCATE_REQUEST or m.type is CREATE_PERMISSION:
                                    csvi.uname = attrs[1][1]
                    csvdata.append(csvi)
                    counter+=1
                else:
                    csvi.message_type = hex(m.type)
                    #print("[[ UNKNOWN STATUS ]]") #should not get here if full STUN support implemented
            except:
                pass
        return csvdata

if __name__ == "__main__":

    home = Utils.home_dir()
    files = Utils.getListOfFiles(home)

    for f in files:
        if (".pcap" in f or ".snoop" in f) and ".csv" not in f:
            pcapfile = f
            csv_items = Utils.parse_stun(pcapfile)
            with  open("{}.csv".format(pcapfile), 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CsvEnums.rows)
                writer.writeheader()
                for csvi in csv_items:
                    csvi.ouput(writer)
        

'''
    pcap_file = "08_Telegram_7_IOS100toAN153.pcap"
    csv_items = Utils.parse_stun(pcap_file)    
    csvname = "defaultdump.csv"

    csvfile =  open(csvname, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=CsvEnums.rows)
    writer.writeheader()
    for csvi in csv_items:
        csvi.ouput(writer)
    
'''

    