'''
Created on 2013-05-21

@author: Dallas
'''
import MySQLdb

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

def test_process():
    process("INSERT INTO `News` (`news`) VALUES ('TEST')")
    result = selectOne("SELECT * FROM News WHERE news like 'TEST'")
    if result is None or result['news'] != 'TEST':
        print("FAILED TEST_PROCESS (INSERT)")
    process("DELETE FROM News WHERE news like 'TEST'")
    result = selectOne("SELECT * FROM News WHERE news like 'TEST'")
    if result is not None:
        print('FAILED TEST_PROCESS (DELETE)')

def test_selectOne():
    result = selectOne("SELECT * FROM Player where player_id = 1")
    if result is None or result['player_name'] != 'Dallas Fraser':
        print("FAILED TEST_SELECTONE ")

def test_selectAll():
    result = selectAll("SELECT * FROM Player")
    if result is None or len(result) < 1:
        print("FAILED TEST_SELECTALL ")

#test_process()
#test_selectAll()
#test_selectOne()
#print("Done")
