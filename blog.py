from flask import (
    Blueprint, blueprints, flash, g, redirect,
    render_template, request,
    url_for
)

from werkzeug.exceptions import abort
from blogpage import auth
from blogpage.auth import login, login_required
from blogpage.db import get_db
from blogpage.timeline import (
    getcom, getcomm_post, getpag_post, getpost_profile, getpost_all, getpost_one,
    getpag_i, getpag
)

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

    posts = getpost_all(limit_t, limit_d, way)

    if way == 'asc':
        posts.reverse()

    print('hasta aqui sin problemas')

    return render_template(
        'blog/index.html', 
        posts=posts, 
        name=g.user['username'],
        navi=getpag_i('global', pag),
        pag=pag,
        num=len(posts)
    )
    


@bp.route('/profile')
@bp.route('/profile/<usr>', methods=['GET', 'POST'])
@bp.route('/profile/<usr>/<int:pag>', methods=['GET', 'POST'])
def profile(usr = None, pag = None):
    
    #in case an unlogged enter to profile
    if usr is None and pag is None:
        if g.user == None:
            return redirect(url_for('auth.login'))
        else:
            usr = g.user['username']
            
    pag = 0
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
    
    posts = getpost_profile(usr, limit_d, limit_t, way)
    db, cursor = get_db()
    cursor.execute(
        '''
        select p.id, p.birthday, p.bio, \
        p.direction, p.pfp, p.anniversary, p.entries, \
        u.username from profile p join user u where \
        p.id = u.id and u.username = %s
        ''', (usr, )
    )
    user_info = cursor.fetchone()

    if way == 'asc':
        posts.reverse()


    navi = getpag('profile', user_info['id'], pag)
    return render_template(
        'blog/profile.html',
        posts=posts,
        pf=user_info,
        name=g.user['username'],
        navi=navi,
        pag=pag,
        num=len(posts),
        edition=(g.user['id'] == user_info['id'])
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
                'update profile set entries = entries + 0.1 where id = %s', (g.user['id'], )
            )
            cursor.execute(
                'update metadata set entries = entries + 0.1 where id = 1'
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
    
    pst = getpost_one(post_id)
    if pst is None or pst['username'] != g.user['username']:
        flash('No puedes editar post que no sea tuyos!!')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/edit.html', posts=pst, name=g.user['username'])


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
                'update profile set entries = entries - 0.1 where id = %s', (g.user['id'], )
        )
        cursor.execute(
                'update metadata set entries = entries - 0.1 where id = 1'
        )
        db.commit()
        return redirect(url_for('blog.index'))
    
    posts = getpost_one(post_id)
    if posts is None or posts['username'] != g.user['username']:
        flash('No puedes borrar post que no sea tuyos!!')
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


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@bp.route('/post/<int:post_id>/<int:pag>', methods=['GET', 'POST'])
def view_post(post_id, pag = 0):
    post = getpost_one(post_id)
    if post is None:
        return redirect(url_for('blog.index'))
    
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
    
    comms = getcomm_post(post_id, limit_d, limit_t, way)

    if way == 'asc':
        comms.reverse()
    
    return render_template(
        'blog/post.html',
        comms = comms,
        pst = post,
        pag = pag,
        num = len(comms),
        name = g.user['username'],
        nav = getpag_post(post_id, pag)
    )
    
