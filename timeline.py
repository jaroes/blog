from blogpage.db import get_db

paged_by_set = {
    'global': 'select entries from metadata where id = 1',
    'profile': 'select entries from profile where id = %s',
    'post': 'select commments from post where id = %s'
}

pestructure = {
    'base': 'select p.id, p.title, p.content, p.last_modified, u.username from post p inner join user u ',
    'one': 'where p.created_by = u.username and p.id = %s',
    'of': 'on p.created_by = u.id and u.username = %s and p.last_modified > %s and p.last_modified < %s order by p.last_modified ',
    'all': 'on p.created_by = u.id and p.last_modified > %s and p.last_modified < %s order by p.last_modified ',
    'desc': 'desc limit 10',
    'asc': 'asc limit 10'
}

cestructure = {
    'base': 'select c.id, c.created_at, c.comment_to, c.content, u.username from comment c inner join user u',
    'one': 'where c.created_by = u.id and u.id = %s',
    'of': 'where c.created_by = u.id and c.comment_to = %s order by c.created_at limit 1',
    'all': 'where c.created_by = u.id and c.comment_to = %s and c.created_at > %s and c.created_at < %s order by c.created_at limit 10'  
}
    
def getpost_one(id):
    db, c = get_db()
    c.execute(
        '''
        select p.id, p.title, p.content, p.last_modified, \
        u.username from post p inner join user u \
        where p.created_by = u.id and p.id = %s
        ''', (id, )
    )
    return c.fetchone()

def getpost_profile(profile_name, limit_d, limit_t, way):
    db, c = get_db()
    c.execute(
        pestructure['base'] + pestructure['of'] + pestructure[way],
        (profile_name, limit_d, limit_t)
    )
    return c.fetchall()

def getpost_all(limit_t, limit_d, way):
    db, c = get_db()
    c.execute(
        pestructure['base'] + pestructure['all'] + pestructure[way],
        (limit_d, limit_t)
    )
    return c.fetchall()



def getcom(id):
    db, c = get_db()
    c.execute(cestructure['base'] + cestructure['one'], id)
    return c.fetchone()

def getcom(post_id):
    db, c = get_db()
    c.execute(
        pestructure['base'] + pestructure['of'],
        post_id
    )
    return c.fetchall()

def getcom(post_id, limit_t, limit_d):
    db, c = get_db()
    c.execute(
        pestructure['base'] + pestructure['all'],
        post_id, limit_d, limit_t
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
    if next is not None:
        if next['entries'] > pag:
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
    if next is not None:
        if next['entries'] > pag:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi