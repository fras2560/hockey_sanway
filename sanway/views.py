'''
Created on 2013-05-21
@author: Dallas
'''
from flask import render_template
from flask import flash, redirect
from sanway import app
from db import selectAll, selectOne, process, insertPicture, processArgs
from flask import request
from flask import url_for
from flask import session
from datetime import date
import json
import datetime
# index view function suppressed for brevity

@app.route('/championships')
def champs(): 
    query = '''SELECT * FROM v_championship'''
    championship = selectAll(query)
    query = '''SELECT * FROM v_winning_roster'''
    players = selectAll(query)
    return render_template('champs.html',
                           players=players,
                           championship=championship
                           )
@app.route('/leaders')
def leaders():
    query = ''' SELECT DISTINCT YEAR FROM v_player_stats'''
    years = selectAll(query)
    list = []
    query = '''SELECT * FROM v_player_stats WHERE Year = %s  
            ORDER BY Goals DESC LIMIT 5''' % 2013
    goal_leaders = selectAll(query)
    query = '''SELECT * FROM v_player_stats WHERE Year = %s  
            ORDER BY Assists DESC LIMIT 5''' % 2013
    assist_leaders = selectAll(query)
    query = '''SELECT * FROM v_player_stats WHERE Year = %s  
            ORDER BY Points DESC LIMIT 5''' % 2013
    points_leaders = selectAll(query)
    return render_template('leader.html',
                           goal_leaders=goal_leaders,
                           years=years,
                           points_leaders=points_leaders,
                           assist_leaders=assist_leaders
                           )     

@app.route('/picture/<int:id>')
def picture(id):
    query = "SELECT * FROM Photos WHERE photo_id = %s" % id
    player = selectOne(query)
    imageBlob = player['picture']
    return imageBlob

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
def index():
    user = {"nickname": "Dallas"}
    events = selectAll('SELECT * FROM News ORDER BY news_id DESC Limit 10')
    query = '''SELECT * FROM Photos WHERE
            photo_id > 3 AND photo_id != 14 LIMIT 10'''
    pictures = selectAll(query)
    captions = ['Because its the cup', 'History will be made',
                'Question will be answered', 'Sanway Cup',
                'Where dreams come true', 'Play hard and Party Hard']
    for picture in pictures:
        if(len(captions) != 0):
            picture['caption'] = captions.pop()
    return render_template('index.html',
                           title='Home',
                           user=user,
                           events=events,
                           pictures=pictures,
                           captions=captions
                           )


@app.route('/news/')
@app.route('/news')
def news():
    user = {"nickname": "Dallas"}
    events = selectAll('SELECT * FROM News ORDER BY news_id DESC')
    return render_template('news.html',
                           title='Home',
                           user=user,
                           events=events
                           )


@app.route('/about')
@app.route('/about/')
def about():
    return render_template('about.html',
                           title="About"
                           )


@app.route('/teamLogout')
@app.route('/teamLogout/')
@app.route('/team/logoutteam/')
@app.route('/team/logoutteam')
def teamLogOut():
    logoutTeam()
    return redirect(url_for('index'))

@app.route('/team/change/teamBio/update/', methods=['GET', 'POST'])
@app.route('/teamBio/update/', methods=['GET', 'POST'])
def updateTeamBio():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    id = session['team_id']
    password = ''
    captain = ''
    name = ''
    if request.form['name']:
        name = request.form['name']
    if request.form['captain']:
        captain = request.form['captain']
    if request.form['pw']:
        password = request.form['pw']
    result = []
    if name != '':
        query = '''UPDATE Team SET team_name = %s WHERE team_id = %s
                ''' 
        temp = processArgs(query, str(name), int(id))
        if temp == 'SUCCESS':
            result.append(' SUCCESS:team name')
        else:
            result.append(' FAILED:team name')
    if captain != '':
        query = '''UPDATE Team SET captain = %s WHERE team_id = %s
                '''  
        temp = processArgs(query, str(captain), int(id))
        if temp == 'SUCCESS':
            result.append(' SUCCESS:captain')
        else:
            result.append(" FAIL:captain")     
    if password != '':
        query = '''UPDATE Team SET password = %s WHERE team_id = %s
                '''  
        temp = processArgs(query, str(captain), int(id))
        if temp == 'SUCCESS':
            result.append(' SUCCESS:password')
        else:
            result.append(" FAILED:password")     
    session['error'] = result
    session['action'] = 'Bio Update'
    return redirect(url_for('teamBio'))


@app.route('/teams/')
@app.route('/teams')
def teams():
    query = 'Select * from v_team_wins ORDER BY team_name ASC'
    teams = selectAll(query)
    return render_template('teams.html',
                           title='Teams',
                           teams=teams
                           )


@app.route('/teams/<int:id>')
@app.route('/teams/<int:id>/')
def teamPage(id):
    captain = None
    query = 'SELECT * FROM v_team_wins WHERE team_id =%s' % id
    team = selectOne(query)
    query = ('''
            SELECT * FROM v_team_roster WHERE
            team_id=%s AND Year=Year(CURDATE())''' % id)
    players = selectAll(query)
    query = 'SELECT * FROM Team WHERE team_id=%i' %id
    c = selectOne(query)
    if c is not None:
        captain = c['captain']
    return render_template('teamPage.html',
                           team=team,
                           players=players,
                           captain=captain
                           )

@app.route('/teamBio/picture/<int:id>/')
@app.route('/teamBio/picture/<int:id>')
@app.route('/picture/<int:id>')
@app.route('/teams/picture/<int:id>')
@app.route('/teams/<int:id>/picture/')
@app.route('/teams/<int:id>/picture')
def teamPicture(id):
    query = "SELECT * FROM Team WHERE team_id = %s" % id
    team = selectOne(query)
    imageBlob = team['team_pic']
    if imageBlob is None:
        query = "SELECT * FROM Photos WHERE photo_id=2"
        picture = selectOne(query)  
        imageBlob = picture['picture']
    return imageBlob


@app.route('/teamBio/')
@app.route('/teamBio')
def teamBio():
    if 'team_id' in session:
        captain = None
        action = None
        id = session['team_id']
        query = 'SELECT * FROM v_team_wins WHERE team_id =%i' % id
        team = selectOne(query)
        query = ('''
                SELECT * FROM v_team_roster WHERE
                team_id=%i AND Year=Year(CURDATE())''' % id)
        players = selectAll(query)
        query = 'SELECT * FROM Team WHERE team_id=%i' %id
        c = selectOne(query)
        if c is not None:
            captain = c['captain']
        if 'error' in session:
            error = session.pop('error',None)
            action = session.pop('action', None)
        else:
            error = []
        return render_template('teamBio.html',
                               team=team,
                               players=players,
                               error=error,
                               action=action,
                               captain=captain
                               )
    else:
        return redirect(url_for('teamLogin'))


@app.route('/teamSignIn', methods=['GET', 'POST'])
@app.route('/teamSignIn/', methods=['GET', 'POST'])
def teamLogin():
    post_url = '/TeamPortal/'
    if 'error' in session:
        error = session.pop('session',None)
    else:
        error = None
    logoutTeam()
    return render_template('login.html',
                            type='Team',
                            error=error,
                            post_url=post_url
                            )

@app.route('/team/roster/cuts', methods=['GET', 'POST'])
@app.route('/team/roster/cuts/', methods=['GET', 'POST'])
def cutPlayer():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    team = session['team_id']
    player = request.form['player_id']
    query = ''' DELETE FROM Team_Roster WHERE player_id = %s 
            AND team_id = %s AND year = Year(CURDATE())''' % (player, team)
    process(query)
    query = 'SELECT * FROM Player where player_id = %s' % player
    p = selectOne(query) 
    player_name = p['player_name']
    query = 'SELECT * FROM Team where team_id = %s' % team
    t = selectOne(query) 
    team_name = t['team_name']
    news = "%s has been released from the %s" %(player_name, team_name)
    writeNews(news)
    return redirect(url_for('teamRosterForm'))

@app.route('/team/change/bio/')
@app.route('/team/change/bio')
def teamBioForm():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    return render_template('teamBioForm.html')


@app.route('/team/roster/adds', methods=['GET', 'POST'])
@app.route('/team/roster/adds/', methods=['GET', 'POST'])
def addPlayer():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    team = session['team_id']
    player = request.form['player_id']
    query = ''' INSERT INTO Team_Roster (team_id, player_id, year) 
            VALUES (%s, %s, Year(CURDATE())) ''' % (team, player)
    print(query)
    process(query)
    query = 'SELECT * FROM Player where player_id = %s' % player
    p = selectOne(query) 
    player_name = p['player_name']
    query = 'SELECT * FROM Team where team_id = %s' % team
    t = selectOne(query) 
    team_name = t['team_name']
    news = "%s has been added to the %s" %(player_name, team_name)
    writeNews(news)
    return redirect(url_for('teamRosterForm'))


@app.route('/team/change/roster')
@app.route('/team/change/roster/')
def teamRosterForm():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    id = session['team_id']
    query = '''SELECT * FROM v_team_roster WHERE team_id = %s AND 
            Year = Year(Curdate())''' % id
    roster = selectAll(query)
    query = '''Select * from Player AS p WHERE p.player_id NOT IN 
            (SELECT player_id from Team_Roster where year=YEAR(CURDATE())) 
            ORDER BY p.player_name'''
    players = selectAll(query)
    return render_template('teamRosterForm.html',
                           roster=roster,
                           players=players)


@app.route('/team/change/picture')
@app.route('/team/change/picture/')
def teamPicForm():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    return render_template('pictureForm.html',
                           type='Team',
                           action='/team/upload/')


@app.route('/team/upload', methods=['GET', 'POST'])
@app.route('/team/upload/', methods=['GET', 'POST'])
def insertTeamPic():
    if 'team_id' not in session:
        return redirect(url_for('teamLogin'))
    if request.method == 'POST':
        if request.files['file']:
            mime_type = request.files['file'].mimetype
            id = session['team_id']
            file = request.files['file'].stream.read()
            query = '''UPDATE Team SET team_pic = %s WHERE team_id = %s
                    '''
            result = insertPicture(query, file, id)
        session['error'] = [result]
        return redirect(url_for('teamBio'))
    else:
        session['error'] = "File Failed"
        return redirect(url_for('teamBio'))


@app.route('/TeamPortal/', methods=['POST', 'GET'])
def TeamPortal():
    if 'teamLogin' in session:
        return redirect(url_for('teamPage'))
    else:
        user_name = request.form['username']
        password = request.form['password']
        query = ''' SELECT * from Team WHERE team_name like 
                '%s' AND password = '%s'
                ''' % (user_name, password)
        teams = selectAll(query)
        if (len(teams) != 1):
            session['error'] = 'INVALID COMBO'
            return redirect(url_for('teamLogin'))
        elif (teams is None):
            session['error'] = 'INVALID COMBO'
            return redirect(url_for('teamLogin'))
        else:
            session['teamLogin'] = True
            session['team_name'] = user_name
            session['team_id'] = teams[0]['team_id']
            return redirect(url_for('teamBio'))

@app.route('/playerBio/picture/<int:id>')
@app.route('/player/picture/<int:id>')
@app.route('/player/picture/<int:id>/')
@app.route('/playerBio/picture/<int:id>')
def playerPicture(id):
    query = "SELECT * FROM Player WHERE player_id = %s" % id
    player = selectOne(query)
    imageBlob = player['picture']
    if imageBlob is None:
        query = "SELECT * FROM Photos WHERE photo_id=1"
        picture = selectOne(query)
        imageBlob = picture['picture']
    return imageBlob

@app.route('/team/join')
def teamJoinForm():
    if 'error' in session:
        error = session.pop('error', None)
    else:
        error = None
    return render_template('joinForm.html',
                           user='Team Name',
                           post='team',
                           error=error)


@app.route('/team/help/', methods=['GET', 'POST'])
def teamJoin():
    if request.form['user'] and request.form['pw']:
        user = request.form['user']
        password = request.form['pw']
    else:
        session['error'] = ' Missing element'
        return redirect(url_for('teamJoinForm'))
    query = 'INSERT INTO Team (team_name, password) VALUES(%s, %s)'
    result = processArgs(query, user, password)
    if result == 'FAILURE':
        session['error'] = ''' JOIN FAILED: CONTACT fras2560@mylaurier,ca
                            check to see if you team name already exist'''
        return redirect(url_for('teamJoinForm'))
    query = ''' SELECT * from Team WHERE team_name like 
                '%s' AND password = '%s'
                ''' % (user, password)
    team = selectOne(query)
    session['teamLogin'] = True
    session['team_name'] = user
    session['team_id'] = team['team_id']
    news = "%s is the new team to beat in the league" % user
    writeNews(news)
    return redirect(url_for('teamBio'))




@app.route('/player/join')
def playerJoinForm():
    if 'error' in session:
        error = session.pop('error', None)
    else:
        error = None
    return render_template('joinForm.html',
                           user='Your Name',
                           post='player',
                           error=error)
    
@app.route('/player/help/',methods=['GET', 'POST'])
def playerJoin():
    if request.form['user'] and request.form['pw']:
        user = request.form['user']
        password = request.form['pw']
    else:
        session['error'] = ' Missing element'
        return redirect(url_for('playerJoinForm'))
    query = 'INSERT INTO Player (player_name, password) VALUES(%s, %s)'
    result = processArgs(query, user, password)
    if result == 'FAILURE':
        session['error'] = ''' JOIN FAILED: CONTACT fras2560@mylaurier,ca
                            Check to see if your name is already entered'''
        return redirect(url_for('playerJoinForm'))
    query = ''' SELECT * from Player WHERE player_name like 
                '%s' AND password = '%s'
                ''' % (user, password)
    player = selectOne(query)
    session['playerLogin'] = True
    session['player_name'] = user
    session['player_id'] = player['player_id']
    news = "%s has joined the league" % user
    writeNews(news)
    return redirect(url_for('playerBio'))


@app.route('/player/<int:id>')
def playerPage(id):
    query = 'Select * from v_player where player_id = %s' % id
    player = selectOne(query)
    query = '''SELECT * FROM v_team_roster WHERE
            player_id = %s AND Year = Year(CURDATE()) ''' % id
    teamInfo = selectOne(query)
    query = '''SELECT * FROM Player WHERE
            player_id = %s''' % id
    personal = selectOne(query)
    if teamInfo:
        team = teamInfo['team_name']
    else:
        team = None
    return render_template('playerPage.html',
                           title='Player Page',
                           player=player,
                           team=team,
                           personal=personal
                           )


@app.route('/player/change/bio/update/', methods=['GET', 'POST'])
@app.route('/bio/update/', methods=['GET', 'POST'])
def updateBio():
    if 'player_id' not in session:
        return redirect(url_for('playerLogin'))
    id = session['player_id']
    favourite = ''
    password = ''
    quote = ''
    years= ''
    if request.form['fp']:
        favourite = request.form['fp']
    if request.form['yp']:
        year = request.form['yp']
        years = int(year)
    if request.form['qu']:
        quote = request.form['qu']    
    if request.form['pw']:
        password = request.form['pw']
    result = []    
    if password != '':
        query = '''UPDATE Player SET password = %s WHERE player_id = %s
                '''
        temp = processArgs(query, password, id)
        if temp == 'SUCCESS':
            result.append(' SUCCESS:password')
        else:
            result.append(' FAIL:password')
    if quote != '':
        query = '''UPDATE Player SET quote = %s WHERE player_id = %s
                ''' 
        temp = processArgs(query, quote, id)
        if temp == 'SUCCESS':
            result.append('SUCCESS:quote')
        else:
            result.append('FAIL:quote')
    if years != '':
        if years < (int(date.today().year) - 2007) and years > 0:
            years = '''UPDATE Player SET years_played = %i WHERE player_id = %s
                    ''' 
            temp = processArgs(query, years, id)
            if temp == 'SUCCESS':
                result.append('SUCCESS:years played')
            else:
                result.append("FAILL: years played")
                
        elif years > (int(date.today().year) - 2007):
            max = int(date.today().year) - 2007
            result.append(" FAIL: years greater than %s" 
                               % max)
        else:
            result.append(" FAIL: years since negative number") 
    if favourite != '':
        query = '''UPDATE Player SET fav_player = %s WHERE player_id = %s
                ''' 
        temp = processArgs(query, favourite, id)
        if temp == 'SUCCESS':
            result.append('SUCCESS: favourite player')     
        else:
            result.append("FAIL: favourite player")
    session['error'] = result
    session['action'] = 'Update Player Bio'
    return redirect(url_for('playerBio'))

    
@app.route('/players')
@app.route('/players/')
def players():
    user = {"nickname": "Brother"}
    players = selectAll('Select * from v_player')
    return render_template('player.html',
                           title='Home',
                           user=user,
                           players=players
                           )

@app.route('/player/change/bio')
@app.route('/player/change/bio/')
def playerBioForm():
    if 'player_id' not in session:
        return redirect(url_for('playerLogin'))
    return render_template('bioForm.html')
    

@app.route('/player/change/picture')
@app.route('/player/change/picture/')
def playerPicForm():
    if 'player_id' not in session:
        return redirect(url_for('playerLogin'))
    return render_template('pictureForm.html',
                           type='Player',
                           action='/player/upload/')


@app.route('/upload/', methods=['GET', 'POST'])
@app.route('/player/upload', methods=['GET', 'POST'])
@app.route('/player/upload/', methods=['GET', 'POST'])
def insertPlayerPic():
    if 'player_id' not in session:
        return redirect(url_for('playerLogin'))
    if request.method == 'POST':
        if request.files['file']:
            mime_type = request.files['file'].mimetype
            id = session['player_id']
            file = request.files['file'].stream.read()
            query = '''UPDATE Player SET picture = %s WHERE player_id = %s
                    '''
            result = insertPicture(query, file, id)
        session['error'] = [result]
        session['action'] = 'Updated Player Picture'
        return redirect(url_for('playerBio'))
    else:
        session['error'] = "File Failed"
        session['action'] = 'Updated Player Picture'
        return redirect(url_for('playerBio'))


@app.route('/playerLogout')
@app.route('/playerLogout/')
@app.route('/player/logoutPlayer/')
@app.route('/player/logoutPlayer')
def playerLogOut():
    logoutPlayer()
    return redirect(url_for('index'))


@app.route('/playerBio/')
@app.route('/playerBio')
def playerBio():
    if 'player_id' in session:
        id = session['player_id']
        query = 'SELECT * FROM v_player WHERE player_id = %s' %id
        player = selectOne(query)
        user = session['player_name']
        query = '''SELECT * FROM v_team_roster WHERE
                player_id = %s AND Year = Year(CURDATE()) ''' % id
        teamInfo = selectOne(query)
        query = '''SELECT * FROM Player WHERE
        player_id = %s''' % id
        personal = selectOne(query)
        if teamInfo:
            team = teamInfo['team_name']
        else:
            team = None

        if 'error' in session:
            error = session.pop('error', None)
            action = session.pop('action', None)
        else:
            error = []
            action = None
        return render_template('playerBio.html',
                               player=player,
                               user=user,
                               error=error,
                               action=action,
                               team=team,
                               personal=personal)
    else:
        return redirect(url_for('playerLogin'))


@app.route('/playerSignIn', methods=['GET', 'POST'])
@app.route('/playerSignIn/', methods=['GET', 'POST'])
def playerLogin():
    
    post_url = '/PlayerPortal/'
    if 'error' in session:
        error = session.pop('error',None)
    else:
        error = None
    logoutPlayer()
    return render_template('login.html',
                            type='Player',
                            error=error,
                            post_url=post_url
                            )
                
@app.route('/PlayerPortal/', methods=['POST', 'GET'])
def playerPortal():
    if 'playerLogin' in session:
        return redirect(url_for('playerBio'))
    else:
        user_name = request.form['username']
        password = request.form['password']
        query = ''' SELECT * from Player WHERE player_name like 
                '%s' AND password = '%s'
                ''' % (user_name, password)
        players = selectAll(query)
        if (len(players) != 1):
            session['error'] = 'INVALID COMBO'
            return redirect(url_for('playerLogin'))
        elif (players is None):
            session['error'] = 'INVALID COMBO'
            return redirect(url_for('playerLogin'))
        else:
            session['playerLogin'] = True
            session['player_name'] = user_name
            session['player_id'] = players[0]['player_id']
            return redirect(url_for('playerBio'))

@app.route('/player/graph')
def playerGraph():
    now = datetime.datetime.now()
    year = now.year
    return render_template('graph.html',
                           year=year)


def writeNews(string):
    query = "INSERT INTO News (news) VALUES ('%s')" % string 
    process(query)
    return

def logoutPlayer():
    session.pop('playerLogin', None)
    session.pop('player_name', None)
    session.pop('player_id', None)
    session.pop('query', None)
    return

    
def logoutTeam():
    session.pop('teamLogin', None)
    session.pop('team_name', None)
    session.pop('team_id', None)
    return

@app.route('/player/graph/info')
def tree():
    tree = {"name": "Player Stats"}
    query = ''' SELECT * FROM Team '''
    teams = selectAll(query)
    team_list = []
    for team in teams:
        team_dictionary = {"name":team['team_name']}
        query = ''' SELECT * FROM v_team_roster WHERE team_id = %s 
                AND Year = YEAR(CURDATE())''' % team['team_id']
        players = selectAll(query)
        player_list = []
        for player in players:
            player_dictionary = {"name":player['player_name']}
            query = ''' SELECT * FROM fras2560.v_player_stats WHERE 
                    player_id = %s AND YEAR=Year(Curdate());
                    ''' % player['player_id']
            stats = selectOne(query)
            if stats:
                player_dictionary['size'] = stats['Goals']
            else:
                player_dictionary['size'] = 0
            player_list.append(player_dictionary)
        if player_list == []:
            team_dictionary['size'] = 0
        else:
            team_dictionary['children'] = player_list
        team_list.append(team_dictionary)
    tree['children'] = team_list
    return json.dumps(tree)
