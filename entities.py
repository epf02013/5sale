from google.appengine.ext import ndb
from flask import Markup, render_template
import cgi, datetime

date_format="%Y-%m-%d %H:%M"



class Field(object):
    """docstring for Field"""
    def __init__(self,name=None, the_type=None, title=None, identifier=None, placeholder=None, tag="input", options=[], step=False):
        super(Field, self).__init__()
        self.name = name
        self.the_type=the_type
        self.title=title
        self.identifier=identifier
        self.placeholder=placeholder
        self.tag=tag
        self.options=options
        self.step=step

class Item(ndb.Model) :
    name=ndb.StringProperty()
    description=ndb.TextProperty()
    category=ndb.StringProperty()
    price=ndb.FloatProperty()
    seller_id=ndb.StringProperty()
    biddable=ndb.BooleanProperty()
    new_bid=ndb.BooleanProperty()
    sold=ndb.BooleanProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
        
class User(ndb.Model) :
    userID=ndb.StringProperty()
    name=ndb.StringProperty()
    email=ndb.StringProperty()
    password=ndb.StringProperty()
    rating=ndb.FloatProperty()
    number_ratings=ndb.FloatProperty()

class Sale(ndb.Model) :
    seller=ndb.StringProperty()
    buyer=ndb.StringProperty()
    item=ndb.IntegerProperty()
    price=ndb.FloatProperty()



class Message(ndb.Model) :
    sender=ndb.StringProperty()
    recipient=ndb.StringProperty()
    body=ndb.BooleanProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    conversation=ndb.IntegerProperty()

class Notification(ndb.Model) :
    user=ndb.StringProperty()
    body=ndb.StringProperty()
    ntype=ndb.StringProperty()
    item=ndb.IntegerProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    noticed=ndb.BooleanProperty()


class Conversation(ndb.Model) :
    user1=ndb.StringProperty()
    user2=ndb.StringProperty()
    subject=ndb.StringProperty()
    item=ndb.IntegerProperty()
    item_name=ndb.StringProperty()
    read1=ndb.BooleanProperty()
    read2=ndb.BooleanProperty()
    time=ndb.DateTimeProperty(auto_now=True)



class Offer(ndb.Model) :
    amount=ndb.FloatProperty()
    message=ndb.TextProperty()
    bidder=ndb.StringProperty()
    item=ndb.IntegerProperty()
    bidder_name=ndb.StringProperty()
    accepted=ndb.BooleanProperty()


class Category(ndb.Model) :
    categoryID=ndb.StringProperty()
    name=ndb.StringProperty()



