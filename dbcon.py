from datetime import datetime, time, date
import psycopg2
from pyhive import presto
import json
import os
from db import dbutil as DB


G_IMODE = True
#"10.164.76.246", 8888, 'hive', paswd=None

'''
used pyinstaller : https://medium.com/@mounirboulwafa/creating-a-single-executable-file-exe-from-a-python-program-abda6a41f74f
pyinstaller --onefile  .\dbcon.py
'''

class QueryEngine:

        def __init__(self):
            self._query = []
            self._tostr = None
            self._begin = False
            
        
        def Select(self, What="*",From="kafka_events_12"): 
            self._query.append("select {0} from {1}".format(What, From))
            return self


        def Or(self, exp):
            if exp is not None:
                self._query.append(" or {0}".format(exp))
            return self


        def And(self, exp):
            if exp is not None:
                self._query.append(" and {0}".format(exp))
            return self


        def Ex(self, extra):
            if extra is not None:
                self._query.append(" {0}".format(extra))
            return self
        

        def compile(self):
            c = " ".join(self._query)
            self._tostr = c
            del self._query
            return self._tostr


        def __str__(self):
            return self._tostr



class KafkaEventsOb(object):

    def __init__(self, jobj):
        self._json = jobj


    def participants(self):
        if self._json['participants'] is not None:
            return self._json['participants']
        else:
            return None


    def ip_connections(self):
        if self._json['transport'] is not None:
            return self._json['transport']['ip_connections']
        return []


    def ip_acces_nw(self):
        if self._json['transport'] is not None:
            return self._json['transport']['ip_access_network']
        return []


    def name_on_storage(self):
        if self._json['content_files'] is not None:
            cf = []
            for i in self._json['content_files']:
                cf.append(i['name_on_storage'])
            return cf
        return []


    def path_on_storage(self):
        if self._json['content_files'] is None:
            cf = []
            for i in self._json['content_files']:
                cf.append(i['path_on_storage'])
            return cf
        return []


    def call_id(self):
        if self._json['call'] is not None:
            return self._json['call']['call_id']


    def jobj(self):
        return self._json


    def __str__(self):
        s = " ".join(self._json)
        return s



class AppCtx:

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self):
        self._hive, self._postgre = None, None
        self._qengine = QueryEngine()
        h = datetime.utcnow().strftime("%H:%M:%S")
        h = h.replace(":", "")
        n = str("session-%s-%s.ses" % (date.today(), h))
        self._fp = open(n, "w")
        self._jobjects = []
        self._db = DB()
        self._db.load('db.json')



    def jdata(self):
        return self._jobjects


    def QE(self):
        return self._qengine


    def Hive(self, ip, port, user, paswd):
        self._ip = ip
        self._port = port
        self._user = user
        self._passwd = paswd
        print "Logging into Hive..."
        try:
            self._hive = presto.connect(host=ip, port=port, username=user).cursor()
            print "Login success!"
        except Exception as ex:
            print "Login fails: ", ex.message



    def Postgre(self, ip, port, user, paswd):
        '''
        self._ip = ip
        self._port = port
        self._user = user
        self._passwd = paswd
        try:
            self._presto = presto.connect(host=ip, port=port, username=user).cursor()
        except Exception as ex:
            print ex.message
        '''
        pass
    
    def execute(self, sqlq):
        try:
            self._hive.execute(sqlq)
            dat = self._hive.fetchall()
            for d in dat:
                jobj = json.loads(d[5])
                if jobj is not None:
                    self._jobjects.append(KafkaEventsOb(jobj))
        except Exception as ex:
            print "Exception in executing {0} -> {1}".format(sqlq, ex.message)

    def finalize(self):
        self._fp.close()
        self._db.save()


    def writepretty(self, ob, opt=""):
        self._fp.write(opt)
        json.dump(ob, self._fp, skipkeys=False, ensure_ascii=True, check_circular=True,allow_nan=True, cls=None, indent=2, separators=None,encoding='utf-8', default=None, sort_keys=False)
        self._fp.write("\r\n")
        self._fp.flush()


    def delimit(self):
        self._fp.write("\r\n------------\r\n")
        self._fp.flush()


    def dumpall(self):
        for i in self._jobjects:
            self._fp.write("------------------------------------------------------------------------------------------\r\n")
            self._fp.write(str(i))
            self._fp.flush()


    def print_dbmode(self, msg):
        print str(">>>%s" % msg)


    def db_run(self, name):
        name = name.rstrip("\r").rstrip("\n")
        if self._db.exists(name) is False:
            print "No session ", name, " in database"
            return 
        print "--------------------------------------------------------------"
        print "Use !login! or !l! to login from user in session: ", name
        print "Use !at! to select query to execute."
        print"\t when prompted ?> enter index."
        print "Use !quit! or !q! to return to `imode`."
        blog = False

        QueriesCnt = int(self._db.get_queries_count(name))
        while True:
            rd = raw_input("db>")
            if "!quit!" in rd.lower() or "!q!" in rd.lower() or "!Q!" in rd.lower():
                break
            if "!login" in rd.lower() or "!l!" in rd.lower():
                conn = self._db.get_login(name)
                conn = conn.split(":")
                blog = True
                if len(conn) < 3:
                    continue
                elif len(conn) == 3:
                    self.Hive(str(conn[0]), int(conn[1]), str(conn[2]).rstrip("\r").strip("\n"), None)
                elif len(conn) == 4:
                    self.Hive(conn[0], int(conn[1]), str(conn[2]).rstrip("\r").strip("\n"), str(conn[3]).rstrip("\r").strip("\n"))
                else:
                    print "Error in HIVE"
                    blog = False

            elif "!at!" in rd.lower():
                if blog is False:
                    print "Not logged in..."
                else:
                    prmpt = "[0-{0}]>".format(QueriesCnt-1)
                    i = input(prmpt)
                    i = int(i)
                    q = self._db.get_query_at(name, int(i))
                    self.execute(q)
                    for d in self.jdata():
                        print "************************"
                        print d.participants()
                        self.writepretty(d)


    def run(self):
        """interactive mode - TODO: mark the commands used"""
        while True:
            rd = raw_input("imode>")
            if "!quit!" in rd.lower() or "!Q!" in rd:
                print "Bye"
                self.finalize()
                break
            elif "!db!" in rd.lower():
                self.print_dbmode("Use db file states...")
                self.print_dbmode("sessions saved")
                self.print_dbmode(self._db.get_all_sessions_cnt())
                session = raw_input("select session: ")
                
                self.db_run(session)
                

            elif "!query!" in rd.lower() or "!q!" in rd.lower():
                rrd = raw_input(">>>")
                sqlq = self._qengine.Ex(rrd).compile()
                self.execute(sqlq)
                # do the ting here
            elif "!look!" in rd.lower() or "!l!" in rd.lower():

                pass # todo
            elif "!hive!" in rd.lower() or "!h!" in rd.lower():
                #"10.164.76.246", 8888, 'hive', paswd=None
                conn = raw_input("IP:PORT:USER:PASS>")
                try:
                    conn = conn.split(":")
                except:
                    print "Invalid format!"
                    continue
                if len(conn) < 3:
                    continue
                elif len(conn) == 3:
                    self.Hive(str(conn[0]), int(conn[1]), str(conn[2]).rstrip("\r").strip("\n"), None)
                elif len(conn) == 4:
                    self.Hive(conn[0], int(conn[1]), str(conn[2]).rstrip("\r").strip("\n"), str(conn[3]).rstrip("\r").strip("\n"))
                else:
                    print "Error in HIVE"
                    continue
            elif "!postgre!" in rd.lower() or "!p!" in rd.lower():
                pass
            else:
                print "Unknown command. Type '!help!' to view commands."
    


def reslove_args():
    class _A:
        def __init__(self):
            self.ip, self.host, self.port, self.passwd, self.user = (None, None, None, None, None)

    a = _A()
    a
    pass

            


############################################################################################################################
#App:


if __name__ == "__main__":

    ip, port, user, passwd = None, None, None, None 

    if G_IMODE is False:
        #test query 
                    #.And("(identifiers like '%10.20.30.40%'")           \
            #.Or("identifiers like '%10.242.50.240%')")          \

        app = AppCtx()
        app.Hive("10.164.76.246",8888,'hive', None)
        app.QE().Select("*", "kafka_events_12")                 \
            .Ex(" where product_type = 'VOIP'")                 \
            .And("topic = 'mcapi.avro.pri.decoded'")            \
            .Ex(" order by start_time desc limit 50")           \
            .compile()
        
        #for query kafka_events_*
        app.execute(str(app.QE()))

        for d in app.jdata():
            app.delimit()
            app.writepretty(d.call_id(), "CallID:\t")
            nameonstorage = d.name_on_storage()
            fileonstorage = d.path_on_storage()
            ip_access_network = d.ip_acces_nw()
            ip_connections = d.ip_connections()
            for i in nameonstorage:
                app.writepretty(i, "Name on storage:\t")
            for j in fileonstorage:
                app.writepretty(j, "File on storage:\t")
            app.writepretty(d.participants(), "Participants:\t")
            for k in ip_access_network:
                app.writepretty(k)
            for h in ip_connections:
                app.writepretty(h)

            app.delimit()
        pass
    else:
        app = AppCtx()        
        app.run()
