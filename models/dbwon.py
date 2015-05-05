# -*- coding: utf-8 -*-

db.define_table('category',Field('name','string'))

db.define_table('maincategory',Field('mainname','string'))

db.define_table('itemcategory',Field('name','string',requires=IS_NOT_EMPTY()),
                Field('main_category','reference maincategory',requires=IS_IN_DB(db,db.maincategory,'%(mainname)s')))

db.define_table('post',Field('category', 'reference category',readable=False,writable=False),Field('title','string',requires=IS_NOT_EMPTY()),Field('body','text',requires=IS_NOT_EMPTY()),Field('rating','integer',default=0,readable=False,writable=False),auth.signature)

db.define_table('votetracker',Field('personid', 'reference auth_user'),Field('postid','reference post'))

db.define_table('comm',Field('post','reference post',readable=False,writable=False),Field('body','text',requires=IS_NOT_EMPTY()),auth.signature)

db.define_table('itemsmain',Field('name','string',requires=IS_NOT_EMPTY()),Field('description','text',requires=IS_NOT_EMPTY()),Field('itemcategory','reference itemcategory',requires=IS_IN_DB(db,db.itemcategory,'%(name)s')), Field('Image','upload',uploadfield='picture_file',requires=[IS_NOT_EMPTY(),IS_IMAGE()]),Field('picture_file','blob'),Field('Price','float',requires=IS_NOT_EMPTY()),Field('Retailer','reference auth_user',readable=False,writable=False),Field('rating','integer',default=0,readable=False,writable=False),Field('Quantity','integer',default=1),
                Field('Quantity_sold','integer',default=0,readable=False,writable=False),auth.signature)

db.define_table('votetrackeritem',Field('personid', 'reference auth_user'),Field('itemid','reference itemsmain'))

db.define_table('commitem',Field('itemid','reference itemsmain',readable=False,writable=False),Field('body','text',requires=IS_NOT_EMPTY()),auth.signature)

db.define_table('addresses', Field('user_id', 'reference auth_user', readable=False, writable=False), Field('body', 'text', requires=IS_NOT_EMPTY()), auth.signature)

db.define_table('shophistory', Field('user_id', 'reference auth_user', readable=False, writable=False), Field('itemid','reference itemsmain'), Field('quantity','integer'), auth.signature)

db.define_table('wishlist', Field('user_id', 'reference auth_user', readable=False, writable=False), Field('itemid', 'reference itemsmain'))
