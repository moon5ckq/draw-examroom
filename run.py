#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mlckq <moon5ckq@gmail.com>
#
# Distributed under terms of the MIT license.

import sys, random, math, os, string
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Server, Shell, Manager, prompt_bool
from flask.ext.login import login_user, logout_user, current_user, \
        login_required, LoginManager, UserMixin
from datetime import datetime

# constant.
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/db')

db = SQLAlchemy()
db.init_app(app)
db.app = app
manager = Manager(app)
manager.add_command("runserver", Server('0.0.0.0',port=8001, threaded=True))
#app.debug = True
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    user_id = db.Column(db.Text)
    passwd = db.Column(db.Text)
    idcard = db.Column(db.Text)
    province = db.Column(db.Text)
    time = db.Column(db.Text)
    exam_id_range = db.Column(db.Text, default='')
    seat_id_range = db.Column(db.Text, default='')
    exam_id = db.Column(db.Integer, default=-1)
    seat_id = db.Column(db.Integer, default=-1)
    is_drawn = db.Column(db.Integer, default=0)
    examid = db.Column(db.Text)
    exam_type = db.Column(db.Text)
  

    def __repr__(self):
        return '<User %d (%d, %d)>[%s; %s]'%(self.id, self.exam_id, self.seat_id, \
            self.exam_id_range, self.seat_id_range)


def passwd_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in xrange(size))

def get_range(value):
    v = value.split('-')
    if len(v) == 1:
        return [ int(v[0]) ]
    else:
        return range( int(v[0]), int(v[1]) + 1)

def random_assign(rset, chose):
    set2 = set()
    for i in chose[1]:
        for j in chose[2]:
            set2.add( (i, j) )
    if rset == None:
        return random.choice(list(set2))
    set2 = rset & set2
    if len(set2) == 0:
        return False
    return random.choice(list(set2))

@app.route('/')
@login_required
def index():
    if datetime(2015,6,15,12,0) > datetime.now():
        return render_template('index.html', user = current_user, info=u"抽签将于2015年6月15日，中午11点59分59秒截止", expire = False)
    else:
        return render_template('index.html', user = current_user, msg=u"抽签已经截止%s"%(u"，系统已经为您抽好签" if not current_user.is_drawn else ""), expire = True)
        

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.values.get('ok') is not None:
        try :
            username = request.values.get('username')
            password = request.values.get('password')
            user = db.session.query(User).filter(User.user_id ==  username)\
                .filter(User.passwd == password).first()
            login_user(user)
            return redirect(request.args.get("next") or url_for("index"))
        except:
            return render_template('login.html', msg=u'报名号或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/draw')
@login_required
def draw():
    current_user.is_drawn = 1
    db.session.commit()
    return jsonify({'exam_id':current_user.exam_id, 'seat_id':current_user.seat_id})

@manager.option('-d', dest='raw_data_path')
@manager.option('-r', dest='room_set')
@manager.option('-o', dest='passwd_list', default=None)
def createall(raw_data_path, room_set, passwd_list = None):
    "Creates database tables"
    db.create_all()
    rset = set()
    user_list_d = {}
    with open(room_set) as f:
        for line in f:
            u = line.strip().split(',')
            for i in get_range(u[1]):
                rset.add( (int(u[0]), i) )
    
    with open(raw_data_path) as f:
        for line in f:
            r = line.decode('utf-8').strip().split(',')
            user = User(name = r[0],\
                examid = r[1],\
                passwd = r[8],\
                idcard = r[2],\
                province = r[3],\
                time = r[4],\
                exam_id_range = r[5],\
                seat_id_range = r[6],\
                user_id =  r[7],\
                exam_type = r[9])
            db.session.add(user)
            db.session.flush()

            if r[4] not in user_list_d:
                user_list_d[ r[4] ] = []
            user_list_d[ r[4] ].append( [user.id, get_range(r[5]), get_range(r[6])] )

    db.session.commit()

    _rset = rset.copy()
    for k, user_list in user_list_d.items():
        result = {}
        _result = {}
        rset = _rset.copy()
        while len(user_list) > 0:
            u = user_list.pop(0)
            r = random_assign(rset, u)
            if r == False:
                r = random_assign(None, u)
                _id = _result[r]
                v = result[_id]
                v.pop()
                user_list.append(v)
            else:
                rset.discard( r )
            u.append(r)
            result[u[0]] = u
            _result[r] = u[0]
        for k, v in _result.items():
            user = db.session.query(User).get(v)
            user.exam_id = k[0]
            user.seat_id = k[1]
            db.session.commit()

    if passwd_list :
        with open(passwd_list, 'w') as f:
            for user in db.session.query(User).all():
                print >>f, user.user_id, user.passwd

@manager.option('-o', dest='assign_result')
def getresult(assign_result):
    "Get assign result"
    with open(assign_result, 'w') as f:
        for user in db.session.query(User).all():
            print >>f, ('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (\
                    user.name, user.examid, user.idcard, user.province,\
                    user.time, user.exam_id_range, user.seat_id_range,\
                    user.exam_id, user.seat_id, user.user_id, user.passwd,\
                    user.exam_type)).encode('utf-8')

if __name__ == '__main__':
    manager.run()
