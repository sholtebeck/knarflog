from flask import Flask, jsonify, render_template, request
from google.appengine.api import memcache, users
import knarflog

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def log_inorout():
    # check for login
    log={'user':'dude', 'url':users.create_login_url(request.url), 'url_link': 'Login' }
    if users.get_current_user():
        log['user'] = users.get_current_user().nickname()
        log['url'] = users.create_logout_url(request.url)
        log['url_link'] = 'Logout'
    return log 

# Routine to fetch the information
def getPicks():
    rankings = memcache.get('rankings')
    if rankings:
        picks=rankings[-1]
    else:
        picks=knarflog.get_picks()
    return picks   

def getRankings():
    rankings = memcache.get('rankings')
    if not rankings:
        rankings=knarflog.get_rankings()
        memcache.add('rankings', rankings)
    return rankings   

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return render_template('hello.html', title='hello', log=log_inorout())

@app.route('/about')
def about():
    return render_template('about.html', title='about', log=log_inorout())

@app.route('/api/picks', methods=['GET'])
def picks():
    return jsonify({'picks': getPicks()})

@app.route('/api/picks/<pick_key>', methods=['GET'])
def get_pick(pick_key):
    pick = getPicks().get(pick_key)
    if not pick or len(pick) == 0:
        abort(404)
    return jsonify({pick_key: pick})

@app.route('/api/rankings', methods=['GET'])
def rankings():
    rankings = getRankings()
    return jsonify({'headers': rankings[0],'players': rankings[1:50], 'pickers': rankings[-1].values() })

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

