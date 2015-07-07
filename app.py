from bson import ObjectId
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.( db name )
app = Flask(__name__)
page = 0
page_end = 15


@app.route('/next')
def next_page():
    global page, page_end
    page += 15
    page_end += 15
    results = list(db.logs.find())
    last = results[page:page_end]
    objects = []


    for i in last:
        item = {}
        item['time'] = i.get('timestamp')
        item['username'] = i.get('username')
        item['url'] = i.get('url')
        item['id'] = i.get('_id')
        objects.append(item)
    return render_template('index.html', objects=objects, last=last)


@app.route('/')
def home_page():
    results = list(db.logs.find())
    last = results[page:page_end]
    objects = []

    for i in last:
        item = {}
        item['time'] = i.get('timestamp')
        item['username'] = i.get('username')
        item['url'] = i.get('url')
        item['id'] = i.get('_id')
        objects.append(item)
    return render_template('index.html', objects=objects, last=last)


@app.route('/detail/<id>')
def detail(id):
    return render_template('detail.html', id=id)

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
                   remoteip = data['remote_ip']
                   )


if __name__ == '__main__':
    app.debug = True
    app.run()
