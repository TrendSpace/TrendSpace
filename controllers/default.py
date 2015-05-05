# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

"""
    http://..../[app]/default/category
    http://..../[app]/default/displaypost/args=categoryid
    http://..../[app]/default/singlepost/args=postid
    http://..../[app]/default/insertpost/args=categoryid
    http://..../[app]/default/ratingadd/args=postid
"""

def index():
    form=db(db.itemsmain).select(orderby=~db.itemsmain.rating)
    form2=db(db.itemsmain).select(orderby=~db.itemsmain.created_on)
    return locals()

@auth.requires_login()
def mailtoretailer():
    form = SQLFORM.factory(Field('Your_message_here','text',requires=IS_NOT_EMPTY())).process()
    if form.accepted:
        mail.send([request.args[0]],
              subject='User Feedback',
              reply_to=auth.user.email,
              message=form.vars.Your_message_here
              )
        redirect(URL('index'))
    return locals()

@auth.requires_login()
def feedback():
    form = SQLFORM.factory(Field('Your_Feedback_here','text',requires=IS_NOT_EMPTY())).process()
    if form.accepted:
        mail.send(['project.teamauthentication@gmail.com'],
              subject='User Feedback',
              reply_to=auth.user.email,
              message=form.vars.Your_Feedback_here
              )
    return locals()

def autorefresh():
    if request.vars.temp2 == 'Price':
            orderingby=db.itemsmain.Price
    elif request.vars.temp2 == 'Rating':
            orderingby=db.itemsmain.rating
    elif request.vars.temp2 == 'Date':
            orderingby=db.itemsmain.created_on
    if request.vars.temp3=='Ascending':
        form=db(db.itemsmain.name.like('%'+request.vars.temp+'%')).select(orderby=orderingby)
    else:
        form=db(db.itemsmain.name.like('%'+request.vars.temp+'%')).select(orderby=~orderingby)
    return ''.join([DIV(A(DIV(IMG(_src=URL('default','download',args=row.Image),_style="width:100px;height:100px;margin-left:20px;"),SPAN(" "),row.name,SPAN(" Rs."),row.Price),_href=URL('singlepostitem',args=row.id),_style="text-decoration:none;font-size:20px;"),P(""),_style="border:2px solid #FFFFFF;padding:4px;",_onMouseOut="this.style.border='2px solid #FFFFFF'",_onMouseOver="this.style.border='2px solid #003366'").xml() for row in form])

@auth.requires_login()
def userprofile():
    vals=db(db.auth_user.id==request.args(0)).select()[0]
    form=db(db.itemsmain.Retailer==request.args(0)).select()
    return locals()

@auth.requires_login()
def ratingadd():
    if len(db((db.votetracker.personid==auth.user.id)&(db.votetracker.postid==request.args(0))).select())==0:
        currating=db(db.post.id==request.args(0)).select()[0].rating
        db(db.post.id==request.args(0)).update(rating=1+currating)
        db.votetracker.insert(personid=auth.user.id,postid=request.args(0))
        session.flash="Your vote has been added"
    else:
        session.flash="You have already voted"
    redirect(URL('singlepost',args=request.args(0)))
    return locals()

@auth.requires_login()
def singlepost(): #Display a single post along with its comments
    val3=db(db.post.id==request.args(0)).select()
    db.comm.post.default=(request.args(0))
    form=SQLFORM(db.comm).process()
    return locals()

def category(): #Shows us the categories present
    val2=db(db.category).select()
    return locals()

def displaypost(): #Displays all the posts of a certain category
    val=db(db.post.category==request.args(0)).select()
    return locals()

@auth.requires_login()
def insertpost(): #Inserts a post in the certain category
    db.post.category.default=request.args(0)
    vals=SQLFORM(db.post).process()
    if vals.accepted:
        session.flash="Well Done!"
        redirect(URL('displaypost',args=request.args(0)))
    return locals()

@auth.requires_membership('Admin')
def posttable():
    valss=SQLFORM.grid(db.post)
    return locals()

@auth.requires_membership('Admin')
def addpermissions():
    gen=SQLFORM(db.auth_membership).process()
    return locals()

@auth.requires_membership('Admin')
def listitems():
    formlist=SQLFORM.grid(db.itemsmain)
    return locals()

@auth.requires_membership('Retailer')
def retaileritem():
    formlist=db(db.itemsmain.Retailer==auth.user.id).select()
    forms=SQLFORM.factory(Field('itemid','reference itemsmain',requires=IS_IN_DB(db,db.itemsmain,'%(name)s')),Field('Quantity','integer'))
    if forms.process().accepted:
        varss=forms.vars.Quantity
        qty=db(db.itemsmain.id==forms.vars.itemid).select()[0].Quantity
        db(db.itemsmain.id==forms.vars.itemid).update(Quantity=qty+varss)
        session.flash="Quantity has been updated"
    return locals()

@auth.requires_login()
def successbuy():
    session.flash="You have successfully completed your purchase"
    for i in range(len(session.cart)):
        newval=db(db.itemsmain.id==session.cart[i]).select()[0].Quantity_sold+int(session.quantity[i])
        db(db.itemsmain.id==session.cart[i]).update(Quantity_sold=newval)
        db.shophistory.insert(user_id=auth.user.id,itemid=session.cart[i],quantity=int(session.quantity[i]))
        qty=db(db.itemsmain.id==session.cart[i]).select()[0].Quantity-int(session.quantity[i])
        if(qty<0):
            qty=0
        db(db.itemsmain.id==session.cart[i]).update(Quantity=qty)
    replystring=""
    for i in range(len(session.cart)):
        itemname = db(db.itemsmain.id==session.cart[i]).select()[0].name
        replystring =replystring + '\n' + 'Item : ' + itemname + '\tQuantity : ' + session.quantity[i]
    mail.send([auth.user.email],
    subject='Your order has been successful',
    reply_to='project.teamauthentication@gmail.com',
    message='Congratulations! Your order has been successfully placed' + '\n' + replystring
    )
    session.cart=[]
    session.quantity=[]
    redirect(URL('index'))
    return locals()

@auth.requires_login()
def buy():
    forms=db(db.addresses.user_id==auth.user.id).select()
    db.addresses.user_id.default=auth.user.id
    addnew=SQLFORM(db.addresses).process()
    return locals()

@auth.requires_login()
def purchasehistory():
    vals=db(db.shophistory.user_id==auth.user.id).select()
    return locals()

@auth.requires_login()
def clearcart():
    session.cart=[]
    session.quantity=[]
    redirect(URL('showcart'))
    return locals()

@auth.requires_login()
def showcart():
    if not session.cart:
        session.cart=[]
        session.quantity=[]
    return locals()

@auth.requires_login()
def addtocart():
    if not session.cart or not session.quantity:
        session.cart=[]
        session.quantity=[]
    session.cart.append(request.args(0))
    session.quantity.append(request.args(1))
    redirect(URL('showcart'))
    return locals()

@auth.requires_login()
def deletefromwish():
    db(db.wishlist.user_id==auth.user.id and db.wishlist.itemid==request.args(0)).delete()
    redirect(URL('showwishlist'))
    return locals()

@auth.requires_login()
def showwishlist():
    lists=db(db.wishlist.user_id==auth.user.id).select()
    return locals()

@auth.requires_login()
def addtowishlist():
    if len(db((db.wishlist.user_id==auth.user.id) & (db.wishlist.itemid==request.args(0))).select())==0:
        db.wishlist.insert(user_id=auth.user.id,itemid=request.args(0))
        redirect(URL('showwishlist'))
    session.flash="Item already in wish list"
    redirect(URL('singlepostitem',args=request.args(0)))

#This is for retailers as well as admins
@auth.requires(auth.has_membership('Admin') or auth.has_membership('Retailer'))
def additem():
    db.itemsmain.Retailer.default=auth.user.id
    gens=SQLFORM(db.itemsmain).process()
    return locals()

def login_callback(form):
    search=db(db.auth_membership).select()
    length=len(search)
    val=search[length-1].user_id
    db.auth_membership.insert(user_id=val,group_id=9) #Group ID 9 is retailers, group ID 8 is Admins

@auth.requires_login()
def ratingadditem():
    if len(db((db.votetrackeritem.personid==auth.user.id)&(db.votetrackeritem.itemid==request.args(0))).select())==0:
        currating=db(db.itemsmain.id==request.args(0)).select()[0].rating
        db(db.itemsmain.id==request.args(0)).update(rating=1+currating)
        db.votetrackeritem.insert(personid=auth.user.id,itemid=request.args(0))
        session.flash="Your vote has been added"
    else:
        session.flash="You have already voted"
    redirect(URL('singlepostitem',args=request.args(0)))
    return locals()

@auth.requires_login()
def singlepostitem(): #Display a single post along with its comments
    val3=db(db.itemsmain.id==request.args(0)).select()
    db.commitem.itemid.default=(request.args(0))
    form=SQLFORM(db.commitem).process()
    form2=SQLFORM.factory(Field('qty','integer',requires=IS_NOT_EMPTY()))
    needcategory=val3[0].itemcategory
    similaritems=db(db.itemsmain.itemcategory==needcategory).select()
    if form2.process().accepted:
        if int(form2.vars.qty)<=val3[0].Quantity:
            session.flash="Added to cart"
            redirect(URL('addtocart',args=[request.args(0),int(form2.vars.qty)]))
        else:
            session.flash="Quantity not in stock"
            redirect(URL('singlepostitem',args=request.args(0)))
    return locals()

def displaypostitem(): #Displays all the posts of a certain category
    val=db(db.itemsmain.itemcategory==request.args(0)).select()
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0) in ['register']:
        hidden_fields = (user_extra_fields if request.args(1) == 'retailer' else retailer_extra_fields)
        if request.args(1)=='retailer':
            auth.settings.register_onaccept = login_callback
            auth.settings.registration_requires_approval=True
        for field in hidden_fields:
            field.readable = field.writable = False
    form=auth()
    #auth.settings.login_form = FaceBookAccount()
    return locals()

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
