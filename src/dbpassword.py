'''
Taken from http://michelanders.blogspot.com/2011/03/sqlite-thread-safe-password-store.html and modified by AK to add an admin field to the db and a check for admin.

    dbpassword.py Copyright 2011, Michel J. Anders

    This program is free software: you can redistribute it
    and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any
    later version.

    This program is distributed in the hope that it will be 
    useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    PURPOSE. See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public
    License along with this program.  If not, see 
    <http: www.gnu.org="" licenses="">.


Example:

from dbpassword import dbpassword

dbpw = dbpassword('/var/password.db')

# later, from any thread

dbpw.update(user,plaintextpassword,fullname,admin) # update or set a new password


if dbpw.check(user,plaintextpassword) :
     ... do stuff ...
else:
     ... warn off user ...

if isAdmin(user):
    ... give access ...

'''
import sqlite3
import hashlib
from random import SystemRandom as sr
import threading

class dbpassword:

    @staticmethod
    def hashpassword(name,salt,plaintextpassword,n=10):
        if n<1 : raise ValueError("n < 1")
        d = hashlib.new(name,(salt+plaintextpassword).encode()).digest()
        while n:
            n -= 1
            d = hashlib.new(name,d).digest()
        return hashlib.new(name,d).hexdigest()

    @staticmethod
    def getsalt(randombits=64):
        if randombits<16 : raise ValueError("randombits < 16")
        return "%016x"%sr().getrandbits(randombits)

    def __connect(self):
        if not hasattr(self.local,'con') or self.local.con is None:
            self.local.con = sqlite3.connect(self.db)
            self.local.con.create_function('crypt',2,
                lambda s,p:dbpassword.hashpassword(
                  self.secure_hash,s,p,self.iterations))
        return self.local.con
    
    def __init__(self,db,
                   secure_hash='sha256',iterations=1000,saltbits=64):
        self.db = db
        self.local = threading.local()
        self.secure_hash = secure_hash
        self.iterations = iterations
        self.saltbits = 64
        with self.__connect() as con:
            cursor=con.cursor()
            sql='create table if not exists pwdb (user unique, salt, password, fullname, admin integer)'
            cursor.execute(sql)    
    
    def update(self,user,plaintextpassword,fullname,admin=0):
        with self.__connect() as con:
            cursor=con.cursor()
            sql1='insert or replace into pwdb (user,salt,fullname,admin) values(?,?,?,?)'
            sql2='update pwdb set password=? where user = ?'
            salt=dbpassword.getsalt(self.saltbits)
            cursor.execute(sql1,(user,salt,fullname,admin))
            cursor.execute(sql2,(dbpassword.hashpassword(
                    self.secure_hash,salt,plaintextpassword,
                    self.iterations),user))

    def check(self,user,plaintextpassword):
        cursor=self.__connect().cursor()
        sql='select user from pwdb where user = ? and crypt(salt,?) = password'
        cursor.execute(sql,(user,plaintextpassword))
        found=list(cursor) # can only create a list form this iterator once!
        return len(found)==1


    def list_users(self):
        cursor=self.__connect().cursor()
        sql='select user,fullname,admin from pwdb'
        cursor.execute(sql,)
        return list(cursor)

    def isAdmin(self,user):
        cursor=self.__connect().cursor()
        sql='select user from pwdb where user = ? and admin = 1'
        cursor.execute(sql,[user])
        found=list(cursor) # can only create a list form this iterator once!
        return len(found)==1

    def user_exists(self,user):
        cursor=self.__connect().cursor()
        sql='select user from pwdb where user = ?'
        cursor.execute(sql,[user])
        found=list(cursor) # can only create a list form this iterator once!
        return len(found)==1

    def get_fullname(self,user):
        ''' Returns a string with full name or empty string ('') '''
        cursor=self.__connect().cursor()
        sql='select fullname from pwdb where user = ?'
        cursor.execute(sql,[user])
        found=list(cursor) # can only create a list form this iterator once!
        return str(found[0][0])

    def delete_users(self,userlist):
        with self.__connect() as con:
            for user in userlist:
                sql='delete from pwdb where user = ?'
                con.execute(sql,[user])

        return
