#!venv/bin/python
#coding:utf-8

import sys
import os
from flask import Flask, session, redirect, url_for, escape, request, jsonify, \
    render_template
import json
from datetime import datetime
from app import db, models
from werkzeug import secure_filename


UPLOAD_FOLDER = sys.path[0] + '/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'c', 'cpp'])
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'titile': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/return/tcourses', methods=['GET'])
def return_courses():
    return jsonify({'tcourses': session['tcourses']})
    return jsonify({'tcourses': [{'tname':'wang',
                                 'cname':'english',
                                 'ctime':'111',
                                 'cid':'2'
                                  }]})


@app.route('/return/cstudents', methods=['GET'])
def return_cstudents():
    return jsonify({'cstudents': session['cstudents']})


@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tname = request.form['tname']
        password = request.form['password']
        teacher = models.Teacher.query.filter_by(tname=tname).first()
        session['tcourses'] = []
        session['tname'] = tname

        if teacher == None:
            print("teacher doesn't exist")
            return jsonify({'tcourses': [{
                'status':'no',
                'message':"The Teacher doesn't exist."
            }]})
        if teacher.password != password:
            print("password error")
            return jsonify({'tcourses': [{'status':'no',
                                          'message':"The password is error."
            }]})
        session['tcourses'].append({
            'status':'yes',
            'message':'login success.'
        })
        tcourses = models.Course.query.filter_by(tid=teacher.tid)
        for tc in tcourses:
            session['tcourses'].append({
                'cid':   tc.cid,
                'cname': tc.cname,
                'ctime': tc.ctime,
                'cstunum': tc.cstunum,
                'tname': tname
            })
        return jsonify({'tcourses': session['tcourses']})
        # return redirect(url_for('return_courses'))
    return '''
        <form action="" method="post">
            <p>姓名<input type=text name=tname>
            <p>密码<input type=text name=password>
            <p><input type=submit value=登陆>
        </form>
    '''

@app.route('/get_cstudents', methods=['GET', 'POST'])
def get_cstudents():
    if request.method == 'POST':
        session['cstudents'] = []

        if request.form['cid']:
            cid = request.form['cid']
            course = models.Course.query.filter_by(cid=cid).first()
        elif request.form['cname']:
            cname = request.form['cname']
            course = models.Course.query.filter_by(cname=cname).first()


        if course == None:
            print("The Course id isn't exist.")
            return jsonify({'cstudents': [{
                'status': 'no',
                'message': "The Course id isn't exist."
            }]})

        cstudents = models.SCourse.query.filter_by(cid=course.cid)
        if cstudents.first() == None:
            print("There is no one in the Course.")
            return jsonify({'cstudents': [{
                'status':'no',
                'message':"There is no one in the Course."
            }]})

        session['cstudents'].append({
            'status': 'yes',
            'message': 'Get students successful.'
        })
        for cs in cstudents:
            student = models.Student.query.filter_by(sid=cs.sid).first()
            session['cstudents'].append({
                'sid': student.sid,
                'sname': student.sname,
                'sclass': student.sclass,
                'surl': student.surl,
                'cname': course.cname
            })
        print(session['cstudents'])
        return jsonify({'cstudents': session['cstudents']})
        # return redirect(url_for('return_cstudents'))
    return '''
        <form action="" method="post">
            <p>课程cid<input type=text name=cid>
            <p><input type=submit value=提交>
        </form>
    '''

@app.route('/post_attendances', methods=['GET', 'POST'])
def post_attendances():
    if request.method == 'POST':
        jsonData = json.loads(request.form['data'])
        for d in jsonData['attendances']:
            attendance = models.Attendance(sid=d['sid'], cid=d['cid'], aresult=d['aresult'])
            db.session.add(attendance)
        db.session.commit()
        return 'commit successful'
        # return json.dumps(jsonData["attendances"])
    return '''
        <form action="" method="post">
            <p>学生编号<input type=text name=sid>
            <p>课程编号<input type=text name=cid>
            <p>考勤时间<input type=text name=atime>
            <p>考勤结果<input type=text name=aresult>
            <p><input type=submit value=提交>
        </form>
    '''


@app.route('/post_attendance', methods=['GET', 'POST'])
def post_attendance():
    if request.method == 'POST':
        sid = request.form['sid']
        cid = request.form['cid']
        # atime = request.form['atime']
        aresult = request.form['aresult']
        if sid == '' or cid == '' or aresult == '':
            return 'commit incomplete.'
            return jsonify({'response': [{
                'status':'no',
                'message':"commit incomplete."
            }]})

        student = models.Student.query.filter_by(sid=sid).first()
        if student == None:
            print("The student doesn't exist.")
            return jsonify({'response': [{
                'status':'no',
                'message':"The student doesn't exist."
            }]})

        course = models.Course.query.filter_by(cid=cid).first()
        if course == None:
            print("The course doesn't exist.")
            return jsonify({'response': [{
                'status':'no',
                'message':"The course doesn't exist."
            }]})

        attendance = models.Attendance(sid=sid, cid=cid, aresult=aresult)
        db.session.add(attendance)
        db.session.commit()
        return jsonify({'response': [{
            'status':'yes',
            'message':"commit successful."
        }]})
    return '''
        <form action="" method="post">
            <p>学生编号<input type=text name=sid>
            <p>课程编号<input type=text name=cid>
            <p>考勤时间<input type=text name=atime>
            <p>考勤结果<input type=text name=aresult>
            <p><input type=submit value=提交>
        </form>
    '''


@app.route('/attendances/today', methods=['GET', 'POST'])
def lastday():
    if request.method == 'POST':
        session['today'] = []
        tname = request.form['tname']
        teacher = models.Teacher.query.filter_by(tname=tname).first()
        courses = models.Course.query.filter_by(tid=teacher.tid).all()
        if courses is None:
            session['today'].append({
                'status':'no',
                'message':"There is no Course."
            })
        else:
            session['today'].append({
                'status':'yes',
                'message':"There has Course."
            })
        for course in courses:
            cid = course.cid
            timenow = datetime.now()
            today = datetime(timenow.year, timenow.month, timenow.day)

            # records = models.Attendance.query.filter(models.Attendance.atime.between(timenow-timedelta(seconds=100), timenow)).all()
            records = models.Attendance.query.filter(models.Attendance.atime.between(today, timenow)).all()
            for each in records:
                if each.cid == cid:
                    student = models.Student.query.filter_by(sid=each.sid).first()
                    course = models.Course.query.filter_by(cid=each.cid).first()
                    session['today'].append({
                        'aresult': each.aresult,
                        'cname': course.cname,
                        'sclass': student.sclass,
                        'sname': student.sname,
                        'atime': str(each.atime.strftime('%Y-%m-%d %H:%M:%S'))[2:]
                    })
        # print(session['today'])
        return jsonify({'today': session['today']})

@app.route('/attendances/course', methods=['GET', 'POST'])
def course():
    if request.method == 'POST':
        session['course'] = []
        cname = request.form['cname']
        course = models.Course.query.filter_by(cname=cname).first()
        attendances = models.Attendance.query.filter_by(cid=course.cid).all()

        if attendances is None:
            session['course'].append({
                'status':'no',
                'message':"There is no attendance."
            })
        else:
            session['course'].append({
                'status':'yes',
                'message':"There has attendance."
            })
        for each in attendances:
            student = models.Student.query.filter_by(sid=each.sid).first()
            session['course'].append({
                'aresult': each.aresult,
                'cname': course.cname,
                'sclass': student.sclass,
                'sname': student.sname,
                'atime': str(each.atime.strftime('%Y-%m-%d %H:%M:%S'))[2:]
            })
        return jsonify({'course': session['course']})


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return '''
                上传成功
            '''
            return redirect(url_for('uploaded_file',filename=filename))
    return render_template('upload_file.html')
    '''
    <!doctype html>
    <title>请提交Excel表</title>
    <h1>请提交Excel表</h1>
    <img src="{{ url_for('static', filename='images/Course.png') }}">
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

app.secret_key = '\xf7c\xcaoVe2\x10j\xff\xe3\xca\xfc\xf1\xac\x1c5a\xa6\xd0lK\xe1\xba'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
