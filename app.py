import pymongo
import csv
import os
import random
from flask import render_template, request, redirect, Flask, make_response, send_file
url = "http://localhost/?code="
app = Flask(__name__)
mongoclient = pymongo.MongoClient("mongodb://admin:!Home4514@localhost:27017/?authSource=admin&ssl=false")
db = mongoclient["Pizza"]['Pizzas']
codedb = mongoclient["Pizza"]["Codes"]


@app.route('/', methods=['GET'])
def mainpage():
    try:
        code = request.args['code']
    except:
        code = None
    if code is not None:
        return render_template('index.html', code=code, disabled='readonly="readonly"')
    return render_template('index.html', code=None, disabled="")


@app.route('/input', methods=['GET'])
def inputfunc():
    name = request.args['fname']
    pizza = request.args['dropdown']
    code = str(request.args['code'])
    exists = False
    for i in codedb.find({}):
        if str(i['code']) == code:
            exists = True
    if not exists:
        return "Error: Code does not exist. <a href='/'>Go back</a>"
    if len(name) > 10:
        return "ERROR: NAME TOO LONG! <a href='/'>Go back</a>"
    data = {"name": name, 'pizzatype': pizza, "code": str(code)}
    db.insert_one(data)
    resp = make_response(redirect('/confirmation'))
    resp.set_cookie('userID', name)
    resp.set_cookie('pizza', pizza)
    resp.set_cookie('code', code)
    return resp


@app.route('/newcode')
def newcode():
    code = random.randint(10000, 99999)
    for i in codedb.find():
        if code == i['code']:
            code = random.randint(10000, 99999)
    codedb.insert_one({'code': str(code)})
    return render_template('newcode.html', url=url, code=code)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/confirmation')
def confirmationpage():
    name = request.cookies.get('userID')
    pizza = request.cookies.get('pizza')
    return render_template('confirmation.html', name=name, pizza=pizza)


@app.route('/admin')
def adminpage():
    try:
        code = request.args['code']
    except:
        return render_template('admin.html', pep="", met="", mar="")
    mar, met, pep = 0, 0, 0
    m, p, me = db.find({'pizzatype': 'Margherita', 'code': code}), db.find({'pizzatype': 'Pepperoni', 'code': code}), db.find(
        {'pizzatype': 'Meteor', 'code': code})
    for _ in m:
        mar = mar + 1
    for _ in p:
        pep = pep + 1
    for _ in me:
        met = met + 1
    return render_template('admin.html', pep=pep, met=met, mar=mar, code=code)


@app.route('/admin/fulllist')
def showfulllist():
    code = request.args['code']
    try:
        os.remove('names.csv')
    except FileNotFoundError:
        pass
    with open('names.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Pizza']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        m, p, me = db.find({'pizzatype': 'Margherita', 'code': code}), db.find({'pizzatype': 'Pepperoni', 'code': code}), db.find(
            {'pizzatype': 'Meteor', 'code': code})
        for i in m:
            writer.writerow({'Name': i['name'], 'Pizza': i['pizzatype']})
        for i in me:
            writer.writerow({'Name': i['name'], 'Pizza': i['pizzatype']})
        for i in p:
            writer.writerow({'Name': i['name'], 'Pizza': i['pizzatype']})
    return send_file('names.csv', as_attachment=True)


@app.route('/assets/bootstrap/css/bootstrap.min.css')
def css():
    return send_file('./assets/bootstrap.min.css')


@app.route('/assets/js/grayscale.js')
def grayscale():
    return send_file('./assets/grayscale.js')


@app.route('/assets/img/intro-bg.jpg')
def bg():
    return send_file('./assets/intro-bg.jpg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')
