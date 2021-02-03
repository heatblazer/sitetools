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
TURN_OFFSET = 4
TURN_RANGE_MIN = 0x4000
TURN_RANGE_MAX = 0x4004

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
FILLIN = 0x16FE

ALLOCATE_SUCCESS_RESPONSE = 0x0103
REFRESH_REQUEST = 0x0004
CHANNEL_BIND_REQUEST = 0x0009
DATA_INDICATION = 0x0017
CREATE_PERMISSION_SUCCESS_RESPONSE = 0x0108
CHANEL_BIND_SUCCESS_RESPONSE = 0x0109
REFRESH_ERROR_RESPONSE = 0x0114

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
XOR_RELAYED_ADDRESS = 0x0016
DATA = 0x0013
ICE_CONTROLED = 0x8029
ICE_CONTROLLING = 0x802a
XOR_MAPPED = 0x0020
UNKNOWN = 0xc057
SOFTWARE = 0x8022
PRIORITY = 0x0024
RESERVATION_TOKEN = 0x0022

class StunStatus:
    '''stun session messages and attribs'''
    class Priorities:
        '''stun meta'''
        Telegram = [1853824768]
        Facebook = [1845501695]
        Skype = [1862269950, 1862269438, 1862270462]

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
                XOR_PEER_ADDRESS : "XOR PEER ADDRESS",
                DATA : "DATA",
                SOFTWARE : "SOFTWARE",
                PRIORITY : "PRIORITY",
                RESERVATION_TOKEN : "RESERVATION TOKEN"
            }


####>> STUN
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
####<< STUN

#Packet, Time, Address A,Port A,Address B,Port B,STUN Command,Username,Username Sorted,XOR-PEER-ADDRESS



class TLVpacket(dpkt.Packet):

    __hdr__ = (
        ('tag', 'I', 0),
        ('length', 'I', 0),
    )

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        self.data = self.data[:self.length]
        if len(self.data) < self.length:
            raise dpkt.NeedData
    #TLVPacket        

class Frame(dpkt.Packet):

    __hdr__ = (
        ('length_bytes', '3s', 0),
        ('type', 'B', 0),
    )

    @property
    def length(self):
        return struct.unpack('!I', b'\x00' + self.length_bytes)[0]

    def unpack(self, buf):
        dpkt.Packet.unpack(buf)
        self.data = self.data[:self.length]
        if len(self.data) != self.length:
            raise dpkt.NeedData


class CsvEnums:             
    rows = ["Packet", "Time","Address A", "Port A", "Address B", "Port B", "STUN Command", 
    "Username", "Username Sorted", "XOR-PEER-ADDRESS", "HAS CHILDREN", "ORIGIN", "APP-NAME",
    "CALL DIRECTION", "PRIORITY"]


class KafkaEnums:
    rows = ["Type", "Transport"]


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
        self.has_children = False
        self.root_cnt = 1
        self.name = None
        self.call_dir = None
        self.priority = -1 # negative - missing 
        self.tokens = 0
#TODO
    def app(self):
        if self.uname is None:
            if self.tokens > 2:
                self.name = "WhatsApp"
        else:
            self.uname = str(self.uname)
            if ":" in self.uname:
                s = self.uname.split(":")
                if self.priority in StunStatus.Priorities.Telegram:
                    self.name = "Telegram"
                elif self.priority in StunStatus.Priorities.Facebook:
                    self.name = "Facebook"
                elif self.priority in StunStatus.Priorities.Skype:
                    self.name = "Skype"                    
                else:
                    pass
        return self.name

    def user(self):
        if self.uname is not None:
            try:
                self.uname = self.uname.decode('ascii')
                return str(self.uname)
            except:
                return self.uname
        return None

    def __lt__(self, other):
        return self.counter <= other.counter and self.root_cnt > other.root_cnt

    def __eq__(self, other):
        return self.counter == other.counter


    def user_fix(self):         
        if self.uname is not None:
            if ":" in str(self.uname):
                uname = self.uname.split(":")
                if len(uname) == 2:
                    if Utils.quick_cmp(uname[0], uname[1]):
                        t = uname[0]
                        uname[0] = uname[1]
                        uname[1] = t
                    uname  = ":".join(uname)
                    return uname
            return self.uname


#Packet, Time, Address A,Port A,Address B,Port B, STUN Command ,Username,Username Sorted,XOR-PEER-ADDRESS, Origin, APP NAME, CALL DIR

    def ouput(self, csvwriter):
        if csvwriter is not None:
            csvwriter.writerow({
            CsvEnums.rows[0]:self.counter, 
            CsvEnums.rows[1]:self.time, 
            CsvEnums.rows[2]:self.srcip, 
            CsvEnums.rows[3]:self.srcport, 
            CsvEnums.rows[4]:self.dstip, 
            CsvEnums.rows[5]:self.dstport, 
            CsvEnums.rows[6]:self.message_type,
            CsvEnums.rows[7]:self.user(),
            CsvEnums.rows[8]:self.user_fix(),
            CsvEnums.rows[9]:self.xor_p_address, 
            CsvEnums.rows[10]:self.has_children,
            CsvEnums.rows[11]:str("{}.{}".format(self.counter, self.root_cnt)),
            CsvEnums.rows[12]:self.app(),
            CsvEnums.rows[13]:self.call_dir,
            CsvEnums.rows[14]:-1#self.priority #let's not shjare the priority for now...
            })
###########################################################################################################
    
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


def parse_tlv_stream(buf):
    i = 0
    packets = []
    while True:
        try:
            p = TLVpacket(buf[i:])
            packets.append(p)
            i += len(p)
        except dpkt.NeedData:
            break
    else:
        pass

    return i, packets

####################>>>> UTILS
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
    def dump_stun(stun, m, ip_port, ts, frameno):
        stuns = list()
        if m.type not in StunStatus.messages:
            return stuns
        csvi = CapCtx(ip_port[0], ip_port[1], ip_port[2], ip_port[3], ts, frameno)
        csvi.message_type = StunStatus.messages[m.type]
        cutoff = int( len(stun) - len(m.data) )
        transaction_id = []
        for i in range(8, cutoff):
            transaction_id.append(hex(stun[i]))
        attrs = parse_attrs(m.data)
        sindex = 0         
        for a in attrs:
            if a[0] in StunStatus.attrs:
                attr = int(a[0])
                if attr is XOR_PEER_ADDRESS:
                    xport = int ((a[1][2] << 8) | a[1][3])
                    xport = (MAGIC_COOKIE >> 16) ^ xport
                    ip_orig = a[1][4] << 24 | a[1][5] << 16 | a[1][6] << 8 | a[1][7]
                    ip_orig ^= MAGIC_COOKIE
                    ip_xtype = [(ip_orig >> 24) & 0xFF, (ip_orig >> 16) & 0xFF, (ip_orig >> 8) & 0xFF, ip_orig & 0xFF]
                    k =  "{}.{}.{}.{}:{}".format(ip_xtype[0], ip_xtype[1], ip_xtype[2], ip_xtype[3], xport)
                    csvi.xor_p_address = k
                elif attr is XOR_MAPPED:
                    pass
                elif attr is USERNAME:
                    csvi.uname = attrs[sindex][1]
                elif attr == ICE_CONTROLED:
                    csvi.call_dir = "CALLED"
                elif attr == ICE_CONTROLLING:
                    csvi.call_dir = "CALLING"
                elif attr == SOFTWARE:
                    print (attrs[sindex][1])
                    #csvi.name = attrs[sindex][1]
                elif attr == PRIORITY:
                    csvi.priority = Utils.btoi(attrs[sindex][1])
                elif attr == RESERVATION_TOKEN:
                    csvi.tokens += 1
                elif attr is DATA:
                    csvi.has_children = True
                    csvi.root_cnt += 1
                    s = STUN(attrs[sindex][1])
                    stuns = stuns + Utils.dump_stun(attrs[sindex][1], s, ip_port, ts, csvi.counter)
            sindex+=1
        stuns.append(csvi)
        return stuns

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

    @staticmethod
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


    @staticmethod
    def pcap_walker(packets):
        missing = {}
        csvdata = list()        
        for i in range(0, len(packets)):            
            ts, pkt = (packets[i])
            ts = str(datetime.datetime.utcfromtimestamp(ts))
            eth=dpkt.ethernet.Ethernet(pkt)
            try:     
                stun = eth.data.data.data
                ip_port = Utils.printip(eth)
                cookie = 0
                cookiestun, cookieturn  = Utils.btoi(stun[TURN_OFFSET:TURN_OFFSET*2]), Utils.btoi(stun[TURN_OFFSET*2:TURN_OFFSET*3])
                if cookiestun != MAGIC_COOKIE and cookieturn != MAGIC_COOKIE:
                    continue
            except:
                continue

            m = STUN(stun)
            if m.type >= TURN_RANGE_MIN and m.type <= TURN_RANGE_MAX:
                m2 = STUN(stun[TURN_OFFSET:])   
                m = m2 #swap with TURN
                cookie = cookieturn
            else:
                cookie = cookiestun
            
            if cookie != MAGIC_COOKIE: #m.type not in StunStatus.messages:
                continue
            else:
                if m.type not in StunStatus.messages:
                    if m.type not in missing:
                        missing.update({m.type:1})
                    else:
                        missing[m.type] += 1
                    continue            
            
            csvis = Utils.dump_stun(stun, m, ip_port, ts, i+1)   
            csvdata += csvis
        for kv in missing:
            print ("missing type: ", hex(kv), " count:", missing[kv])        
        return csvdata

    @staticmethod
    def fix_pcap(cap, n=0):
        '''todo'''
        with open(cap, "rb") as fp:
            ln = fp.read()
            print(ln)
            if ln[0] == 10:                
                bdata = ln[n:len(ln)]
                fpfix = open(str('%sFix.pcap' % cap), "wb")
                fpfix.write(struct.pack(str('%sB' % len(bdata)), *bdata))
                fpfix.close()

################# << UTILS

class KafkaDump:

    def __init__(self, fname):
        self._fname = fname
        self._kafkaObj = None
        with open(self._fname ,'r') as fp:
            self._kafkaObj = json.load(fp)
    
    
    def Run(self):
        print("KafkaDump exec...")
        home = Utils.home_dir()
        files = Utils.getListOfFiles(home)

        kafkawr = csv.DictWriter(open("out.csv", "w"), fieldnames=KafkaEnums.rows)
        kafkawr.writeheader()


        for rec in self._kafkaObj:
            if rec == "type":
                print(rec, "--", self._kafkaObj[rec])
                kafkawr.writerow({KafkaEnums.rows[0] : self._kafkaObj[rec]})
            elif  rec == "transport":
                kafkawr.writerow({KafkaEnums.rows[1] : self._kafkaObj[rec]})
                if "ip_access_network" in self._kafkaObj[rec]:
                    for r in self._kafkaObj[rec]["ip_access_network"]:
                        print(r)
#                        arr.update({'ip_access_network' : self._kafkaObj[rec]["ip_access_network"]})
                if "ip_connections" in self._kafkaObj[rec]:
                    for r in self._kafkaObj[rec]["ip_connections"]:
                        print(r)
#                        arr.update({'ip_connections' : self._kafkaObj[rec]["ip_connections"]})


class StunAnalyzer:

    def __init__(self):
        self.dummy = None


    def Run(self, args=[]):
        print("StunDump exec...")
        home = Utils.home_dir()
        files = Utils.getListOfFiles(home)
        for f in files:
            if (".pcap" in f or ".snoop" in f) and ".csv" not in f:
                pcapfile = f
                print ("Processing file: {", f, "}")
                caps = dpkt.pcap.Reader(open(pcapfile,'rb'))
                caplst = caps.readpkts()
                csv_items = Utils.pcap_walker(caplst)
                csv_items.sort() # overriden  < and == 
                with  open("{}.csv".format(pcapfile), 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=CsvEnums.rows)
                    writer.writeheader()
                    for csvi in csv_items:
                        csvi.ouput(writer)


#TODO: move in separte app 
if __name__ == "__main__":
#    kafkadmp = KafkaDump("test.json")
#    kafkadmp.Run()    
    sd = StunAnalyzer()
    sd.Run()

    
