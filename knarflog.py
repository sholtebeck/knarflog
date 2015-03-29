# Get OWGR Results
from time import gmtime,strftime
import urllib2
# External modules (bs4)
import json,csv,sys
sys.path[0:0] = ['lib']
from bs4 import BeautifulSoup
MAXPICKS=12
pickers=(u'Mark',u'Steve')
points={}
picks={}

# Handler for string values to ASCII or integer
def xstr(string):
    if string is None:
        return None 
    elif string.isdigit():
        return int(string)
    else:
        return string.encode('ascii','ignore').strip()

def get_value(string):
    try:
        value=float(string)
    except:
        value=0.0
    return value

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

def last_week():
    this_week=strftime("%y%U",gmtime())
    return str(int(this_week)-1)

# soup_results -- get results for a url
def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup

# get_field (loaded from api)
def get_players():
    players=[]
    players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=A2%3AF100&output=csv"
    result = urllib2.urlopen(players_url)
    reader = csv.reader(result)
    rownum = 0
    for row in reader:
        if row:
            rownum += 1
            player={'rownum':rownum }
            player['rank']=int(row[0])
            player['name']=row[1]
            player['points']=int(row[2].replace(',','').replace('-','0'))
            player['hotpoints']=int(row[3].replace(',','').replace('-','0'))
            player['odds']=int(row[4])
            if int(row[5])>0:
                player['picked']=True
            else:
                player['picked']=False
            players.append(player)
    return players

# get_picks (loaded from api)
def get_picks():
    url="http://knarflog.appspot.com/api/picks"
    picks=json_results(url).get('picks')
    points=get_points()
    # initialize counter for each user
    for picker in pickers:
        for player in picks[picker][u'Picks']:
            picks[player]={'Picker': picker, 'Points': points.get(player) }
        picks[picker]={'Name':picker,'Count':0,'Points':points.get(picker),'Picks':[],'Week':0 }
    return picks

def get_picker_results(results):
    picker_results={}
    for picker in pickers:
        picker_results[picker]={'Name':picker,'Count':0,'Points':0 }
    for result in results:
        for player in result['Results']:
            picker=player.get('Picker')
            if picker:
                picker_results[picker]['Count']+=1
                picker_results[picker]['Points']+=player['Points']
    return picker_results

# Get the totals for last week
def get_points():
    url="http://knarflog.appspot.com/api/rankings/"+last_week()
    rankings=json_results(url)
    # initialize counter for each user
    for picker in rankings['pickers']+rankings['players']:
        if picker.get('Name'):
            points[picker['Name']]=picker.get('Points')
    return points    
    
def get_rank(position):
    if not position or not position.replace('T','').isdigit():
        return 0
    else:
        rank = int(position.replace('T',''))
        return rank

def event_headers(soup):
    headers={}
    if soup.title.string:
        headers['title']=str(soup.title.string)
    headers['url']=str(soup.find('form').get('action'))
    if headers['url'].find('=')>0:
        headers['id']=headers['url'].split('=')[1]
    headers['name']=str(soup.find('h2').string)
    headers['date']=str(soup.find('time').string)
    headers['Week']=headers['name'][-2:]
    headers['columns']=[xstr(column.string) for column in soup.find('thead').findAll('th')]
    return headers

def event_results(row, keys):
    values=[xstr(td.string) for td in row.findAll('td')]
    event=dict(zip(keys,values))
    if row.find(id="ctl5"):
        event['url']=str(row.find(id="ctl5").find('a').get('href'))
        event['ID']=int(event.get('url').rsplit('=')[-1])
    event['Points']=int(event.get("Winner's Points",0))
    return event

def player_rankings(row):
    name = row.find('a')
    cols = row.findAll('td')
    player={}
    if name and len(cols)>=10:
        player_name=xstr(name.string)
        player={'Rank': int(cols[0].text), 'Name': player_name }
        player['ID']=int(row.find('a').get('href').rsplit('=')[-1])
        player['Ctry']= xstr(cols[3].img.get('title'))
        player['Avg']=round(get_value(cols[5].text),2)
        player['Total']=round(get_value(cols[6].text),2)
        player['Events']=int(cols[7].text)
        player['Points']=get_value(cols[9].text) 
        player['Week']=player['Points']-points.get(player_name,0)
    return player

def player_results(row, keys):
    values=[xstr(td.string) for td in row.findAll('td')]
    player=dict(zip(keys,values))
    player['Rank']=get_rank(str(player.get('Pos')))
    player['Ctry']=str(row.find('img').get('title'))
    player['ID']=int(row.find('a').get('href').rsplit('=')[-1])
    player['Points']=float(player.get('Ranking Points',0))
    return player

def get_player(player_id):
    return None

def get_rankings():
    picks=get_picks()
    picks['Available']={'Count':0, 'Picks':[] }
    ranking_url="http://www.owgr.com/ranking"
    soup=soup_results(ranking_url)
    rankings=[event_headers(soup)]
    for row in soup.findAll('tr'):
        player=player_rankings(row)
        player_name=player.get('Name')
        if player_name in picks.keys():
            picker=picks[player_name]['Picker']
            player['Week']=player['Points']-picks[player_name]['Points']
            player['Picker']=picker
            player['Pickno']=picks[picker]['Count']
            if picks[picker]['Count']<MAXPICKS:
                picks[picker]['Picks'].append(player_name)
                picks[picker]['Count']+=1
                picks[picker]['Week']+=player['Week']
                picks[picker]['Points']+=player['Week']
        else:
            if player_name:
                picks['Available']['Picks'].append(player_name)
                picks['Available']['Count']+=1 
        if player and player_name:          
            rankings.append(player)
    # append totals to the end
    rankings.append({key:value for key,value in picks.iteritems() if key in pickers})
    picks['Available']['Picks'].sort()
    rankings[-1]['Available']=picks['Available']
    return rankings

def get_results(event_id):
    picks=get_picks()
    event_url='http://www.owgr.com/en/Events/EventResult.aspx?eventid='+str(event_id)
    soup=soup_results(event_url)
    headers=event_headers(soup)
    keys=headers.get('columns')
    players=[]
    for row in soup.findAll('tr'):
        name = row.find('td',{'class': "name"})
        if name and name.string:
            player=player_results(row,keys)
            if player.get('Name') in picks.keys():
                player_name=player['Name']
                picker=picks[player_name]['Picker']
                player['Picker']=xstr(picker)
                players.append(player)
    return players

def get_events(week_id):
    week=week_id % 100
    year=2000 + int(week_id/100)
    events_url='http://www.owgr.com/en/Events.aspx?year='+str(year)
    soup = soup_results(events_url)
    headers=event_headers(soup)
    keys=headers.get('columns')[:6]
    events=[]
    for row in soup.findAll('tr'):
        if row.find(id="ctl5"):
            event=event_results(row,keys)
            if event.get("Week",0)==week:
                 results=get_results(event['ID'])
                 if results:
                     event['Results']=results
                     events.append(event)
    return events

