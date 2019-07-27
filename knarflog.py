# Get OWGR Results
from time import gmtime,strftime
import datetime, urllib, urllib2
# External modules (bs4)
import json,csv,sys
sys.path[0:0] = ['lib']
from bs4 import BeautifulSoup
MAXPICKS=12
pickers=(u'Mark',u'Steve')
points={}
picks={}
debug=False

def do_debug(string):
    if debug:
        print (string)

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
        value=round(float(string),2)
    except:
        value=0.0
    return value

# json_results -- get results for a url
def json_results(url):
    page=urllib2.urlopen(url)
    results=json.load(page)
    return results

def current_week():
    this_week=strftime("%U",gmtime())
    return str(int(this_week)-1)

def current_year():
    this_week=strftime("%Y",gmtime())
    return str(int(this_week))    

def last_week():
    this_year=datetime.date.today().isocalendar()[0]%100
    this_week=datetime.date.today().isocalendar()[1]
    last_week=(this_year*100)+(this_week-2)
    return str(last_week)

# last_weeks_rankings (loaded from api)
def last_weeks_rankings():
    url="http://knarflog.appspot.com/api/rankings/"+last_week()
    rankings=json_results(url)
    lastweek={}
    ranknum=0
    for player in rankings["players"]:
        lastweek[player['Name']]={"Rank": player["Rank"], "Points": player['Points'] }
    for picker in [picker for picker in rankings["pickers"] if picker.get('Name') in pickers]:
        ranknum+=1
        lastweek[picker['Name']]={"Points": round(picker.get("Points",0.0),2), "Rank": ranknum }
    return lastweek

# last_weeks_results (from owgr home page)
def get_results():
    events=[]
    owgr_url='http://www.owgr.com/'
    soup=soup_results(owgr_url)
    last_week=[xstr(t.string) for t in soup.find_all('time') if t.string.endswith(current_year())][0].split()
    week_no = xstr(last_week[4])
    week_date = ' '.join(last_week[5:])	
    for row in soup.find_all('tr'):
        if row.find('th'):
            headers=[xstr(th.string) for th in row.find_all('th') if th.string]
            headers[0]="Event Name"			
        elif row.find('td'):
            values=[xstr(td.string) for td in row.find_all('td')]
            event={header:value for (header,value) in zip(headers,values) if value }
            if event.get('Winner') and event.get('SOF')>50:	
                urls=[u.get('href') for u in row.find_all('a')]
                event['ID']=int(max([url.rsplit('=')[-1] for url in urls if 'Event' in url]) )
                event['Week']=week_no
                event['Date']=week_date
                results=event_results(event['ID'])
                if len(results)>0:
                    event['Points']=results[0].get("Points")   
                    event['Results']=results					
                    events.append(event)
    return events
	
# this_weeks_rankings (loaded from api)
def this_weeks_rankings():
    url="http://knarflog.appspot.com/api/rankings"
    rankings=json_results(url)
    return rankings

# soup_results -- get results for a url
def soup_results(url):
    soup = None
    timeout = 2
    while not soup and timeout < 1000:
        try:  
            page=urllib2.urlopen(url,timeout=180)
            soup = BeautifulSoup(page.read())
        except:
            timeout = timeout * 2
    return soup
    
def get_bool(input):
    if input in ('true',True,1,'1'):
        return True
    else:
        return False
        
# get_field (loaded from api)
def get_event():
    events_url='https://docs.google.com/spreadsheets/d/1rb_attQJRkfOuQSeg7Qq8GoYdgorpm-oQKK60AQY8J8/pub?single=true&gid=0&range=A2:E2&output=csv'
    result = urllib2.urlopen(events_url)
    reader = csv.reader(result)
    event={}
    for row in reader:
        event['id']=row[0]
        event['name']=row[1]
        event['shortname']=row[1][5:]
        event['url']=row[2]
        event['start']=row[3]
    return event

def get_players():
    players=[]
    players_url="https://docs.google.com/spreadsheet/pub?key=0AgO6LpgSovGGdDI4bVpHU05zUDQ3R09rUnZ4LXBQS0E&single=true&gid=1&range=A2%3AF155&output=csv"
    result = urllib2.urlopen(players_url)
    reader = csv.reader(result)
    rownum = 1
    for row in reader:
        if row:
            rownum += 1
            player={'rownum':rownum }
            player['rank']=int(row[0])
            player['name']=row[1]
            player['lastname']=row[1].split(" ")[-1]
            player['points']=get_value(row[2].replace(',','').replace('-','0'))
            if len(row)>=5:           
                player['country']=row[3]
                player['odds']=get_value(row[4])
                player['picked']=int(row[5])
            else:
                player['hotpoints']=0.0
                player['odds']=999
                player['picked']=0
            players.append(player)
    return players

# get_picks (loaded from api)
def get_picks():
    url="http://knarflog.appspot.com/api/picks"
    picks=json_results(url).get('picks')
    # initialize counter for each user
    for picker in pickers:
        points=picks[picker]['Points']
        for player in picks[picker][u'Picks']:
            picks[player]={'Picker': picker, 'Points': 0.0 }
        picks[picker]={'Name':picker,'Count':0,'Points': points ,'Picks':[],'Week':0 }
    return picks

def get_weeks(year):
    weeks=[]
    return weeks

def get_picker_results(results):
    picker_results={}
    for picker in pickers:
        picker_results[picker]={'Name':picker,'Count':0,'Points':0,'Rank':1 }
    if results:
        for result in results:
            for player in result['Results']:
                picker=player.get('Picker')
                if picker:
                    picker_results[picker]['Count']+=1
                    picker_results[picker]['Points']+=player['Points']
    if (picker_results[pickers[0]]['Points']>picker_results[pickers[1]]['Points']):
        picker_results[pickers[1]]['Rank']=2
    else:
        picker_results[pickers[0]]['Rank']=2
    return picker_results
   
def get_rank(position):
    if not position or not position.replace('T','').isdigit():
        return 0
    else:
        rank = int(position.replace('T',''))
        return rank

def event_headers(soup):
    headers={}
    if soup.title.string:
        headers['title']=soup.title.string
    headers['url']=str(soup.find('form').get('action'))
    if headers['url'].find('=')>0:
        headers['id']=headers['url'].split('=')[1]
    headers['name']=soup.find('h2').string
    headers['date']=str(soup.find('time').string)
    headers['Week']=int(soup.find("span", { "class" : "week" }).string.split()[-1])
    headers['Year']=str(current_year())
#   headers['Year']=headers['date'][-4:]
    headers['week_id']=int(headers['Year'][-2:])*100+headers['Week']
#   headers['columns']=[xstr(column.string) for column in soup.find('thead').findAll('th')]
    headers['columns']=[xstr(column.string) for column in soup.findAll('th',{"class":"header"})]
    return headers

def ranking_headers(soup):
    headers={}
    if soup.title.string:
        headers['title']=soup.title.string
    headers['url']=str(soup.find('form').get('action'))
    if headers['url'].find('=')>0:
        headers['id']=headers['url'].split('=')[1]
    headers['name']=[head.string for head in soup.findAll('h2') if head.string.startswith('WEEK')][0]
    headers['date']=str(soup.findAll('time')[-1].string)
    headers['Week']=int(headers['name'][-2:])
    headers['Year']=str(current_year())
#   headers['Year']=headers['date'][-4:]
    headers['week_id']=int(headers['Year'][-2:])*100+headers['Week']
#   headers['columns']=[xstr(column.string) for column in soup.find('thead').findAll('th')]
    headers['columns']=[xstr(column.string) for column in soup.findAll('th')]
    return headers
    
def row_results(row, keys):
    values=[xstr(td.string) for td in row.findAll('td')]
    event=dict(zip(keys,values))
    if row.find(id="ctl5"):
        event['url']=str(row.find(id="ctl5").find('a').get('href'))
        event['ID']=int(event.get('url').rsplit('=')[-1])
    event['Points']=int(event.get("SOF",0))
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
    player['Points']=get_value(player.get('Ranking Points',0))
    return player

def get_player(player_id):
    return None

def get_ranking(size):
    ranking_url="http://www.owgr.com/ranking?pageSize="+str(size)
    soup=soup_results(ranking_url)
    ranking=[ranking_headers(soup)]
    for row in soup.findAll('tr'):
        player=player_rankings(row)
        player_name=player.get('Name')
        if player and player_name:
            ranking.append(player)
    return ranking

def get_rankings():
    # Get previous weeks ranking (if not week 0)
    if current_week()=='0':
        prevweek={}
    else:
        prevweek=last_weeks_rankings()
    picks=get_picks()
    for pick in picks:
        if prevweek.get(pick):
            picks[pick]["Points"]=round(prevweek[pick]["Points"],2)
        else:
            picks[pick]["Points"]=0.0
    picks['Available']={'Count':0, 'Picks':[] }
    ranking_url="http://www.owgr.com/ranking"
    soup=soup_results(ranking_url)
    rankings=[ranking_headers(soup)]
    for row in soup.findAll('tr'):
        player=player_rankings(row)
        player_name=player.get('Name')
        if player_name in prevweek.keys():
            player['Last Week']=prevweek[player_name]["Rank"]
            player['Week']=round(player['Points']-prevweek[player_name]['Points'],2)
        if player_name in picks.keys():
            picker=picks[player_name]['Picker']
            player['Picker']=picker
            player['Pickno']=picks[picker]['Count']
            if picks[picker]['Count']<MAXPICKS:
                picks[picker]['Picks'].append(player_name)
                picks[picker]['Count']+=1
                picks[picker]['Week']=round(picks[picker]['Week']+player['Week'],2)
                picks[picker]['Points']=round(picks[picker]['Points']+player['Week'],2)
        else:
            if player_name:
                picks['Available']['Picks'].append(player_name)
                picks['Available']['Count']+=1 
        if player and player_name:  
            player["Week"]=round(player["Week"],2)        
            rankings.append(player)
    # append totals to the end
    rankings.append({key:value for key,value in picks.iteritems() if key in pickers})
    picks['Available']['Picks'].sort()
    rankings[-1]['Available']=picks['Available']
    return rankings

def event_results(event_id):
    picks=get_picks()
    num_picks=0
    event_url='http://www.owgr.com/en/Events/EventResult.aspx?eventid='+str(event_id)
    soup=soup_results(event_url)
    headers=event_headers(soup)
    event_keys=['Pos', 'Ctry', 'Name', 'R1', 'R2', 'R3', 'R4', 'Agg', 'Ranking Points']
    players=[]
    for row in soup.findAll('tr'):
        add_player=False
        name = row.find('td',{'class': "name"})
        if name and name.string:
            player=player_results(row,event_keys)
            if player.get("Rank")==1:
                add_player=True
            if player.get('Name') in picks.keys():
                player_name=player['Name']
                picker=picks[player_name]['Picker']
                player['Picker']=xstr(picker)
                add_player=True
                num_picks+=1
        if add_player:
           players.append(player)
    # only add events with picks
    if num_picks==0:
        players=[]
    return players

def get_events(week_id=0):
    return get_results()

def major_event(event):
    event_id=(event['Year']-2000)*100
    if event['Week']<20:
        event_id+=4
        event_name=str(event['Year'])+" Masters"
    elif event['Week']<25:
        event_id+=6
        event_name=str(event['Year'])+" US Open"
    elif event['Week']<30:
        event_id+=7
        event_name=str(event['Year'])+" Open Championship"
    else:
        event_id+=8
        event_name=str(event['Year'])+" PGA Championship"
    new_event=json_results('http://skipflog.appspot.com/picks?event_id='+str(event_id))
    new_event["url"]="http://www.owgr.com"+event["url"]
    return new_event
    
def get_majors(year):
    events_url='http://www.owgr.com/events?pageNo=1&pageSize=400&tour=Maj&year='+str(year)
    soup=soup_results(events_url)
    headers=event_headers(soup)
    keys=headers.get('columns')[:6]
    events=[]
    for row in soup.findAll('tr'):
        if row.find(id="ctl5"):
            event=row_results(row,keys)
            if event.get("Points",0)>=100:
                events.append(major_event(event))
    return events

def dump_rankings():
    ranking=get_rankings()
    with open('../rankings.json', 'w') as outfile:
        json.dump(ranking, outfile)
    results=get_events(ranking[0]['week_id'])
    with open('../results.json', 'w') as outfile:
        json.dump(results, outfile)

def post_results():
    ranking=get_rankings()
    week_id=ranking[0]['week_id']
    rankingstr=json.dumps(ranking)
    results=get_results()
    resultstr=json.dumps(results)
    query_args = { 'week_id': week_id, 'rankings': rankingstr, 'results': resultstr, 'submit':'Update' }
    encoded_args = urllib.urlencode(query_args)
    update_url="http://knarflog.appspot.com/update"
    result=urllib2.urlopen(update_url, encoded_args)
    return True