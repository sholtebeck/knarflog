# Get OWGR Results
from bs4 import BeautifulSoup
import simplejson as json
import urllib2

# Get Players from File
#names = [line.strip() for line in open("players.txt", 'r')]
def xstr(string):
    if string is None:
        return None 
    elif string.isdigit():
        return int(string)
    else:
        return str(string.encode('ascii','ignore').strip())

# get_picks (currently static: implement as a service)
def get_picks():
    picks={
    'Adam Scott': 'Steve', 'Bill Haas': 'Steve', 'Billy Horschel': 'Steve', 'Brandt Snedeker': 'Mark', 
    'Bubba Watson': 'Steve', 'Charl Schwartzel': 'Mark', 'Dustin Johnson': 'Steve', 'Ernie Els': 'Mark',
    'Graeme McDowell': 'Mark', 'Harris English': 'Mark', 'Jason Day': 'Steve', 'Jason Dufner': 'Mark', 
    'Jim Furyk': 'Mark', 'Jimmy Walker': 'Steve', 'John Senden': 'Mark', 'Jonas Blixt': 'Steve',
    'Jordan Spieth': 'Steve', 'Justin Rose': 'Mark', 'Keegan Bradley': 'Mark', 'Lee Westwood': 'Steve', 
    'Louis Oosthuizen': 'Steve', 'Luke Donald': 'Mark', 'Matt Every': 'Steve', 'Matt Jones': 'Steve', 
    'Matt Kuchar': 'Mark', 'Patrick Reed': 'Mark', 'Phil Mickelson': 'Mark', 'Rickie Fowler': 'Mark', 
    'Rory McIlroy': 'Steve', 'Sergio Garcia': 'Mark', 'Stephen Gallacher': 'Steve', 'Steve Stricker':'Steve',
    'Tiger Woods': 'Steve','Webb Simpson': 'Mark', 'Zach Johnson': 'Steve'
    }
    return picks

def get_rank(position):
    if not position or not position.replace('T','').isdigit():
        return 0
    else:
        rank = int(position.replace('T',''))
        return rank

# soup_results -- get results for a url
def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup


def event_headers(soup):
    headers={}
    if soup.title.string:
        headers['title']=str(soup.title.string)
    headers['url']=str(soup.find('form').get('action'))
    headers['id']=headers['url'].split('=')[1]
    headers['name']=str(soup.find('h2').string)
    headers['time']=str(soup.find('time').string)
    headers['week']=headers['time'][-2:]
    headers['columns']=[str(column.string) for column in soup.find('thead').findAll('th')]
    return headers

def event_results(row, keys):
    values=[xstr(td.string) for td in row.findAll('td')]
    event=dict(zip(keys,values))
    if row.find(id="ctl5"):
        event['url']=str(row.find(id="ctl5").find('a').get('href'))
        event['event_id']=int(event.get('url').rsplit('=')[-1])
    event['Points']=int(event.get("Winner's Points",0))
    return event

def player_rankings(row):
    name = row.find('a')
    cols = row.findAll('td')
    player={}
    if name and len(cols)>=10:
        player_name=xstr(name.string)
        player={'Rank': int(cols[0].text), 'Name': player_name }
        player['Ctry']= str(cols[3].img.get('title'))
        player['Avg']=float(cols[5].text)
        player['Total']=float(cols[6].text)
        player['Events']=int(cols[7].text)
        player['Points']=float(cols[9].text) 
    return player

def player_results(row, keys):
    values=[xstr(td.string) for td in row.findAll('td')]
    player=dict(zip(keys,values))
    player['Rank']=get_rank(str(player.get('Pos')))
    player['Ctry']=str(row.find('img').get('title'))
    player['ID']=int(row.find('a').get('href').rsplit('=')[-1])
    player['Points']=float(player.get('Ranking Points',0))
    return player

def get_rankings():
    skip_picks=get_picks()
    ranking_url="http://www.owgr.com/ranking"
    page=soup_results(ranking_url)
    rankings=[]
    for row in page.findAll('tr')[:50]:
        player=player_rankings(row)
        if player.get('Name') in skip_picks.keys():
            player['Picker']=skip_picks[player.get('Name')]
            rankings.append(player)
    return rankings

def get_results(event_id):
    url='http://www.owgr.com/en/Events/EventResult.aspx?eventid='+str(event_id)
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    headers=event_headers(soup)
    keys=headers.get('columns')
    players=[headers]
    for row in soup.findAll('tr'):
        name = row.find('td',{'class': "name"})
        if name and name.string:
            player=player_results(row,keys)
            if player.get('Points')>0:
                players.append(player)
    return players

def get_majors(year):
    url='http://www.owgr.com/en/Events.aspx?year='+str(year)
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    headers=event_headers(soup)
    keys=headers.get('columns')[:6]
    events=[]
    for row in soup.findAll('tr'):
        if row.find(id="ctl5"):
            event=event_results(row,keys)
            if event.get("Points",0)>99:
                 events.append(event)
    return events

def write_majors(year):
    events=get_majors(year)
    for event in events:
        print event.get('event_id'), event.get('Event Name')
        results=get_results(event.get('event_id'))
        event['Results']=results
    json.dump(events,open(str(year)+'.json','wb'))

    


