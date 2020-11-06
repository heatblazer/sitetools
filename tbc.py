#!/usr/bin/env python
import os
import os.path
from os import path
import subprocess
import sys

#constants - move to other file
CLI="/usr/confd/bin/confd_cli --user admin"

REQ="request ip-intelligence-platform applications DPE-apps DPE-app"

RECTRAFFIC="record-traffic "

TF_ACTION_START="tf-action start-trace"

TF_ACTION_STOP="tf-action stop-trace"

HOME= os.getcwd()

IIPC="#!/bin/bash \n echo o | /usr/confd/bin/confd_cli --user admin \n"

HELP = r'''
        usage:\r\n
        To start capture:
        tboss-capture --ip <1..6> xx.xx.xx.xx --start\r\n
        To stop capture:
        tboss-capture --ip <1..6> xx.xx.xx.xx --stop\r\n
        To omit recordinc pcaps:
        tboss-capture --ip <1..6> xx.xx.xx.xx --start/--stop --norec\r\n
        To show tboses per site:
        tboss-capture --lsbos\r\n
        To show id:
        tboss-capture --id\r\n
        To show this page:
        tboss-capture --help\r\n
        '''

OLD_BOS = True

GET_DELETE = False

NO_COPY = False

def bakesftp(ip):
        print "Baking sftp command"
        path = None
        try:
                path= ip.replace(".", "_")
                if os.path.isdir(path) is False:
                        os.mkdir(path)
                else:
                        print path, " exists"

                fp = open(str("%s/%s.sh" % (HOME, path)), "w")
                if GET_DELETE is True:
                        fp.write(str("#!/usr/bin/bash\n sftp root@%s <<EOF\n cd ../service/DPE/TrafficRecorder\nget *.pcap\nrm *.pcap\nquit\n<<EOF\n" % ip))
                else:
                        fp.write(str("#!/usr/bin/bash\n sftp root@%s <<EOF\n cd ../service/DPE/TrafficRecorder\nget *.pcap\nquit\nEOF\n" % ip))
        except:
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
        """is a functor class"""
        def __init__(self,echo="echo", interpreter=CLI):
                self._echo = echo
                self._interpreter= interpreter
                self._stdout = None
                self._stderr = None
                pass


        def execute(self, cmd):
                c= subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                self._stdout, self._stderr = c.communicate()



        def __call__(self, cmd):
                fcmd=str("echo %s | %s" % (cmd, CLI))
                bakeipc(fcmd)
                fp = subprocess.Popen(str("%s/iipc.sh" % HOME), stdout=subprocess.PIPE, shell=True)
                self._stdout, self._stderr = fp.communicate()



class App:

        def __init__(self, ippatern="1.1."):
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
                                                if ippatern in tmp:
                                                        continue
                                                else:
                                                        ss = tmp.split(" ")
                                                        self._bosip.append(ss[-1])


        def addIp(self, ip):
                self._ip.append(ip)



        def addPattern(self, pat):
                self._pattern = pat



        def lsbos(self):
                for tb in self._tbosses:
                        print tb
                        for i in range(0, len(self._bosip)-1):
                                print "IP: ", self._bosip[i]



        def run(self, start=True, rec=True, execute=True):
                print "Run..."
                if execute is False:
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
                if NO_COPY is True:
                        return
                if start is False:
                        for i in range(0, len(self._bosip)-1):
                                self._bakedsftp.append(bakesftp(self._bosip[i]))

                        for bsf in self._bakedsftp:
                                spl = bsf.split("/")
                                path = str("/%s/%s/%s/%s/" % (spl[1], spl[2], spl[3], spl[4]))
                                os.system(str("bash %s" % bsf))
                                os.system(str("mv *.pcap %s" % path))

                pass #endcall



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

                        if sys.argv[i] == "--ippat":
                                app.addPattern(sys.argv[i+1])
                        if sys.argv[i] == "--del":
                                GET_DELETE = True
                        if sys.argv[i] == "--nocpy":
                                NO_COPY = True

                        if sys.argv[i] == "--start":
                                run = True
                        elif sys.argv[i] == "--stop":
                                run = False
                        elif sys.argv[i] == "--norec":
                                rec = False
                        elif sys.argv[i] == "--id":
                                app.id()
                                execute =False
                        elif sys.argv[i] == "--lsbos":
                                app.lsbos()
                                execute = False
                        elif sys.argv[i] == "--help":
                                print HELP
                                execute = False
                        elif sys.argv[i] == "--ver":
                                app.ver()
                                execute = False
                        elif sys.argv[i] == "--cfg":
                                app.showcfg()
                                execute = False


                app.run(run, rec, execute)
##################################################################################################################################
