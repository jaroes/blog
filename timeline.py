from blogpage.db import get_db

paged_by_set = {
    'global': 'select entries from metadata where id = 1',
    'profile': 'select entries from profile where id = %s',
    'post': 'select comments from post where id = %s',
    'pf': 'select p.comments from profile p join user u where u.username = %s'
}

pestructure = {
    'base': 'select p.id, p.title, p.content, p.last_modified, u.username, if(p.created_by = %s, True, Null) as post_owner from post p inner join user u ',
    'one': 'where p.created_by = u.username and p.id = %s',
    'of': 'on p.created_by = u.id and u.username = %s and p.last_modified > %s and p.last_modified < %s order by p.last_modified ',
    'all': 'inner join comment c on p.created_by = u.id and p.last_modified > %s and p.last_modified < %s order by p.last_modified ',
    'desc': 'desc limit 10',
    'asc': 'asc limit 10'
}

cestructure = {
    'base': 'select c.created_by, c.created_at, c.commented_to, c.content, u.username',
    'one': ', p.title from comment c join user u join post p where p.id = c.commented_to and c.id = %s',
    'of': ', p.title from comment c join user u join post p where u.id = c.created_by, and u.id = %s and p.id = c.commented_to and c.created_by > %s and c.created_by < %s order by c.created_at ',
    'all': 'from comment c join user u join post p where p.id = c.commented_to and p.id = 4 and c.created_by > %s and c.created_by < %s order by c.created_at '  
}


'''
query para un post

select c.created_by, c.created_at, c.commented_to, c.content, u.username,
p.title from comment c join user u join post p where p.id = c.commented_to
and c.id = 4;
'''


'''
query para traerme todos los comentarios de un profile

select c.created_by, c.created_at, c.commented_to, c.content, u.username,
p.title from comment c join user u join post p where u.id = c.created_by,
and u.id = 1 and p.id = c.commented_to;
'''    


'''
query para traerme todos los comentarios de un post

select c.created_by, c.created_at, c.commented_to, c.content, 
u.username from comment c join user u join post p where p.id = 
c.commented_to and p.id = 4 order by created_by desc limit 10; 
'''

'''
limit_d = '1999-01-01 00:00:00'
limit_t = '2999-01-01 00:00:00'
'''

'''
select c.created_by, c.created_at, c.commented_to, c.content, 
u.username from comment c join user u join post p where 
p.id = c.commented_to and p.id = 4 and c.created_by > "" and 
c.created_by < "" order by c.created_at desc limit 10;
'''

def getpost_one(current_user, id):
    db, c = get_db()
    c.execute(
        '''
        select p.id, p.title, p.content, p.last_modified, \
        u.username, if(p.created_by = %s, True, Null) as \
        post_owner from post p inner join user u \
        where p.created_by = u.id and p.id = %s
        ''', (current_user, id)
    )
    return c.fetchone()

def getpost_profile(current_user, profile_name, limit_d, limit_t, way):
    db, c = get_db()
    c.execute(
        pestructure['base'] + pestructure['of'] + pestructure[way],
        (current_user, profile_name, limit_d, limit_t)
    )
    return c.fetchall()


def getpost_all(current_user ,limit_t, limit_d, way):
    db, c = get_db()
    c.execute(
        '''
        select p.id, p.title, p.content, p.last_modified, \
        u.username, if(p.created_by = %s, True, Null) as \
        post_owner from post p inner join user u on \
        p.created_by = u.id and \
        p.last_modified > %s and p.last_modified < %s \
        order by p.last_modified
        '''+ pestructure[way], (current_user, limit_d, limit_t)
    )
    return c.fetchall()


def getcom_one(current_user ,id):
    db, c = get_db()
    c.execute(
        '''
        select c.commented_by, c.commented_at, c.commented_to, \
        c.comm, u.username, p.title, if(commented_by = %s, True, Null) \
        as comment_owner from comment c join \
        user u join post p where p.id = c.commented_to and commented_by = u.id and c.id = %s;
        ''', (current_user, id)
    ) 
    return c.fetchone()

def getcomm_post(current_user, post_id, limit_d, limit_t, way):
    db, c = get_db()
    c.execute(
        '''
        select c.id, c.commented_by, c.commented_at, c.commented_to, \
        c.comm, u.username, if(commented_by = %s, True, Null) as \
        comment_owner from comment c join user u \
        join post p where p.id = c.commented_to and p.id = %s \
        and c.commented_by = u.id \
        and c.commented_at > %s and c.commented_at < %s \
        order by c.commented_at 
        ''' + pestructure[way], (current_user, post_id, limit_d, limit_t)
    )
    return c.fetchall()

def getcomm_profile(current_user, profile_id, limit_d, limit_t, way):
    db, c = get_db()
    print(current_user)
    c.execute(
        '''
        select c.id, c.commented_by, c.commented_at, c.commented_to, \
        c.comm, u.username, if(commented_by = %s, True, Null) as comment_owner from comment c join user u \
        join post p where p.id = c.commented_to and u.id = %s \
        and c.commented_at > %s and c.commented_at < %s \
        order by c.commented_at 
        ''' + pestructure[way], (current_user, profile_id, limit_d, limit_t)
    )
    return c.fetchall()


def getcomm_user(current_user, user_name, limit_d, limit_t, way):
    db, c = get_db()
    c.execute(
        '''
        select c.id, c.commented_by, c.commented_at, c.commented_to, \
        c.comm, u.username, p.title, if(commented_by = %s, True, Null) \
        as comment_owner from comment c join user u \
        join post p where c.commented_by = u.id and u.username = %s \
        and p.id = commented_to and c.commented_at > %s and \
        c.commented_at < %s order by c.commented_at 
        ''' + pestructure[way], (current_user, user_name, limit_d, limit_t)
    )
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