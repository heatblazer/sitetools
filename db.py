import json

class dbutil(object):

    def __init__(self):
        """init db and load it"""
        self._db = None
        self._fname = None


    def __del__(self):
        pass


    def load(self, fname):
        self._fname = fname
        try:
            with open(fname, 'r') as fp:
                self._db = json.load(fp)    
                fp.close()
                return True
        except:
            return False
        pass

    
    def dumpall(self):
        if self._db is not None:
            for record in self._db:
                print str("%s:%s" % (record, self._db[record]))


    def lsession(self):
        if self._db is not None:
            for rec in self._db:
                print rec


    def add_session(self, name):
        if self._db is not None:
            if name not in self._db:
                self._db[name] = {'session' : {'login': None, 'queries' : []}}



    def add_login(self, name, login):
        if self._db is not None and name in self._db:
            self._db[name]['session']['login'] = login



    def add_query(self, name, query):
        if self._db is not None and name in self._db:
            self._db[name]['session']['queries'].append(query)


    def get_login(self, name):
        if self._db is not None and name in self._db:
            return self._db[name]['session']['login']
        return None


    def get_query_at(self, name, idx):
        if self._db is not None and name in self._db:
            q = None
            try:
                q = self._db[name]['session']['queries'][idx]
            except:
                pass
            return q


    def get_all_sessions_cnt(self):
        if self._db is not None:
            for q in self._db:
                print str("session: %s : queries %s" % (q, self.get_queries_count(q)))


    def get_queries_count(self, name):
        if self._db is not None and name in self._db:
            return len(self._db[name]['session']['queries'])
        return -1


    def get_top_query(self, name):
        return self.get_query_at(name, 0)



    def get_bottom_query(self, name):
            return self.get_query_at(name, -1)



    def save(self):
        try:
            with open(self._fname, 'w') as fp:
                json.dump(self._db, fp, skipkeys=False, ensure_ascii=True, check_circular=True,allow_nan=True, cls=None, indent=2, separators=None,encoding='utf-8', default=None, sort_keys=False)
                fp.close()
                return True
        except:
            return False
        pass


    def fname(self):
        return self._fname

if __name__ == "__main__":
    #unit test
    

    db = dbutil()
    db.load('db.json')
    
    if False:
        db.add_session('session2')
        db.add_login('session2', "10.164.222.222:ilian:hive")
        for i in range(0, 10):
            db.add_query('session2', str("select * from %s where NMP=NMG" % i))


        db.dumpall()
        db.save()

    if True:
        db.lsession()

        print "Queries in 'session2'",  db.get_queries_count('session2')
        #db.dumpall()
        #print db.get_bottom_query('session2')


    r'''
    db.add_record('Infra')
    db.add_record('Sau')
    db.add_svnrev('Infra', 99999)
    db.add_svnrev('Sau', 88888)
    for i in range(1, 10):
        db.add_tag('Sau', i)
        db.add_tag('Infra', i)

    db.printme()
    db.savedb()
    '''