from google.appengine.ext import ndb
from flask import Markup, render_template
from forms import Form
import cgi, datetime

date_format="%Y-%m-%d %H:%M"



class Field(object):
    """docstring for Field"""
    def __init__(self,name=None, the_type=None, title=None, identifier=None, placeholder=None, tag="input", options=[], step=False, value="", hidden=""):
        super(Field, self).__init__()
        self.name = name
        self.the_type=the_type
        self.title=title
        self.identifier=identifier
        self.placeholder=placeholder
        self.tag=tag
        self.options=options
        self.step=step
        self.value=value
        self.hidden=hidden


class Item(ndb.Model) :
    name=ndb.StringProperty()
    description=ndb.TextProperty()
    category=ndb.StringProperty()
    price=ndb.FloatProperty()
    seller_id=ndb.StringProperty()
    seller_name=ndb.StringProperty()
    biddable=ndb.BooleanProperty()
    new_bid=ndb.BooleanProperty()
    sold=ndb.BooleanProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    best_offer=ndb.FloatProperty()
    photo=ndb.BlobProperty()
    photo_mimetype=ndb.StringProperty()

    def get_amount(self) :
        if self.biddable and self.best_offer>self.price :
            return "$"+str(self.best_offer)
        else :
            return "$"+str(self.price)
    def get_pretty_date_time(self) :
        return self.time.strftime("%Y-%m-%d at %I:%M %p")

    @ndb.transactional(retries=3)
    def update_best_offer(self, new_offer_price) :
        if new_offer_price> self.best_offer :
            self.best_offer=new_offer_price

            self.put()
        return "updated"

    def display(self, mine=False, detailed=False, tags=[]) :
        return Markup(render_template("Item.html", item=self, mine=mine, detailed=detailed, tags=tags))
   
    def display_row(self) :
        return Markup(render_template("Item_row.html", item=self))
class Admin(ndb.Model) :
    admin_id=ndb.StringProperty()
        
class User(ndb.Model) :
    userID=ndb.StringProperty()
    name=ndb.StringProperty()
    email=ndb.StringProperty()
    password=ndb.StringProperty()
    rating=ndb.FloatProperty()
    number_ratings=ndb.FloatProperty()
    
    def display(self) :
        fields=[]
        options=[]
        for x in xrange(1,6) :
            option={}
            option["name"]=x
            option["value"]=x
            options.append(option)


        fields.append(Field(name='rating',
                                title="Rating",
                                the_type="select",
                                identifier="rating",
                                placeholder="5 is high 1 is low",
                                tag="select",
                                options=options,
                                value="1"))
        fields.append(Field(name='reason',
                                title="Reason",
                                the_type="textarea",
                                identifier='reason',
                                placeholder='Great experience. Item description was accurate.',
                                tag="textarea"))

        title="Write Review"
        form=Form(fields=fields, 
                title=title)

        recent_reviews=self.get_recent_reviews()
        return Markup(render_template("User.html", 
                                        user=self, 
                                        reviews=recent_reviews,
                                        user_form=form))
    
    def get_recent_reviews(self) :
        reviews=Review.query(Review.user==self.key.id()).order(-Review.time)
        the_reviews=[]
        count=0
        for review in reviews :
            if count==10 :
                break
            the_reviews.append(review)
            count+=1
        the_reviews.reverse()
        return the_reviews


class Review(ndb.Model) :
    user=ndb.StringProperty()
    reviewer=ndb.StringProperty()
    rating=ndb.IntegerProperty()
    reason=ndb.TextProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    flagged=ndb.BooleanProperty()

    def display(self, remove=False) :
        return Markup(render_template("Review.html", review=self, remove=remove))


class Sale(ndb.Model) :
    seller=ndb.StringProperty()
    buyer=ndb.StringProperty()
    item=ndb.IntegerProperty()
    price=ndb.FloatProperty()



class Message(ndb.Model) :
    sender=ndb.StringProperty()
    recipient=ndb.StringProperty()
    body=ndb.StringProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    conversation=ndb.IntegerProperty()

class Notification(ndb.Model) :
    user=ndb.StringProperty()
    body=ndb.StringProperty()
    ntype=ndb.StringProperty()
    item=ndb.IntegerProperty()
    item_category=ndb.StringProperty()
    time=ndb.DateTimeProperty(auto_now_add=True)
    noticed=ndb.BooleanProperty()

    def display(self):
        return Markup(render_template("Notification.html", notification=self))


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
    confirmed=ndb.BooleanProperty()
    time=ndb.DateTimeProperty(auto_now=True)

    def display(self):
        item=Item.get_by_id(self.item)
        return Markup(render_template("Offer.html", 
                                        offer=self,
                                        item=item))




class Category(ndb.Model) :
    categoryID=ndb.StringProperty()
    name=ndb.StringProperty()
    photo=ndb.BlobProperty()
    photo_mimetype=ndb.StringProperty()

    def display(self, width=20):
        return Markup(render_template("Category.html", category=self, width=width))



class Subcategory(ndb.Model) :
    name=ndb.StringProperty()

class Tag(ndb.Model):
    name=ndb.StringProperty()

class Item_Tag(ndb.Model):
    item=ndb.IntegerProperty()
    tag=ndb.StringProperty()

