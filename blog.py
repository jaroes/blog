from flask import (
    Blueprint, blueprints, flash, g, redirect,
    render_template, request,
    url_for
)

from werkzeug.exceptions import abort
from blogpage import auth
from blogpage.auth import login, login_required
from blogpage.db import get_db
from blogpage.timeline import getpost, getcom, getpag

from datetime import datetime

bp = Blueprint('blog', __name__)

@bp.route('/')
@bp.route('/<int:pag>', methods=['GET', 'POST'])
@login_required
def index(pag = 0):
    limit_d = '1999-01-01 00:00:00'
    limit_t = '2999-01-01 00:00:00'
    way = 'desc'
    if request.method == 'POST':
        try:
            if request.form['limit_d'] is not None:
                limit_d = request.form['limit_d']
        except:
            way = 'desc'

        try:
            if request.form['limit_t'] is not None:
                limit_t = request.form['limit_t']
        except:
            way = 'asc'

    posts = getpost(limit_t, limit_d, way)

    if way == 'asc':
        posts.reverse()
    
    return render_template(
        'blog/index.html', 
        posts=posts, 
        name=g.user['username'],
        navi=getpag('global', pag),
        pag=pag,
        num=len(posts)
    )
    


@bp.route('/profile/<usr>/<int:pag>', methods=['GET', 'POST'])
def profile(usr, pag):
    author = True
    sig = None
    db, cursor = get_db()

    owner = {
        'id': g.user['id'],
        'username': g.user['username']
    }
    if owner['username'] != usr:
        cursor.execute(
            '''
            select id, username, entries from user where username = %s
            ''', (usr, )
        )
        owner = cursor.fetchone()
        if owner is None:
            return redirect(url_for('blog.index'))
        author = None

    if request.method == 'POST':
        next = request.form['next']
        cursor.execute (
            'select * from post where created_by = %s and id < %s order by id desc limit 5', (owner['id'], next)
        )
    else:
        cursor.execute (
            '''
            select p.id, p.title, p.content, p.created_by, \
            p.last_modified from post p where \
            p.created_by = %s order by p.id desc limit 5
            ''', (owner['id'], )
        )
    
    posts = cursor.fetchall()

    
    cursor.execute(
        '''
        select p.birthday, p.bio, \
        p.direction, p.pfp, p.anniversary, p.entries \
        from profile p where p.id = %s
        ''', (owner['id'], )
    )
    user_info = cursor.fetchone()
    if user_info['entries'] > pag + 1:
        sig = True
        

    return render_template(
        'blog/profile.html',
        posts=posts,
        pf=user_info,
        name=owner['username'],
        au=author,
        usern=g.user['username'],
        si = sig,
        nimpi = len(posts),
        yupi = pag + 1
    )



@bp.route('/profile')
@login_required
def profile_user():
    pages = False
    author = None
    db, cursor = get_db()

    cursor.execute (
        '''
        select p.id, p.title, p.content, p.created_by, \
        p.last_modified from post p where \
        created_by = %s order by p.last_modified desc limit 5
        ''', (g.user['id'], )
    )
    posts = cursor.fetchall()

    
    cursor.execute(
        '''
        select p.birthday, p.bio, \
        p.direction, p.pfp, p.anniversary \
        from profile p where p.id = %s
        ''', (g.user['id'], )
    )
    user_info = cursor.fetchone()
    return render_template(
        'blog/profile.html',posts=posts,
        pf=user_info,name=g.user['username'], au=True
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
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
            cursor.execute(
                'update profile set entries = entries + 0.2 where id = %s', (g.user['id'], )
            )
            cursor.execute(
                'update metadata set entries = entries + 0.2 where id = 1'
            )
            db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


@bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    db, cursor = get_db();
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute(
            '''
            update post set content = %s, title = %s, \
            last_modified = %s where id = %s and created_by = %s
            ''', (content, title, datetime.now(), post_id, g.user['id'])
        )
        db.commit()
        return redirect(url_for('blog.index'))
    
    cursor.execute(
        '''
        select p.id, p.title, p.content, p.created_by \
        from post p where p.created_by = %s and p.id = %s
        ''', (g.user['id'], post_id)
    )
    pst = cursor.fetchone()
    if pst is None:
        flash('No puedes editar post que no sea tuyos!!')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/edit.html', posts=pst, name=g.user['id'])


@bp.route('/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete(post_id):
    db, cursor = get_db()
    if request.method == 'POST':
        cursor.execute(
            '''
            delete from post where \
            id = %s and created_by = \
            %s
            ''', (post_id, g.user['id'])
        )
        cursor.execute(
                'update profile set entries = entries - 0.2 where id = %s', (g.user['id'], )
        )
        cursor.execute(
                'update metadata set entries = entries - 0.2 where id = 1'
        )
        db.commit()
        return redirect(url_for('blog.index'))
    cursor.execute(
        '''
        select p.id, p.title, p.content, p.created_by \
        from post p where p.created_by = %s and p.id = %s
        ''', (g.user['id'], post_id)
    )
    posts = cursor.fetchone()
    if posts is None:
        flash('No puedes eliminar el post de alguien más')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/delete.html', post=posts)


@bp.route('/deleteuser', methods=['GET', 'POST'])
@login_required
def deleteuser():
    if request.method == 'POST':
        db, cursor = get_db()
        deluser = [
            'delete from post where created_by = %s',
            'delete from user where id = %s',
            'delete from profile where id = %s'
        ]
        for query in deluser:
            cursor.execute(query, (g.user['id'], ))
        db.commit()
        return redirect(url_for('auth.logout'))
    return render_template('blog/deleteuser.html')


@bp.route('/editprofile', methods=['GET', 'POST'])
@login_required
def edituser():
    db, cursor = get_db()
    if request.method == 'POST':
        img = request.form['img']
        nm = request.form['name']
        bio = request.form['bio']
        dir = request.form['dir']
        cumple = request.form['cumple']
        cursor.execute(
            '''
            update profile set bio = %s, \
            direction = %s, pfp = %s, \
            birthday = %s where id = %s
            ''', (bio, dir, img, cumple, g.user['id'])
        )
        cursor.execute(
            '''
            update user set username = %s \
            where id = %s
            ''', (nm, g.user['id'])
        )
        db.commit()
        return redirect(url_for('blog.profile_user'))
    cursor.execute(
        '''
        select p.birthday, p.bio, \
        p.direction, p.pfp, p.anniversary \
        from profile p where p.id = %s
        ''', (g.user['id'], )
    )
    user_info = cursor.fetchone()
    return render_template(
        'blog/editprofile.html', pf=user_info,
        name=g.user['username']
    )



    
