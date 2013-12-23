# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, make_response


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/flaskr.db',
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_last_post_id():
    db = get_db()
    cur = db.execute('select max(id) from entries')
    return cur.fetchall()[0]['max(id)']

@app.route('/set_cookie')
def cookie_insertion():
    redirect_to_index = redirect(url_for('show_entries'))
    response = app.make_response(redirect_to_index )  
    response.set_cookie('test_cookie',value='test')
    return response

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select text from entries order by id desc')
    entries = cur.fetchall()
    cookie_insertion()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    redirect_to_index = redirect(url_for('show_entries'))
    response = app.make_response(redirect_to_index )  
    
    last_post_id = get_last_post_id()
    my_last_post_id = int(request.cookies.get('my_last_post_id') 
                          if request.cookies.get('my_last_post_id') is not None 
                          else 0)
    if my_last_post_id == last_post_id and last_post_id is not None:
        flash('let someone else have a turn before you contribute again!')
        return redirect(url_for('show_entries'))
    else:
        db = get_db()
        db.execute('insert into entries (text) values (?)',
                 [request.form['text']])
        db.commit()
        flash('thank you!')
        with open('poem','a') as poemfile:
            poemfile.write(request.form['text']+'\n')
        response.set_cookie('my_last_post_id',value=str(get_last_post_id()))
    return response

if __name__ == '__main__':
    init_db()
    app.run()
