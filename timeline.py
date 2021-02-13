from flask import g
from blogpage.db import get_db
from datetime import datetime

paged_by_set = {
    'global': 'select entries from metadata where id = 1',
    'profile_posts': 'select p.entries from profile p join user u on p.id = u.id and u.username = %s',
    'post': 'select comments from post where id = %s',
    'profile_comments': 'select p.comments from profile p join user u on p.id = u.id and u.username = %s'
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


new_po = dict(
    base='''
        select p.id, p.title, p.content, p.last_modified, \
        u.username, if(p.created_by = %s, True, Null) \
        as post_owner from post p inner join user u 
        ''',
    main='''
        on p.created_by = u.id order by \
        p.last_modified desc limit %s, %s
        ''',
    profile='''
        on p.created_by = u.id and u.username = %s \
        order by p.last_modified desc limit %s, %s
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
    np=new_po,
    desc='desc limit 10',
    asc='asc limit 10'
)





def new_getseveral(tipo, which, current_user, page, per_page=10, id=None):
    db, c = get_db()
    to_fetch = 'base'
    if which == 'post' and tipo == 'comment':
        to_fetch = 'unique'

    sql = data[tipo][to_fetch] + data[tipo][which]
    if id is None:
        c.execute( sql,(current_user, page, per_page) )
    else:
        c.execute( sql,(current_user, id, page, per_page) )
    return c.fetchall()





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

def needs_pag(pages_for, pag, id=None):
    db, c = get_db()
    
    if id is None:
        c.execute (paged_by_set[pages_for])
    else:
        c.execute (paged_by_set[pages_for], (id, ))
    next = c.fetchone()
    
    navi = {
        'next': None,
        'back': None
    }
    
    consult_for = 'entries'
    if pages_for == 'profile_comments' or pages_for == 'post':
        consult_for = 'comments'
    if next is not None:
        if next[consult_for] > pag + 1:
            navi['next'] = True
        if pag > 0:
            navi['back'] = True
    
    return navi


class get_from_db:
    def __init__(self):
        self.data = dict(
            post = po,
            comments = co,
            desc='desc limit 10',
            asc='asc limit 10'
        )
    
    def getone(self, tipo, current_id, id):
        db, c = get_db()
        sql = self.data[tipo]['base'] + self.data[tipo]['one']
        c.execute(sql, (current_id, id))
        return c.fetchone()

    def getseveral(self, tipo, which, current_user, limit_d, limit_t, way, id=None):
        db, c = get_db()
        to_fetch = 'base'
        if which == 'post' and tipo == 'comment':
            to_fetch = 'unique'

        sql = self.data[tipo][to_fetch] + self.data[tipo][which] + self.data[way]
        if id is None:
            c.execute(sql, (current_user, limit_d, limit_t))
        else:
            c.execute(sql, (current_user, id, limit_d, limit_t))
        
        return c.fetchall()



'''
class Posts:
    def __init__(self, current_user, for_what, pilin=None):
        self.context=for_what
        self.current_user=current_user
        self.relatives = dict(
            next=None,
            back=None
        )
        if pilin is None:
            print('voy yo')
            self.entries=self.get_entries()
        else:
            self.entries=self.get_entries(pilin)
        

    def get_entries(self, rios=0):
        db, c = get_db()
        print('--------\n{}\n-------------'.format(type(rios)))
        if rios == 0:
            print('voy yo 2')
            c.execute(paged_by_set['global'])
        else:
            print('no sé wn')
            c.execute(paged_by_set['profile_post'], (rios, ))
        entradas = c.fetchone()
        print(entradas)
        return entradas['entries']

    def getone(self, id):
        return get_from_db.getone('p', self.current_user, id)

    def getseveralin(self, page, paged_by=10):
        outt = new_getseveral(
            'np', 
            self.context, 
            self.current_user, 
            page*10, 
            paged_by
        )
        print('pagina: {}'.format(page))
        print('paginass: {}'.format(self.entries))
        
        if page > 0:
            self.relatives['back'] = True
        if (page+1) * paged_by < (self.entries*10):
            self.relatives['next'] = True
        return outt, self.relatives

'''



class From_DB:
    def __init__(self):
        self.user=g.user['id']
        self.data = dict(
            post=new_po,
            comment=co
        )
    
    def getone(self, tipo, id):
        db, c = get_db()
        sql = self.data[tipo]['base'] + self.data[tipo]['one']
        c.execute(sql, (self.user, id))
        return c.fetchone()

    def new_getseveral(self, tipo, which, page, per_page=10, id=None):
        db, c = get_db()
        to_fetch = 'base'
        print(id)
        if which == 'post' and tipo == 'comment':
            to_fetch = 'unique'

        sql = self.data[tipo][to_fetch] + self.data[tipo][which]
        if id is None:
            c.execute( sql,(self.user, page, per_page) )
        else:
            c.execute( sql,(self.user, id, page, per_page) )
        print('salimo bien?')
        return c.fetchall()


class Posts(From_DB):
    def __init__(self, Post_to, id=None):
        super().__init__()
        self.mode=Post_to
        self.db, self.c = get_db()
        self.total=self.get_entries(id)
        self.relatives = dict(
            next=None,
            back=None
        )

    def get_entries(self, id):
        if id is None:
            print('voy yo 2')
            self.c.execute(paged_by_set['global'])
        else:
            print('no sé wn')
            self.c.execute(paged_by_set['profile_posts'], (id, ))
        entradas = self.c.fetchone()
        print(entradas)
        return entradas['entries']


    def get_a_post(self, id):
        return super().getone('post', id)
    
    def get_posts(self, page, username, paged_by=10):
        posts = super().new_getseveral(
            'post', self.mode, page*10, paged_by, username
        )
        print('page en 1 es {}'.format(page))
        if page > 0:
            self.relatives['back'] = True
        if (page+1) * paged_by < (self.total*10):
            self.relatives['next'] = True
        print(self.relatives)
        print('page+1*paged_by={}'.format((page+1) * paged_by))
        print('total={}'.format(self.total*10))
        return posts, self.relatives, len(posts), self.user

    def delete(self, id):
        self.c.execute(
            '''
            delete from post where \
            id = %s and created_by = \
            %s
            ''', (id, self.user)
        )
        self.c.execute(
            '''
            update profile set entries = \
            entries - 0.1 where id = %s
            ''', (self.user)
        )
        self.c.execute(
            '''
            update metadata set entries = \
            entries - 0.1 where id = 1
            '''
        )
        self.db.commit()

    def edit(self, id, title, content):
        self.c.execute(
            '''
            update post set content = %s, title = %s, \
            last_modified = %s where id = %s and created_by = %s
            ''', (content, title, datetime.now(), id, self.user)
        )
        self.db.commit()

    def create(self, title, content):
        self.c.execute(
            'insert into post (created_by, title, content) values (%s, %s, %s)',
            (self.user, title, content)
        )
        self.c.execute(
            'update profile set entries = entries + 0.1 where id = %s',
            (self.user, )
        )
        self.c.execute(
            'update metadata set entries = entries + 0.1 where id = 1'
        )
        self.db.commit()


class Comments(From_DB):
    def __init__(self, Post_to):
        super().__init__()
        self.mode=Post_to
        self.total=self.get_comments()
        self.relatives = dict(
            next=None,
            back=None
        )
        self.db, self.c = get_db()

    def get_entries(self, id=None):
        if id is None:
            print('voy yo 2')
            self.c.execute(paged_by_set['profile_comment'])
        else:
            print('no sé wn')
            self.c.execute(paged_by_set['post_comments'], (id, ))
        entradas = self.c.fetchone()
        return entradas['comments']


    def get_a_comment(self, id):
        return super().getone('comment', id)
    
    def get_posts(self, page, paged_by=10):
        posts = super().new_getseveral(
            'comment', self.mode, page, paged_by
        )
        if page > 0:
            self.relatives['back'] = True
        if (page+1) * paged_by < (self.entries*10):
            self.relatives['next'] = True
        return posts, self.relatives, len(posts), self.user

    def delete(self, id):
        self.c.execute(
            '''
            delete from post where \
            id = %s and created_by = \
            %s
            ''', (id, self.user)
        )
        self.c.execute(
            '''
            update profile set entries = \
            entries - 0.1 where id = %s
            ''', (self.user)
        )
        self.c.execute(
            '''
            update metadata set entries = \
            entries - 0.1 where id = 1
            '''
        )
        self.db.commit()

    def edit(self, id, title, content):
        self.c.execute(
            '''
            update post set content = %s, title = %s, \
            last_modified = %s where id = %s and created_by = %s
            ''', (content, title, datetime.now(), id, self.user)
        )
        self.db.commit()

    def create(self, title, content):
        self.c.execute(
            'insert into post (created_by, title, content) values (%s, %s, %s)',
            (self.user, title, content)
        )
        self.c.execute(
            'update profile set entries = entries + 0.1 where id = %s',
            (self.user, )
        )
        self.c.execute(
            'update metadata set entries = entries + 0.1 where id = 1'
        )
        self.db.commit()
        

        