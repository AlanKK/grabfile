from dbpassword import dbpassword
import os

if os.path.exists('password_test.db'):
    os.remove('password_test.db')
dbpw = dbpassword('password_test.db')
dbpw.update('admin', 'test', '', 1)
dbpw.update('user1', 'test', 'User One', 0)

user = 'user1'
assert dbpw.user_exists(user)

user = 'ialkjaslfdkjdf'
assert not dbpw.user_exists(user)

assert dbpw.get_fullname('admin') == ''
assert dbpw.get_fullname('user1') == 'User One'

assert dbpw.isAdmin('admin')
assert not dbpw.isAdmin('user1')


# Test delete
user = 'user123'
dbpw.update(user, 'test', 'User One', 0)
dbpw.delete_users([user])

assert not dbpw.user_exists(user)

assert dbpw.check('admin', 'test')
assert dbpw.check('user1', 'test')
assert not dbpw.check('admin', 'te')
assert not dbpw.check('admin', 'testing')
assert not dbpw.check('admin', '')
print "OK"
