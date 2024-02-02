from time import gmtime, strftime
from flask import Flask, abort, jsonify, make_response, request
import json
import sqlite3

app = Flask(__name__) 

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Resource not found'}), 404)

@app.route('/api/v1/info', methods=['GET'])
def home_index():
    conn = sqlite3.connect('apirelease.db')
    api_list=[] 
    cursor = conn.execute("SELECT buildtime, version, methods, links from apirelease") 
    for row in cursor: 
        a_dict = {} 
        a_dict['version'] = row[0] 
        a_dict['buildtime'] = row[1] 
        a_dict['methods'] = row[2] 
        a_dict['links'] = row[3] 
        api_list.append(a_dict) 
    conn.close() 
    return jsonify({'api_version': api_list}), 200 

@app.route('/api/v1/users', methods=['GET']) 
def get_users():
    conn = sqlite3.connect('apirelease.db')
    api_list=[]
    cursor = conn.execute("SELECT username, full_name, emailid, password, id from users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['email'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    conn.close()
    return jsonify({'user_list': api_list}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET']) 
def get_user(user_id): 
    conn = sqlite3.connect('apirelease.db') 
    api_list=[] 
    cursor=conn.execute("SELECT * from users where id=?",(user_id,)) 
    data = cursor.fetchall() 
    user = {}
    if len(data) != 0: 
        user['username'] = data[0][0] 
        user['name'] = data[0][1] 
        user['email'] = data[0][2] 
        user['password'] = data[0][3] 
        user['id'] = data[0][4] 
    conn.close() 
    return jsonify(user), 200
    
@app.route('/api/v1/users', methods=['POST']) 
def create_user(): 
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json: 
        abort(400) 
    user = { 
        'username': request.json['username'], 
        'emailid': request.json['email'], 
        'name': request.json.get('name',""), 
        'password': request.json['password'] 
    }
    conn = sqlite3.connect('apirelease.db') 
    cursor = conn.execute("SELECT * from users where username=? or emailid=?",(user['username'],user['emailid'])) 
    data = cursor.fetchall() 
    if len(data) != 0: 
        abort(409) 
    else: 
       cursor.execute("insert into users (username, emailid, password, full_name) values (?,?,?,?)",(user['username'], user['emailid'], user['password'], user['name'])) 
    conn.commit() 
    conn.close() 
    return jsonify({"status": "User created successfully"}), 201

@app.route('/api/v1/users', methods=['DELETE']) 
def delete_user(): 
    if not request.json or not 'username' in request.json: 
        abort(400) 
    user = request.json['username'] 
    conn = sqlite3.connect('apirelease.db')
    cursor = conn.execute("SELECT * from users where username=?",(user,))
    data = cursor.fetchall()
    if len(data) == 0:
      abort(409)
    else:
      cursor.execute("delete from users where username=?",(user,))
      conn.commit()
      conn.close()
    return jsonify({'status': 'User deleted successfully'}), 200
    
@app.route('/api/v1/users/<int:user_id>', methods=['PUT']) 
def update_user(user_id):
    if not request.json:
        abort(400)
    user = {
        'username': request.json.get('username',""),
        'emailid': request.json.get('email',""),
        'name': request.json.get('name',""),
        'password': request.json.get('password',""),
    }
    conn = sqlite3.connect('apirelease.db')
    cursor = conn.execute("SELECT * from users where id=?",(user_id,))
    data = cursor.fetchall()
    if len(data) == 0:
      abort(409)
    else:
      cursor.execute("update users set username=?, emailid=?, password=?, full_name=? where id=?",(user['username'], user['emailid'], user['password'], user['name'], user_id))
      conn.commit()
      conn.close()
    return jsonify({'status': 'User updated successfully'}), 200

@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
    conn = sqlite3.connect('apirelease.db')
    print ("Opened database successfully")
    api_list=[]
    cursor = conn.execute("SELECT username, body, tweet_time, id from tweets")
    for row in cursor:
        tweets = {}
        tweets['username'] = row[0]
        tweets['body'] = row[1]
        tweets['tweet_time'] = row[2]
        tweets['id'] = row[3]
        api_list.append(tweets)
    conn.close()
    return jsonify({'tweet_list': api_list}), 200

@app.route('/api/v2/tweets', methods=['POST'])
def create_tweet():
    if not request.json or not 'username' in request.json or not 'body' in request.json:
        abort(400)
    tweet = {
        'username': request.json['username'],
        'body': request.json['body'],
        'tweet_time': strftime("%Y-%m-%d %H:%M:%S", gmtime())
    }
    conn = sqlite3.connect('apirelease.db')
    cursor = conn.execute("SELECT * from users where username=?",(tweet['username'],))
    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        cursor.execute("insert into tweets (username, body, tweet_time) values (?,?,?)",(tweet['username'], tweet['body'], tweet['tweet_time']))
    conn.commit()
    conn.close()
    return jsonify({"status": "Tweet created successfully"}), 201
    
@app.route('/api/v2/tweets/<int:id>', methods=['GET']) 
def get_tweet(id):
    conn = sqlite3.connect('apirelease.db')
    api_list=[]
    cursor=conn.execute("SELECT * from tweets where id=?",(id,))
    data = cursor.fetchall()
    tweet = {}
    if len(data)==0:
        abort(404)
    else:
        tweet['username'] = data[0][0]
        tweet['body'] = data[0][1]
        tweet['tweet_time'] = data[0][2]
        tweet['id'] = data[0][3]
    conn.close()
    return jsonify(tweet), 200


if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=5000, debug=True) 
