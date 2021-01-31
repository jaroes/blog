import functools
from flask import (
    Blueprint, flash, g,
    render_template, request,
    url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from blogpage.db import get_db

bp=Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        db, c = get_db()
        error = None
        c.execute (
            'select id from user where email = %s', (email, )
        )

        if not email:
            error='Email es requerido'
        if not password:
            error='Contraseña es requerida'
        elif c.fetchone() is not None:
            error = 'El correo {} se encuentra registrado '.format(email)
        
        if error is None:
            c.execute(
                'insert into user (email, password) values (%s, %s)',
                (email, generate_password_hash(password))
            )
            c.execute(
                'insert into profile (username) values (%s)',
                (username, )
            )
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('base.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
                'select * from user where username = %s', (email, )
                )
        user = c.fetchone()
        
        if email is None:
            error = 'Email y/o contraseña invalida'
        elif not check_password_hash(user['password'], password):
            error = "Usuario y/o contraseña invalida"

        if error is None:
            #por si acaso limpiaresmo el dato de
            #session y pillaresmo el id de DB
            session.clear()
            session['user_id'] = user['id']
            return  redirect(url_for('auth.register'))

        flash(error)
    return render_template('auth/login.html')