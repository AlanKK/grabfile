'''
'''
import sqlite3
from random import SystemRandom as sr
import threading

class dbsession:

    def __connect(self):
        if not hasattr(self.local,'con') or self.local.con is None:
            self.local.con = sqlite3.connect(self.db)
        return self.local.con
    
    def __init__(self,db):
        self.db = db
        self.local = threading.local()

        with self.__connect() as con:
            cursor=con.cursor()
            sql1='create table if not exists upload_sessions (user, session_id unique, expiration integer)'
            sql2='create table if not exists files (session_id, filename)'
            cursor.execute(sql1)    
            cursor.execute(sql2)    
    
    def add_session(self,user,session_id,expiration = 0):
        with self.__connect() as con:
            cursor=con.cursor()
            sql='insert or replace into upload_sessions (user,session_id,expiration) values(?,?,?)'
            cursor.execute(sql,(user,session_id,expiration))
            con.commit()

    def get_session_user(self,session_id):
        cursor=self.__connect().cursor()
        sql='select user from upload_sessions where session_id = ?'
        cursor.execute(sql,[session_id])
        found=list(cursor) # can only create a list form this iterator once!
        return str(found[0][0])

    def get_sessions(self,user):
        cursor=self.__connect().cursor()
        sql='select session_id,expiration from upload_sessions where user = ?'
        cursor.execute(sql,[user])
        found=list(cursor) # can only create a list form this iterator once!
        return found

    def delete_session(self,session_id):
        with self.__connect() as con:
            cursor=con.cursor()
            sql1='delete from upload_sessions where session_id = ?'
            sql2='delete from files where session_id = ?'
            cursor.execute(sql1,[session_id])
            cursor.execute(sql2,[session_id])
            con.commit()

    def add_file(self,session_id,filename):
        with self.__connect() as con:
            cursor=con.cursor()
            sql='insert or replace into files (session_id,filename) values(?,?)'
            cursor.execute(sql,(session_id,filename))
            con.commit()

    def get_files(self,session_id):
        cursor=self.__connect().cursor()
        sql='select filename from files where session_id = ?'
        cursor.execute(sql,[session_id])
        found=list(cursor)
        return found

    def get_all_files(self,user):
        """ Return a table with sessions and files like this:

                {u'0bb2c443-37c3-49c5-9782-0d9ac1ca50b7': [],
                 u'bfecbf7f-723e-485e-9bde-f29e56afb894': ['test1.file',
                                                           'test2.file',
                                                           'test3.file']}

        """ 
        cursor=self.__connect().cursor()
	result_dict = {}
        sql='select session_id,expiration from upload_sessions where user = ?'
        for row in cursor.execute(sql,[user]):
	    files = self.get_files(row[0])
	    file_list = []
	    for filename in files:
	        file_list = file_list + [str(filename[0])]
	    result_dict[row[0]] = file_list

        return result_dict


    def delete_file(self,filename):
        with self.__connect() as con:
            cursor=con.cursor()
            sql='delete from files where filename = ?'
            cursor.execute(sql,[filename])
            con.commit()

