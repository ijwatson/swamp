import sqlite3
import os
import time

dbDefault = "/sydpp/iwatson/db"

# length of a measure in seconds
measureLength = 30 * 60

# since the last global check
updateCount = 0
update = None

def isweek(t):
    t = time.strptime(t)
    m = time.localtime()
    

def istoday(t):
    t = time.strptime(t)
    m = time.localtime()
    return t.tm_mon == m.tm_mon and t.tm_year == m.tm_year and t.tm_mday == m.tm_mday

class DB:
    
    def __init__(self, path=None):
        dbName = path if path else dbDefault
        if not os.path.exists(dbName):
            os.system('sqlite3 %s < setup.sql' % dbName)
        self.db = sqlite3.connect('%s' % dbName)
        
    def getNames(self):
        return [a[0] for a in self.db.execute('select name from users').fetchall()]
        
    def addUser(self, name):
        self.db.execute('insert into users values (?,?)', (None, name,))
        self.db.commit()
        
    def userId(self, name):
        return self.db.execute('select id from users where name=?', (name,)).fetchone()[0]
        
    def addCurrent(self, name):
        crnt = self.db.execute('select measureTime from current where userId=?', (self.userId(name),)).fetchall()
        newTime = 0
        if len(crnt) > 0:
            newTime = 1 + crnt[0][0]
        else:
            newTime = 1
            self.db.execute('insert into current values (?,?,?,?)', (self.userId(name),0,int(status),time.ctime()))
        if newTime > measureLength:
            stime = self.db.execute('select startTime from current where userid=?',(self.userId(name),)).fetchone()[0]
            self.db.execute('delete from current where userId=?', (self.userId(name),))
            self.db.execute('insert into measures values (?,?,?,?)', (None,self.userId(name),stime,time.ctime()))
            self.db.commit()
            return True
        else:
            self.db.execute('update current set measureTime=? where userId=?', (newTime, self.userId(name)))
            self.db.commit()
            return False

    def currentTime(self, name):
        crnt = self.db.execute('select measureTime from current where userId=?', (self.userId(name),)).fetchall()
        if len(crnt) > 0:
            return crnt[0][0]
        else:
            return 0
            
    def nMeasures(self, name):
        return len(self.db.execute('select * from measures where userId=?', (self.userId(name),)).fetchall())

    def isInCurrent(self, name):
        return self.db.execute('select count(*) from current where userid=?', (self.userId(name),)).fetchone()[0] > 0
        
    def updateStatus(self, name, status):
        try:
            if self.isInCurrent(name):
                print "in current", name
                self.db.execute('update current set status=? where userId=?', (int(status), self.userId(name),))
            else:
                print "not in curr", name
                self.db.execute('insert into current values (?,?,?,?)', (self.userId(name),0,int(status),time.ctime()))
            self.db.commit()
        except:
            print "No update", name, status

    def statusTick(self):
        self.db.execute('update current set measureTime=measureTime+1 where status=1')
        self.db.commit()
        updates = False
        for name in self.getNames():
            uid = self.userId(name)
            if self.currentTime(name) > measureLength:
                stime = self.db.execute('select startTime from current where userid=?',(uid,)).fetchone()[0]
                self.db.execute('delete from current where userId=?', (uid,))
                self.db.execute('insert into measures values (?,?,?,?)', (None,uid,stime,time.ctime()))
                self.db.commit()
                updates = True
        return updates
        
    def status(self, name):
        try:
            return int(self.db.execute('select status from current where userId=?', (self.userId(name),)).fetchone()[0]) == 1
        except:
            return False

    def nToday(self, name):
        times = [a[0] for a in self.db.execute('select startTime from measures where userId=?', (self.userId(name),)).fetchall()]
        return len(filter(istoday, times))

    def clearCurrent(self):
        self.db.execute('delete from current')
        self.db.commit()

    def addMeasure(self, name, start, end):
        self.db.execute('insert into measures values (?,?,?,?)', (None,self.userId(name),start,end))
        self.db.commit()

    def getMeasures(self, name):
        m = [a[0] for a in self.db.execute('select endTime from measures where userid=?', (self.userId(name),))]
        return m
