from dbsession import dbsession
from uuid import uuid4
import os
from pprint import pprint

os.remove('session_test.db')
sess = dbsession('session_test.db')

session_list = []

user = 'user1'
session_id = str(uuid4())
session_list.append(session_id)
sess.add_session(user, session_id, expiration=0)
sessions = sess.get_sessions(user)
assert len(sessions) == 1
assert sessions[0][0] == session_id

user = 'user1'
session_id = str(uuid4())
sess.add_session(user, session_id, expiration=0)
sessions = sess.get_sessions(user)
assert len(sessions) == 2
assert sessions[1][0] == session_id

sess.delete_session(session_id)
sessions = sess.get_sessions(user)
assert len(sessions) == 1

# Add files, delete files
user = 'user1'
session_id = str(uuid4())
session_list.append(session_id)
sess.add_session(user, session_id, expiration=0)
sessions = sess.get_sessions(user)
assert len(sessions) == 2
assert sessions[1][0] == session_id
sess.add_file(session_id, 'testa.file')
sess.add_file(session_id, 'testb.file')
sess.add_file(session_id, 'testc.file')
files = sess.get_files(session_id)
assert len(files) == 3
assert files[1][0] == 'testb.file'

# Add session, add files, delete session and check for file and 
# session removal
sess.delete_session(session_id)
session_list.remove(session_id)
files = sess.get_files(session_id)
assert len(files) == 0
sessions = sess.get_sessions(user)
assert session_id not in sessions

# Add another session and some files
user = 'user1'
session_id = str(uuid4())
session_list.append(session_id)
sess.add_session(user, session_id, expiration=0)
sessions = sess.get_sessions(user)
assert len(sessions) == 2
assert sessions[1][0] == session_id
sess.add_file(session_id, 'test1.file')
sess.add_file(session_id, 'test2.file')
sess.add_file(session_id, 'test3.file')
files = sess.get_files(session_id)
assert len(files) == 3
assert files[1][0] == 'test2.file'

session_id = str(uuid4())
session_list.append(session_id)
sess.add_session(user, session_id, expiration=0)
sessions = sess.get_sessions(user)
assert len(sessions) == 3
sess.add_file(session_id, 'test4.file')
sess.add_file(session_id, 'test5.file')
sess.add_file(session_id, 'test6.file')
files = sess.get_files(session_id)
assert len(files) == 3
assert files[1][0] == 'test5.file'

assert sess.get_session_user(session_id) == user

pprint(sess.get_all_files(user))
#sess.get_all_files(user)

print "OK"
