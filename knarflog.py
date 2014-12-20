# Get OWGR Results
import urllib2
# External modules (bs4)
import json
import sys
sys.path[0:0] = ['lib']
from bs4 import BeautifulSoup
pickers=(u'Mark',u'Steve')

# Handler for string values to ASCII or integer
def xstr(string):
    if string is None:
        return None 
    elif string.isdigit():
        return int(string)
    else:
        return string.encode('ascii','ignore').strip()

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

# soup_results -- get results for a url
def soup_results(url):
    page=urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())
    return soup

# get_picks (loaded from api)
def get_picks():
    url="http://knarflog.appspot.com/api/picks"
    picks=json_results(url).get('picks')
    # initialize counter for each user
    for picker in pickers:
        for player in picks[picker][u'Picks']:
            picks[player]=picker
        picks[picker]={'Name':picker,'Count':0,'Points':0,'Picks':[],'Total':0 }
    return picks

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
        player['Avg']=round(float(cols[5].text),2)
        player['Total']=round(float(cols[6].text),2)
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
            picker=picks[player_name]
            player['Picker']=picker
            player['Pickno']=picks[picker]['Count']
            if picks[picker]['Count']<15:
                picks[picker]['Picks'].append(player_name)
                picks[picker]['Count']+=1
                picks[picker]['Total']+=int(player['Total']+0.5)
                picks[picker]['Points']+=int(player['Points']+0.5)
        else:
            if player_name:
                picks['Available']['Picks'].append(player_name)
                picks['Available']['Count']+=1 
        if player and player_name:          
            rankings.append(player)
    # append totals to the end
    rankings.append({key:value for key,value in picks.iteritems() if key in picks.values()})
    picks['Available']['Picks'].sort()
    rankings[-1]['Available']=picks['Available']
    return rankings

def get_results(event_id):
    event_url='http://www.owgr.com/en/Events/EventResult.aspx?eventid='+str(event_id)
    soup=soup_results(event_url)
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
    events_url='http://www.owgr.com/en/Events.aspx?year='+str(year)
    soup = soup_results(events_url)
    headers=event_headers(soup)
    keys=headers.get('columns')[:6]
    events=[]
    for row in soup.findAll('tr'):
        if row.find(id="ctl5"):
            event=event_results(row,keys)
            if event.get("Points",0)>99:
                 events.append(event)
    return events

#def write_majors(year):
#    events=get_majors(year)
#    for event in events:
#        print event.get('event_id'), event.get('Event Name')
#        results=get_results(event.get('event_id'))
#        event['Results']=results
#    json.dump(events,open(str(year)+'.json','wb'))

    


