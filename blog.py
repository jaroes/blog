from flask import (
    Blueprint, blueprints, flash, g, redirect,
    render_template, request,
    url_for
)

from werkzeug.exceptions import abort
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
        '''
        select p.id, p.title, p.content, p.created_by, u.username \
        from post p join user u on p.created_by = u.id where \
        created_by = %s limit 5
        ''', (g.user['id'], )
    )
    posts = cursor.fetchall() 
    return render_template('blog/index.html', posts=posts, next=pages)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        error = None
        title = request.form['title']
        title = None
        content = request.form['content']
        author = g.user['id']
        db, cursor = get_db()

        if title is None or content is None:
            flash('Rellena todos los campos!')
        else:
            cursor.execute(
                'insert into post (created_by, title, content) values (%s, %s, %s)',
                (author, title, content)
            )
            db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')



    
