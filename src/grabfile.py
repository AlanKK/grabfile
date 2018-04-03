#!/usr/bin/python
"""
    Grabfile
"""
import os, sys, hashlib
from time import time
from flask import Flask, request, session, g, redirect, abort, render_template, flash, url_for, abort, send_file, safe_join, send_from_directory, escape
from functools import wraps
from werkzeug import secure_filename
from dbpassword import dbpassword
from dbsession import dbsession
from uuid import uuid4
from flask_debugtoolbar import DebugToolbarExtension
import logging
from logging import Formatter

# Set up logging

#werkzeug_log = logging.getLogger('werkzeug')
#werkzeug_log.setLevel(logging.DEBUG) # logging of URLs is at DEBUG level

logging.basicConfig(filename='grabfile.log', level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s: %(message)s ' '[in %(pathname)s:%(lineno)d]')
logging.info ('=============================================================')
logging.info ('Starting grabfile                                            ')
logging.info ('=============================================================')

app = Flask('grabfile')
app.debug = True

# the toolbar is only enabled in debug mode:
app.debug = True

# set the secret key.  keep this really secret:
#app.secret_key = ';lkj ;A#O# A3;8aw3pq8a;lk;gi AFAJLjr29038'
app.config['SECRET_KEY'] = ';lkj ;A#O# A3;8aw3pq8a;lk;gi AFAJLjr29038'

toolbar = DebugToolbarExtension(app)

DOWNLOAD_DIR = '../files'

app.config['username'] = 'admin'
app.config['password'] = 'test'

dbpw = dbpassword('password.db')
dbpw.update('admin', 'test', 'Administrator', 1) # update or set a new password
dbpw.update('user1', 'test', 'User One', 0) # update or set a new password

dbsession = dbsession('sessions.db')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def home():
    return render_template('home.html', name="TEST")


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/admin')
def admin():
    """Admin interface. It may be possible to reach this function if the client side 
       admin flag is set in the session cookie.  Protect this by checking the database
       as well"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    # todo: make an admin page
    return render_template('admin.html')

@app.route('/change_password?user=<user>')
def change_password(user):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    # todo: make an admin page
    return render_template('change_password.html', user=user)


@app.route('/save_password?user=<user>', methods=['POST'])
def save_password(user):
    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    pwd =  request.form['password']

    logging.debug('save_password')
    dbpw.update(user, pwd) # update or set a new password

    return render_template('change_password.html', user=user, result='Complete')


@app.route('/manage_users')
def manage_users():
    """It may be possible to reach this function if the client side 
       admin flag is set in the session cookie.  Protect this by checking the database
       as well"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    logging.debug('list_users')
    users = dbpw.list_users()

    return render_template('manage_users.html', users=users)


@app.route('/delete_users', methods=['POST'])
def delete_users():
    """Add user completion page. It may be possible to reach this function if the client side 
       admin flag is set in the session cookie.  Protect this by checking the database
       as well"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    if request.method != 'POST':
        return abort(400)

    userlist_tuples = request.form.items()

    if not userlist_tuples:
        # Nothing to delete
        users = dbpw.list_users()
        return render_template('manage_users.html', users=users, 
                                error='Nothing selected to delete.')

    # Create a list of users
    userlist = []
    for user in userlist_tuples:
        userlist.append(user[0])
        
    dbpw.delete_users(userlist)
    info = 'User ' +  " ".join([item for item in userlist])+ ' deleted.'
    logging.info(info)

    # go back to login page if auth fails
    users = dbpw.list_users()
    return render_template('manage_users.html', info=info, users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add user completion page. It may be possible to reach this function if the client side 
       admin flag is set in the session cookie.  Protect this by checking the database
       as well"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not dbpw.isAdmin(session.get('username')):
        return abort(401)

    if request.method == 'GET':
        return render_template('add_user.html')
    elif request.method == 'POST':
        error = None

        #TODO: scrub input for valid chars
        user     = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        try:
            if request.form['Administrator']:
                admin = 1
        except KeyError:
            admin = 0

        if len(user) <= 3:
            error = 'Username is too short: ' + user
            logging.warning(error)
            return render_template('add_user.html', error=error)
        if dbpw.user_exists(user.lower()):
            error = user + ' already exists.'
            logging.warning(error)
            return render_template('add_user.html', error=error)

        if len(password) < 8:
            error = 'Password too short for  user ' + user
            logging.warning(error)
            return render_template('add_user.html', error=error)
    else:
        error = 'Invalid request.'
        return render_template('add_user.html', error=error)


    dbpw.update(user, password, fullname, admin) # update or set a new password
    info = 'User ' + user + ' added.'
    logging.info(info)

    # go back to login page if auth fails
    return render_template('add_user.html', info=info)


@app.route('/upload')
def upload(msg=""):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('upload.html')


@app.route('/guest_upload/<uuid>')
def guest_upload(uuid):
    """ Link was clicked for an guest file upload.  Check db to make sure
		it is valid and hasn't expired.
    """
    #TODO:  validate session
    #session.isValidSession(uuid) 
    return render_template('guest_upload.html', session_id=uuid)


@app.route('/generate_upload_link')
def generate_upload_link():
    """Generate a link someone can use to upload a file to you.  Uploading 
	with this link does not require an account or authentication

    Generate a UUID and save in the DB with an expiration date and the user generating (recipient of the uploaded file.  This UUID is part of the URL given to the friend for uploading.  

    Create a path $UPLOAD_PATH/user/uuid/filename to store the uploaded file.  
       
    When owner logs in, show files uploaded since last login.

    create table if not exists files (uuid unique, user, path, expiration 
    integer)
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    uuid = str(uuid4())

    upload_url = url_for('guest_upload', uuid=uuid, _external=True)

    # Store upload link with the user's email addr
    logging.info('Storing session %s for %s.' % (uuid, session.get('username')))
    dbsession.add_session(session.get('username'), uuid)

    return render_template('upload_link.html', upload_url=upload_url)


@app.route('/login', methods=['GET', 'POST'])
def login():

    #TODO: scrub input for valid chars
    #TODO: record last login for user so we can display new files uploaded for the user
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if dbpw.check(username, password):
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['fullname'] = dbpw.get_fullname(username)
	    logging.info('%s logged in. isAdmin %d Fullname %s.' % 
                (username, dbpw.isAdmin(username), session['fullname']))

            # Store in a client cookie so we can use it in the html templates
            # Don't rely on the client cookie for authorization.
            session['admin'] = dbpw.isAdmin(session['username'])

            return redirect(url_for('upload'))
        else:
            error = 'Invalid username or password'

    # go back to login page if auth fails
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    logging.info(get_loggedon_user() + ' logged out.')

    """Remove all session information"""
    session.pop('username', None)
    session.pop('admin', None)
    session.pop('logged_in', None)
    
    # flash('You were logged out')
    return redirect(url_for('thankyou'))


@app.route('/thankyou')
def thankyou():
    return render_template('logged_out.html')


def get_loggedon_user():
    if 'username' in session:
        return escape(session['username'])
    else:
	return None


@app.route('/download/')
@app.route('/download/<path:dirname>/<path:filename>')
def download(dirname, filename):
    
    if '..' in dirname  or dirname.startswith('/'):
        abort(404)
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    # Just in case
    filename = secure_filename(filename)
    dirname  = secure_filename(dirname)

    path = safe_join(DOWNLOAD_DIR, dirname)
    path = safe_join(path, filename)
    path = os.path.abspath(path)

    logging.info('Logged in as %s' % get_loggedon_user())

    if os.path.isfile(path):
        return send_file(path)
    else:
        abort(404)


@app.route('/complete_upload', methods=['GET', 'POST'])
def complete_upload():
    """
    This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
       <input name="file_1" type="file">
       The DOWNLOAD_DIR is the directory where the file will be written.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try: # Windows needs stdio set for binary mode.
        import msvcrt
        msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
        msvcrt.setmode (1, os.O_BINARY) # stdout = 1
    except ImportError:
        pass

    debug_msg = ''

    if request.method == 'POST':
        f = request.files['file']

        # Construct a path using unix time
        unixtime = str(int(time()))
        s_filename = secure_filename(f.filename)
        save_path = os.path.join(DOWNLOAD_DIR, unixtime, s_filename)

        # Create the directory
        dirname = os.path.dirname(save_path)
        if not os.path.exists(dirname): os.makedirs(dirname)

        try:
            f.save(save_path)
            f.close()
        except:
            return writeHtmlTemplate('Upload Failed', '')

        #debug_msg = 'filename: ' + filename + '\n'

        download_path = unixtime + '/' + s_filename
        file_url = url_for('download', _external=True) + download_path
    else:
        return render_template('complete_upload.html', error='Failed')

    return render_template('complete_upload.html', file_url=file_url)


#@app.route('/guest_upload_complete?session_id=<session_id>', methods=['GET', 'POST'])
@app.route('/guest_upload_complete/<session_id>', methods=['GET', 'POST'])
def guest_upload_complete(session_id):
    """
    This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
       <input name="file_1" type="file">
       The DOWNLOAD_DIR is the directory where the file will be written.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """

    logging.info('Guest upload complete for %s.' % session_id)

    try: # Windows needs stdio set for binary mode.
        import msvcrt
        msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
        msvcrt.setmode (1, os.O_BINARY) # stdout = 1
    except ImportError:
        pass

    debug_msg = ''

    if request.method == 'POST':
        f = request.files['file']

        # Construct a path using unix time
        unixtime = str(int(time()))
        s_filename = secure_filename(f.filename)
        save_path = os.path.join(DOWNLOAD_DIR, unixtime, s_filename)

        # Create the directory
        dirname = os.path.dirname(save_path)
        if not os.path.exists(dirname): os.makedirs(dirname)

        try:
            f.save(save_path)
            f.close()
            logging.info('Guest upload complete for %s' % save_path)
        except:
            return writeHtmlTemplate('Upload Failed', '')
            logging.error('Guest upload failed for %s' % save_path)

        download_path = unixtime + '/' + s_filename
        file_url = url_for('download', _external=True) + download_path
    else:
        return render_template('complete_upload.html', error='Failed')

    # get session_id for the upload.  Store file with session id in db.  Notify user the upload is available.
    user = dbsession.get_session_user(session_id)
    email = user
    dbsession.add_file(session_id, save_path)
    logging.info('Add file %s to session %s.' % (save_path, session_id))
    #assert app.debug == False, "Don't panic! You're here by request of debug()"

    # TODO: send email to user

    return render_template('guest_upload_complete.html', 
               email=user, filename=f.filename)


if __name__ == '__main__':
    app.run()




