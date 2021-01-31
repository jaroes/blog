from flask import (
    Blueprint, blueprints, flash, g, redirect,
    render_template, request,
    url_for
)

from werkzeug import exceptions
from blogpage import auth
from blogpage.auth import login_required
from blogpage.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
@login_required
def index():
    pages = False
    author = None
    db, cursor = get_db()

    cursor.execute (
        'select * from post where id = %s limit 1', (g.user['id'], ) 
    )
    if cursor.fetchone() is None:
        return 'ningun post'
    else:
        cursor.execute (
            'select * from post where created_by = %s order by id desc limit 6', (g.user['id'], )
        )
        
        posts = cursor.fetchall()
        if len(posts) == 6:
            pages = True
        
        return render_template('blog/index.html', posts=posts, next=pages, author=g.user['username'])


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        error = None
        title = request.form['title']
        content = request.form['content']
        author = g.user['id']
        db, cursor = get_db()

        if title is None or content is None:
            return 'Rellena todos los campos!'
        
        cursor.execute(
            'insert into post (created_by, title, content) values (%s, %s, %s)',
            (author, title, content)
        )
        db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')



    