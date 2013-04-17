#!/usr/bin/env python2

import os
from bottle import Bottle, run, static_file, request, template, redirect
import sqlite3
import time

app = Bottle()

dbName = "db"

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
    
    def __init__(self):
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
            self.db.execute('insert into current values (?,?,?)', (self.userId(name),0,1))
        if newTime > measureLength:
            self.db.execute('delete from current where userId=?', (self.userId(name),))
            self.db.execute('insert into measures values (?,?,?,?)', (None,self.userId(name),time.ctime(time.time()-measureLength),time.ctime()))
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

    def updateStatus(self, name, status):
        try:
            self.db.execute('update current set status=? where userId=?', (status, self.userId(name),))
        except:
            pass

    def status(self, name):
        try:
            return int(self.db.execute('select status from current where userId=?', (self.userId(name),)).fetchone()[0]) == 1
        except:
            return False

    def nToday(self, name):
        times = [a[0] for a in self.db.execute('select startTime from measures where userId=?', (self.userId(name),)).fetchall()]
        return len(filter(istoday, times))

@app.route('/')
@app.route('/main', method="GET")
def index():
    redirect('/login')

@app.route('/ajax')
def ajax():
    cname  = request.GET.get('name','')
    status = int(request.GET.get('status',''))
    db = DB()
    names = db.getNames()
    finishedMeasure = False
    if int(status) != 0:
        finishedMeasure = db.addCurrent(cname)
    db.updateStatus(cname, status)
    aj = { 'names' : names, 'measures' : {}, 'today' : {}, 'simple':'',
           'current' : {}, 'status' : {}, 'finished' : finishedMeasure }
    for n in names:
        aj['measures'][n] = db.nMeasures(n)
        aj['today'][n] = db.nToday(n)
        aj['current'][n] = db.currentTime(n)
        aj['status'][n] = db.status(n)
    return aj
    
@app.route('/main', method="POST")
def mainview():
    db = DB()
    name = request.forms.get("name")
    if name not in db.getNames():
        db.addUser(name)
    return template("\n".join(open("main.html").readlines()), name=name)
    
@app.route('/jquery.min.js')
def jq():
    return " ".join(open("jquery.min.js").readlines())
    
@app.route('/login', method="GET")
def login():
    return """
<html>
    <head><title>Swamp Thing</title></head>
    <body>
     <h1>Login</h1>
     <form method="POST" action="/main">
      Enter your name: <input type="text" name="name"></input><br>
      <input type="submit"></input>
     </form>
    </body>
</html>
    """

def summTable():
    pass

app.secret_key = 'alfbadnbjaetbea'
if __name__ == "__main__":
    run(app, host='0.0.0.0', port=9876, debug=True, reloader=True)

