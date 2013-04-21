#!/usr/bin/env python2

import flask
import werkzeug.serving
import json

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()

from flask import Flask, request, Response, render_template, redirect

from swamp_db import DB

app = Flask(__name__)

# count number of updates, resend iff the event source hasnt seen the most recent update
nupdates = 0

encoder = json.JSONEncoder()

def update():
    db = DB()
    names = db.getNames()
    aj = { 'names' : names, 'measures' : {}, 'today' : {}, 'simple':'',
           'current' : {}, 'status' : {} }
    for n in names:
        aj['measures'][n] = db.nMeasures(n)
        aj['today'][n] = db.nToday(n)
        aj['current'][n] = db.currentTime(n)
        aj['status'][n] = db.status(n)
    return encoder.encode(aj)

def subscription():
    mseen = -1
    try:
        while True:
            gevent.sleep(1)
            while nupdates >  mseen:
                print "Sending msg"
                yield "data: %s\n\n" % update()
                mseen = nupdates
    except:
        print "A connection dropped"
            
@app.route('/subscribe')
def sse_request():
    return Response(subscription(), mimetype = 'text/event-stream')

@app.route('/status', methods=['POST'])
def status():
    global nupdates
    db=DB()
    name = request.args.get("name")
    status = request.args.get("status")
    print 'status update', name, status
    db.updateStatus(name, status)
    nupdates += 1
    return ""

@app.route('/login', methods=['POST'])
def login():
    global nupdates
    name = request.args.get("name")
    db = DB()
    if name not in db.getNames():
        db.addUser(name)
        nupdates += 1
    return ""

def admin_clear():
    global nupdates
    db = DB()
    db.clearCurrent()
    nupdates += 1

def admin_add(name, start, end):
    global nupdates
    db = DB()
    db.addMeasure(name, start.strip(), end.strip())
    nupdates += 1
    
@app.route('/admin', methods=['POST'])
def admin_post():
    func = request.args.get("func")
    print 'Recieved message', func
    if func == 'clear':
        admin_clear()
    elif func == 'add':
        admin_add(request.args.get("name"), request.args.get("start"), request.args.get("end"))
    else:
        print "Unknown admin command:", func
    return ""
    
@app.route('/admin', methods=['GET'])
def admin_main():
    return render_template('admin.html')
    
@app.route('/')
def index():
    return render_template('main.html')

# @werkzeug.serving.run_with_reloader
def runserver():
    http_server = WSGIServer(('0.0.0.0', 8001), app)
    http_server.serve_forever()

import threading

def timer():
    global nupdates
    t=threading.Timer(1.0, timer)
    t.start()
    dbUpdate = DB().statusTick()
    if dbUpdate:
        nupdates += 1

if __name__ == '__main__':
    # initial setup. clear the current status'
    db = DB()
    db.db.execute('update current set status=0;')
    db.db.commit()
    timer()
    runserver()
