# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
additional_fields = ([Field('Phone_Number',requires=IS_MATCH('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')),Field('Gender',requires=IS_IN_SET(['Male','Female']))])
user_extra_fields=[]
retailer_extra_fields = [Field('Date_Of_Birth','date')]

auth.settings.extra_fields['auth_user'] = (additional_fields + user_extra_fields + retailer_extra_fields)

auth.define_tables(username=False, signature=False)

'''
#janrain
from gluon.contrib.login_methods.rpx_account import RPXAccount

auth.settings.actions_disabled=['register','change_password','request_reset_password']
auth.settings.login_form=RPXAccount(request,
                                    api_key='04ea77ebb173add981bb84fcdff5d51b967f5cd1',
                                    domain='itproject',
                                    url='http://127.0.0.1:8000/%s/default/user/login'%request.application)
'''

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'project.teamauthentication@gmail.com'
mail.settings.login = 'project.teamauthentication@gmail.com:teamauthentication'

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')


FB_CLIENT_ID='444844902338940'
FB_CLIENT_SECRET="68b948c09d6ea20ef58492e2deb76467"

## import required modules
try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json
from facebook import GraphAPI, GraphAPIError
from gluon.contrib.login_methods.oauth20_account import OAuthAccount


## extend the OAUthAccount class
class FaceBookAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL="https://graph.facebook.com/oauth/authorize"
    TOKEN_URL="https://graph.facebook.com/oauth/access_token"

    def __init__(self):
        OAuthAccount.__init__(self, None, FB_CLIENT_ID, FB_CLIENT_SECRET,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='email,user_about_me,user_activities, user_birthday, user_education_history, user_groups, user_hometown, user_interests, user_likes, user_location, user_relationships, user_relationship_details, user_religion_politics, user_subscriptions, user_work_history, user_photos, user_status, user_videos, publish_actions, friends_hometown, friends_location,friends_photos',
                              state="auth_provider=facebook",
                              display='popup')
        self.graph = None

    def get_user(self):
        '''Returns the user using the Graph API.
        '''
        if not self.accessToken():
            return None

        if not self.graph:
            self.graph = GraphAPI((self.accessToken()))

        user = None
        try:
            user = self.graph.get_object("me")
        except GraphAPIError, e:
            session.token = None
            self.graph = None

        if user:
            if not user.has_key('username'):
                username = user['id']
            else:
                username = user['username']

            if not user.has_key('email'):
                email = '%s.fakemail' %(user['id'])
            else:
                email = user['email']    

            return dict(first_name = user['first_name'],
                        last_name = user['last_name'],
                        username = username,
                        email = '%s' %(email) )

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
