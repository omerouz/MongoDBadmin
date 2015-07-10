from bson import ObjectId
from flask import Flask, render_template, jsonify, url_for
from pymongo import MongoClient
from flask import request, abort
from datetime import datetime


client = MongoClient('mongodb://localhost:27017/')
db = client.chroma
app = Flask(__name__)


@app.route('/')
def home_page():
    offset = request.args.get('offset')
    if offset:
        results = list(db.logs.find({'_id': {'$lt': ObjectId(offset)}}).sort('_id', -1).limit(50))
    else:
        results = list(db.logs.find().sort('_id', -1).limit(50))

    offset_id = results[49].get('_id')
    objects = []
    for i in results:
        item = {}
        item['time'] = i.get('timestamp')
        item['username'] = i.get('username')
        item['url'] = i.get('url')
        item['id'] = i.get('_id')
        objects.append(item)
    return render_template('index.html', objects=objects, results=results, offset=offset_id)


def time_format(datetime_):
    dt = datetime.strptime(datetime_, "%Y-%m-%dT%H:%M")
    return dt


def response_(response):
    objects = []
    results = list(response)
    for i in results:
        item = {}
        item['time'] = i.get('timestamp')
        item['username'] = i.get('username')
        item['url'] = i.get('url')
        item['id'] = i.get('_id')
        objects.append(item)
    return objects


@app.route('/search/')
def search():
    if request.args.get('date_from') and not request.args.get('user'):
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        response = db.logs.find({'$and': [{'timestamp': {'$gt': time_format(date_from)}},
                                      {'timestamp': {'$lt': time_format(date_to)}}]}).sort('_id', -1)
        user = []

    elif request.args.get('user') and not request.args.get('date_from'):
        user = request.args.get('user')
        response = db.logs.find({"username": user}).sort('_id', -1)
        date_to = []
        date_from = []

    elif request.args.get('user') and request.args.get('date_from'):
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        user = request.args.get('user')
        response = db.logs.find({'$and': [{'timestamp': {'$gt': time_format(date_from)}},
                                      {'timestamp': {'$lt': time_format(date_to)}}]}).sort('username', user).sort('_id', -1)

    else:
       abort(404)

    if response:
        results = list(response)
        objects = response_(results)
        return render_template('index.html', objects=objects,
                                             has_next= len(objects),
                                             user = user,
                                             date_to=date_to,
                                             date_from=date_from)


@app.route('/detail/<id>')
def detail(id):
    return render_template('detail.html', id=id, redirect=redirect_url())

@app.route('/body/<id>')
def get_detail(id):
    data = db.logs.find_one({'_id': ObjectId(id)})
    return jsonify(
                   body=data['body'],
                   username=data['username'],
                   cookies=data['cookies'],
                   timestamp=data['timestamp'],
                   accesstoken=data['access_token'],
                   headers=data['headers'],
                   query=data['query'],
                   path =data['path'],
                   method = data['method'],
                   remoteip = data['remote_ip'])


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


if __name__ == '__main__':
    app.debug = True
    app.run()