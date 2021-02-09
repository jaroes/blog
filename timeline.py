from blogpage.db import get_db

paged_by_set = {
    'global': 'select entries from metadata where id = 1',
    'profile': 'select entries from profile where id = %s',
    'post': 'select comments from post where id = %s',
    'pf': 'select p.comments from profile p join user u where u.username = %s'
}

po = dict(
    base='''
        select p.id, p.title, p.content, p.last_modified, \
        u.username, if(p.created_by = %s, True, Null) \
        as post_owner from post p inner join user u 
        ''',
    main='''
        on p.created_by = u.id and \
        p.last_modified > %s and p.last_modified < %s \
        order by p.last_modified
        ''',
    profile='''
        on p.created_by = u.id and u.username = %s and \
        p.last_modified > %s and p.last_modified < %s \
        order by p.last_modified
        ''',
    one='''
        where p.created_by = u.id and p.id = %s
        '''
)

co = dict(
    base='''
        select c.id, c.commented_by, c.commented_at, \
        c.commented_to, c.comm, u.username, p.title, \
        if(commented_by = %s, True, Null) as \
        comment_owner from comment c join \
        user u join post p 
        ''',
    unique='''
        select c.id, c.commented_by, c.commented_at, \
        c.commented_to, c.comm, u.username, if(commented_by \
        = %s, True, Null) as \ comment_owner from comment \
        c join user u join post p 
        ''',
    post='''
        where p.id = c.commented_to and p.id = %s and \
        c.commented_by = u.id and c.commented_at > %s \
        and c.commented_at < %s order by c.commented_at 
        ''',
    user='''
        where c.commented_by = u.id and u.username = %s \
        and p.id = commented_to and c.commented_at > %s and \
        c.commented_at < %s order by c.commented_at 
        ''',
    one='''
        where p.id = c.commented_to and \
        commented_by = u.id and c.id = %s
        '''
)

data = dict(
    p=po,
    c=co,
    desc='desc limit 10',
    asc='asc limit 10'
)

def getone(tipo, current_id, id):
    db, c = get_db()
    sql = data[tipo]['base'] + data[tipo]['one']
    c.execute(sql, (current_id, id))
    return c.fetchone()

def getseveral(tipo, which, current_user, limit_d, limit_t, way, id=None):
    db, c = get_db()
    to_fetch = 'base'
    if which == 'post' and tipo == 'comment':
        to_fetch = 'unique'

    sql = data[tipo][to_fetch] + data[tipo][which] + data[way]
    if id is None:
        c.execute(sql, (current_user, limit_d, limit_t))
    else:
        c.execute(sql, (current_user, id, limit_d, limit_t))
    
    return c.fetchall()


def getpag_i(fr, pag):
    db, c = get_db()
    c.execute (paged_by_set[fr])
    next = c.fetchone()
    navi = {
        'next': None,
        'back': None
    }
    print('-------------------------')
    print(next['entries'])
    print('-------------------------')
    if next is not None:
        if next['entries'] > pag + 1:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi


def getpag(fr, id, pag):
    db, c = get_db()
    c.execute (paged_by_set[fr], (id, ))
    next = c.fetchone()
    navi = {
        'next': None,
        'back': None
    }
    print('-------------------------')
    print(next['entries'])
    print('-------------------------')

    if next is not None:
        if next['entries'] > pag + 1:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi

def getpag_post(post_id, pag):
    db, c = get_db()
    c.execute (paged_by_set['post'], (post_id, ))
    next = c.fetchone()
    navi = {
        'next': None,
        'back': None
    }
    print('-------------------------')
    print(next['comments'])
    print('-------------------------')

    if next is not None:
        if next['comments'] > pag + 1:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi

def getpag_profile(post_id, pag):
    db, c = get_db()
    c.execute (paged_by_set['pf'], (post_id, ))
    next = c.fetchone()
    navi = {
        'next': None,
        'back': None
    }
    print('-------------------------')
    print(next['comments'])
    print('-------------------------')

    if next is not None:
        if next['comments'] > pag + 1:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi
