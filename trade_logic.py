'''
Created on 2013-05-21

@author: Dallas
'''
import MySQLdb
import unittest
import datetime
def selectAll(querytext): 
    connection=MySQLdb.connect(user="fras2560",passwd="Lcc17pet",db="fras2560",
                               host="hopper.wlu.ca")
    cursor=connection.cursor(MySQLdb.cursors.DictCursor)
    #print (querytext)
    cursor.execute(querytext)
    answer=cursor.fetchall()
    connection.close()
    return answer

def selectOne(querytext):
    connection=MySQLdb.connect(user="fras2560",passwd="Lcc17pet",db="fras2560",
                               host="hopper.wlu.ca")
    cursor=connection.cursor(MySQLdb.cursors.DictCursor)
    #print (querytext)
    cursor.execute(querytext)
    answer=cursor.fetchone()
    connection.close()
    return answer


def process (querytext):
    connection=MySQLdb.connect(user="fras2560",passwd="Lcc17pet",db="fras2560",
                               host="hopper.wlu.ca")
    cursor=connection.cursor(MySQLdb.cursors.DictCursor)
    print (querytext)
    try:
        cursor.execute(querytext)
        connection.commit()
    except:
        connection.rollback()
    connection.close()
    return

def processArgs(query, item, id):
    connection = MySQLdb.connect(user="fras2560", passwd="Lcc17pet",
                                 db="fras2560", host="hopper.wlu.ca")
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    args = [item, id]
    print(query)
    print(args)
    try:
        cursor.execute(query, args)
        connection.commit()
        result = 'SUCCESS'
    except:
        connection.rollback()
        result = 'FAILURE'
    return result
     
def insertPicture (query, file, id):
    connection = MySQLdb.connect(user="fras2560", passwd="Lcc17pet",
                                 db="fras2560", host="hopper.wlu.ca")
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    args = (file, id)
    try:
        cursor.execute(query, args)
        connection.commit()
        result='SUCCESS'
    except:
        connection.rollback()
        result='FAILURE'
    connection.close()
    return result

class testSuit(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def testMakeTrade(self):
        team_id = [31,32]
        proposing_id = 31
        receiving_id = 32
        proposing_team = [110]
        receiving_team = [111,112]
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        create_trade = ''' INSERT INTO trade 
                        (team_id_1, team_id_2, date, status ) 
                        VALUES ('%s', '%s', %s, 'CREATING');        
                        ''' % (team_id[0], team_id[1], date)
        process(create_trade)
        trade_query = '''SELECT * FROM trade WHERE 
                        team_id_1 = %i AND
                        team_id_2 = %i AND
                        status = 'CREATING' 
                      ''' % (team_id[0], team_id[1])
        print(date)
        trade_result = selectOne(trade_query)              
        trade_id =  trade_result['trade_id']
        for player in proposing_team:
            trade_row = ''' INSERT INTO Trade_Player_List 
                        (player_id, trade_id, team_to)
                        VALUES ('%s', '%s', '%s')
                        ''' %(player, trade_id, receiving_id )
            process(trade_row)
        for player in receiving_team:
            trade_row = ''' INSERT INTO Trade_Player_List 
                        (player_id, trade_id, team_to)
                        VALUES ('%s', '%s', '%s')
                        ''' %(player, trade_id, proposing_id )
            process(trade_row)
        query = '''SELECT * FROM view_trade_details'''
        results =  selectAll(query)
        print(results)
        update_trade = '''UPDATE trade SET `status`='PENDING' WHERE `trade_id`=%s
                       ''' % trade_id
        process(update_trade)
        return 
        
    def testDeleteTrade(self, trade_id = None):
        
        delete_trade = '''DELETE FROM Trade_Player_List WHERE trade_id  = %i
                        ''' % trade_id
        delete_players = '''DELETE FROM trade WHERE trade_id  = %i
                        ''' % trade_id
        process(delete_players)
        process(delete_trade)
        
        query = '''SELECT * FROM view_trade_details'''
        results =  selectAll(query)
        self.assertEqual(False, 'TESTPLAYER1' in results)
        return
    
    def testConfirmTrade(self):
        trade_id = 22
        proposing_sql = '''SELECT * FROM Trade_Player_List WHERE trade_id = %s;
                        ''' % trade_id
        results = selectAll(proposing_sql)
        for player in results:
            print(player)
            delete_sql = '''DELETE FROM Team_Roster WHERE player_id = %i 
                        AND year = Year(CURDATE());
                        ''' % player['player_id']
            insert_sql = '''INSERT INTO Team_Roster (team_id, player_id, year) 
                            VALUES (%s, %s, Year(CURDATE()));
                         ''' % (player['team_to'], player['player_id'])
            process(delete_sql)
            process(insert_sql)
        self.testDeleteTrade(trade_id)
        
        
        
        
        
        
        