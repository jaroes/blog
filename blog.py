from flask import (
    Blueprint, blueprints, flash, g, redirect,
    render_template, request,
    url_for
)

from werkzeug import exceptions
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
        
        return render_template('blog/blog.html', posts=posts, next=pages, author=g.user['username'])

    