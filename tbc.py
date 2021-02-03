#!/usr/bin/python
import os
import os.path
from os import path
import subprocess
import sys

#constants - move to other file
CLI="/usr/confd/bin/confd_cli --user admin"
REQ="request ip-intelligence-platform applications DPE-apps DPE-app"
PRUCMD = "request ip-intelligence-platform applications prus pru pru+1 write-filters-summary match-all all"
RECTRAFFIC="record-traffic "
TF_ACTION_START="tf-action start-trace"
TF_ACTION_STOP="tf-action stop-trace"
SITE_NAME = "default"
HOME= os.getcwd()
MERGECAP_PATH = "\"c:\\Program Files\\Wireshark\\mergecap.exe\""
IIPC="#!/bin/bash \n echo o | /usr/confd/bin/confd_cli --user admin \n"
DEBUG = False
OLD_BOS = False
GET_DELETE = False

HELP = r'''
usage:
To start capture:
tbc.py --ip <1..6> xx.xx.xx.xx --start
To stop capture:
tbc.py --ip <1..6> xx.xx.xx.xx --stop
To omit recordinc pcaps:
tbc.py --ip <1..6> xx.xx.xx.xx --start/--stop --norec
To show tboses per site:
tbc.py --lsbos
To show id:
tbc.py --id
To dump PRU:
tbc.py --pru
---------------------------------------------------------------------------
After collecting all captures an archive is created with 'default.zip' name
if you want to change the name use:
--file <yourfilename>
(.zip) is applied by default so --file myfile is enough.
----------------------------------------------------------------------------
If you want to see more verbosity messages use: --v
----------------------------------------------------------------------------
If you want the sftp to delete the caputres from the TBoS, use: --d 
To show this page:
tboss-capture --help

Enjoy :)
----------------------------------------------------------------------------
'''

class TBOS_Consts:
    """ consts to replace hardcoded stuff"""
    Blade = "atca-blade", 
    Tbos = "tbos"
    Dlm1 = ";"
    Dlm2 = " " 
    Mgmt = "management"
    Num = "1.1"
    


def bakesftp(ip):
    print "Baking sftp command"
    path = None
    try:
        path= ip.replace(".", "_")
        if os.path.isdir(path) is False:
            os.mkdir(path)
        if DEBUG is True:
            print path, " exists"
            print "sfpt iipc" , str("%s/%s.sh" % (HOME, path))
        fp = open(str("%s/%s.sh" % (HOME, path)), "w")
        if GET_DELETE is True:
            fp.write(str("#!/usr/bin/bash\n sftp root@%s <<EOF\n cd /\n cd /service/DPE/TrafficRecorder\n get *.pcap\n rm *.pcap\n quit\n<<EOF\n" % ip))
        else:
            fp.write(str("#!/usr/bin/bash\n sftp root@%s <<EOF\n cd /\n cd /service/DPE/TrafficRecorder\n get *.pcap\n quit\n<<EOF\n" % ip))
        fp.close()
    except:
        print "Exception in bakesftp" 
        pass
    cmd = str("mv %s/%s.sh  %s/%s" % (HOME, path, HOME, path))
    print "Using ", cmd
    os.system(cmd)
    return str("%s/%s/%s.sh" %(HOME, path, path))


def bakeipc(b=IIPC):
    print "Baking command pipe"
    if path.exists(str("%s/iipc.sh" % HOME)):
        os.system(str("rm  -f %s/iipc.sh" % HOME))
    fp = open(str("%s/iipc.sh" % HOME),"w")
    fp.write(str(b))
    fp.close()
    os.system(str("chmod u+x %s/iipc.sh" % HOME))


class Cmd:

    def __init__(self,echo="echo", interpreter=CLI):
        self._echo = echo
        self._interpreter= interpreter
        self._stdout = None
        self._stderr = None
        pass

    def execute(self, cmd):
        c= subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self._stdout, self._stderr = c.communicate()
        pass

    def __call__(self, cmd):
        fcmd=str("echo %s | %s" % (cmd, CLI))
        bakeipc(fcmd)
        fp = subprocess.Popen(str("%s/iipc.sh" % HOME), stdout=subprocess.PIPE, shell=True)
        self._stdout, self._stderr = fp.communicate()
        return (self._stdout, self._stderr)


class App:

    def __init__(self):
            self._tbosses = []
            self._bosip = []
            self._ip = []
            self._full = []
            self._bakedsftp=[]
            c = Cmd()
            c("o")

            ln = c._stdout.split("\n")
            for l in ln:
                if "tbos" in l.lower():
                    tb = l.split(" ")
                    if len(l) > 1:
                        self._tbosses.append(tb[1])

            ips = Cmd()
            ips("show config")
            cf = ips._stdout.split("atca-blade")
            for c in cf:
                if "tbos" in c.lower():
                    spl = c.split(";")
                    for i in range(0, len(spl)):
                        if "management" in spl[i].lower():
                            tmp = spl[i-2]
                            if "1.1" in tmp:
                                continue
                            else:
                                ss = tmp.split(" ")
                                self._bosip.append(ss[-1])

    def addIp(self, ip):
        self._ip.append(ip)

    def lsbos(self):
        for i  in range(0, len(self._tbosses)):
            print self._tbosses[i], "@", self._bosip[i]
        

    def run(self, start=True, rec=True, execute=True):
        print "Run..."
        if execute is False:
            c = Cmd()
            sout, serr = c(PRUCMD)
            sout = sout.replace("\n", " ").split(" ")
            for s in sout:
                if "/" in s:
                    s = s.replace("//", "/")
                    tmp = None
                    os.system("cp -r %s %s" % (s, s.split("/")[-1]))						
                    break
            return False
        if len(self._ip) > 6:
            print "Can't enter more than 6 IPs"
            return False
        #tst
        record = "true"
        if rec is False:
            record = "false"

        j = 1
        #error correction for missing ip-addres-[xx]
        fix = str("ip-address %s" % self._ip[0])
        print fix
        for ip in self._ip:
            if j==1 and OLD_BOS is True:
                self._full.append(fix)
                if len(self._ip) == 1:
                    break
                j+=1
            else:
                self._full.append(str("ip-address-%s %s" % (j,ip)))
                j+=1

        for tbos in self._tbosses:
            ipcomplete = " ".join(self._full)
            if start is True:
                fullcommand=str("%s %s trace-flow %s %s %s  %s" % (REQ, tbos, ipcomplete, RECTRAFFIC, record, TF_ACTION_START))
            else:
                fullcommand=str("%s %s trace-flow %s %s %s %s" % (REQ, tbos, ipcomplete, RECTRAFFIC, record, TF_ACTION_STOP))
                #todo
            print fullcommand
            dispatch = Cmd()
            dispatch(str(fullcommand))
            
        if start is False:
            batch_buffer = []
            for i in range(0, len(self._bosip)-1):
                self._bakedsftp.append(bakesftp(self._bosip[i]))            
            for bsf in self._bakedsftp:
                spl = bsf.split("/")
                path = str("/%s/%s/%s/%s/" % (spl[1], spl[2], spl[3], spl[4]))
                os.system(str("bash %s" % bsf))
                os.system(str("mv *.pcap %s" % path))
                batch_buffer.append(spl[4])
            
            #post process bakery...
            batch_bakery = str() # "%s " % (MERGECAP_PATH, ) )
            rxidx = 1
            delidx = 1
            print batch_buffer
            #exit(1)
            for b in batch_buffer:	
                batch_bakery += str("%s -w %sDelivery.pcap  %s\DeliveryTrace*\r\n" % (MERGECAP_PATH, delidx, b))
                batch_bakery += str("%s -w %sRX.pcap %s\RxTrace* \r\n" % (MERGECAP_PATH, rxidx, b))
                rxidx += 1
                delidx+=1
            batch_bakery += str("%s -w DeliveryALL.pcap *Delivery.pcap \r\n" % MERGECAP_PATH)
            batch_bakery += str("%s -w RXAll.pcap *RX.pcap\r\n" % MERGECAP_PATH)
            with open("merge.bat", "w") as fp:
                fp.write(batch_bakery)		
            os.system(str("zip -r %s.zip * -x *.zip" % SITE_NAME))
            os.system(str("rm -rvf *_*")) 

    def id(self):
        c = Cmd()
        c("id")
        print c._stdout

    def ver(self):
        c = Cmd()
        c("dist")
        print c._stdout

    def showcfg(self):
        c = Cmd()
        c("show configuration")
        print c._stdout


##################################################################################################################################

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print "Not enough arguments. See usage"
    else:
        app = App()
        rec = True
        run = False
        execute = True
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--ip":
                app.addIp(sys.argv[i+1])

        for i in range(len(sys.argv)):
            if sys.argv[i] == "--start":
                run = True
                break
            elif sys.argv[i] == "--stop":
                run = False
            elif sys.argv[i] == "--norec" or sys.argv[i] == "-n":
                rec = False
            elif sys.argv[i] == "--id":
                app.id()
                exit(0)
            elif sys.argv[i] == "--lsbos" or sys.argv[i] == "-l":
                app.lsbos()
                exit(0)
            elif sys.argv[i] == "--help" or sys.argv[i] == "-h":
                print HELP
                exit(0)
            elif sys.argv[i] == "--ver" or sys.argv[i] == "-v":
                app.ver()
                exit(0)
            elif sys.argv[i] == "--cfg" or sys.argv[i] == "-c":
                app.showcfg()
                exit(0)
            elif sys.argv[i] == "--file" or sys.argv[i] == "-f":
                SITE_NAME = sys.argv[i+1]
            elif sys.argv[i] == "--debug" or sys.argv[i] == "-d":
                DEBUG = True
            elif sys.argv[i] == "--pru" or sys.argv[i] == "-p":
                execute=False
                break
            elif sys.argv[i] == "--delete":
                GET_DELETE = True
            else:
                pass # convinence
    
        app.run(run, rec, execute)
##################################################################################################################################
