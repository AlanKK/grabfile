from dbpassword import dbpassword
import os

if os.path.exists('password_test.db'):
    os.remove('password_test.db')
dbpw = dbpassword('password_test.db')
dbpw.update('admin', 'test', '', 1)
dbpw.update('alank', 'test', 'Alan Keister', 0)

user = 'alank'
assert dbpw.user_exists(user)

user = 'ialkjaslfdkjdf'
assert not dbpw.user_exists(user)

assert dbpw.get_fullname('admin') == ''
assert dbpw.get_fullname('alank') == 'Alan Keister'

assert dbpw.isAdmin('admin')
assert not dbpw.isAdmin('alank')


# Test delete
user = 'alank123'
dbpw.update(user, 'test', 'Alan Keister', 0)
dbpw.delete_users([user])

assert not dbpw.user_exists(user)

assert dbpw.check('admin', 'test')
assert dbpw.check('alank', 'test')
assert not dbpw.check('admin', 'te')
assert not dbpw.check('admin', 'testing')
assert not dbpw.check('admin', '')
print "OK"
