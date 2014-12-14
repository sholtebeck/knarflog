from flask import Flask, jsonify, render_template, redirect, request
from google.appengine.api import memcache, users
import knarflog,datetime,json,models

app = Flask(__name__)
app.config['DEBUG'] = True
default_url='/app/index.html'

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def logon_info():
    # check for login
    names={'sholtebeck':'Steve','mholtebeck':'Mark'}
    log={'nickname':'guest', 'url_link':users.create_login_url(request.url), 'url_title': 'Login' }
    if users.get_current_user():
        log['nickname']=nickname=users.get_current_user().nickname()
        log['name'] = names.get(nickname,nickname)
        log['url_link'] = users.create_logout_url(request.url)
        log['url_title'] = 'Logout'
    return log 

# Routine to fetch the information
def getRankings(week_id=models.current_week()):
    rankings = memcache.get('rankings')
    if rankings:
        models.put_rankings(rankings)        
    if not rankings:
        rankings = models.get_rankings(week_id)
    if not rankings:
        rankings=knarflog.get_rankings()
        models.put_rankings(rankings)
    memcache.add('rankings', rankings)
    return rankings   

def getPicks():
    rankings = getRankings()
    if rankings:
        picks=rankings[-1]
    else:
        picks=knarflog.get_picks()
    return picks   

@app.route('/')
def hello():
    """Redirect to default url"""
    return redirect(default_url, code=302)

@app.route('/about')
def about():
    return render_template('about.html', title='about', log=logon_info())

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
def api_rankings():
    rankings = getRankings()
    return jsonify({'headers': rankings[0],'players': rankings[1:100], 'pickers': rankings[-1].values() })
    
@app.route('/api/user', methods=['GET'])
def get_user():
    current_user=logon_info()
    #hack to fix the caller url to redirect to the default page
    current_user['url_link']=current_user['url_link'].replace('/api/user',default_url)
    return jsonify({'user':current_user })
    

@app.route('/rankings')
def ranking():
    picks=getRankings()[-1].get('Mark')
    return render_template('ranking.html', title='ranking', pick=picks, log=logon_info())

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

