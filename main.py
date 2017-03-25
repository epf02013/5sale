"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, render_template, request, session
from google.appengine.ext import ndb
from entities import User, Field, Category, Item, Offer, Notification, Conversation, Message
from forms import Form

import datetime, json
app = Flask(__name__)
app.secret_key="pop"
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def check_login():
    if not session.get("logged_in"):
        return login()

@app.route('/')
def splash():
    """Return a friendly HTTP greeting."""
    return "splash!"

@app.route('/logout')
def logout():
    session.clear()
    return session["logged_in"]

@app.route('/c')
def c():
    """Return a friendly HTTP greeting."""
    for i in xrange(10) :
        category=Category(categoryID=str(i),
                          name=str(i))
        category.put()
    return "splash!"

@app.route("/home")
def home() :
    if not session.get("logged_in"):
        return login()


    categories=Category.query()

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("home.html", 
                            categories=categories,
                            notifications=notifications)


@app.route("/my_items")
def my_items() :
    if not session.get("logged_in"):
        return login()


    items=Item.query(Item.seller_id==session.get("user_id"))

    for item in items :
        item.item_id=item.key.id()

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("my_items.html", items=items)

@app.route("/offers/<offer_id>", methods=["GET", "POST"])
def offers(offer_id) :
    if not session.get("logged_in"):
        return login()

    if request.method=="GET" :
        return "oops", 404
    offer_id=int(offer_id)
    offer=Offer.get_by_id(offer_id)
    item=Item.get_by_id(offer.item)

    if request.form["reason"]=="accept" :
        if item.seller_id!=session["user_id"] :
            return "uninformative error", 404

        offer.accepted=True
        offer.put()
        
        previous_notification=Notification.query(Notification.user==offer.bidder,
                                                 Notification.item==item.key.id(),
                                                 Notification.ntype=="accepted-offer").get()
        if previous_notification :
            previous_notification.key.delete()
        notification_body=session["first_name"]+" "+session["last_name"]+" has accepted your offer for their "+item.name+" posting."
        notification=Notification(user=offer.bidder,
                                  body=notification_body,
                                  ntype="accepted-offer",
                                  item=item.key.id(),
                                  noticed=False)
        notification.put()

        conversation=Conversation(user1=session["user_id"],
                                  user2=offer.bidder,
                                  subject="Arranging Sale",
                                  item=item.key.id(),
                                  item_name=item.name,
                                  read1=True,
                                  read2=True)

        conversation.put()






        return "success"

    if request.form["reason"]=="accept" :
        if item.seller_id!=session["user_id"] :
            return "uninformative error", 404

        offer.accepted=True
        offer.put()
        return "success"
    return "uninformative error", 404


@app.route("/view_conversations") 
def view_conversations() :
    if not session.get("logged_in"):
        return login()

    conversations=Conversation.query(ndb.OR(Conversation.user1==session["user_id"],Conversation.user2==session["user_id"])).order(Conversation.time)

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("conversations.html", 
                            conversations=conversations,
                            notifications=notifications)


@app.route("/view_conversations/<conversation_id>") 
def view_conversation(conversation_id) :
    if not session.get("logged_in"):
        return login()


    conversation_id=int(conversation_id)
    conversation=Conversation.get_by_id(conversation_id)
    messages=Message.query(Message.conversation==conversation_id).order(Message.time)


    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("view_conversation.html", 
                            messages=messages,
                            conversation=conversation,
                            notifications=notifications)

@app.route("/my_items/<item_id>")
def my_item(item_id) :
    if not session.get("logged_in"):
        return login()

    item_id=int(item_id)

    item=Item.get_by_id(item_id)

    offers=Offer.query(Offer.item==item_id).order(Offer.amount)

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("view_my_item.html", 
                            offers=offers,
                            item=item,
                            notifications=notifications)

@app.route("/browse/<category_id>")
def browse(category_id) :
    if not session.get("logged_in"):
        return login()

    items=Item.query(Item.category==category_id)

    for item in items :
        item.item_id=item.key.id()

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("browse.html", 
                            items=items,
                            category_id=category_id,
                            notifications=notifications)
    
@app.route("/browse/<category_id>/<item_id>", methods=["GET", "POST"])
def browse_item(category_id,item_id) :
    item_id=int(item_id)
    if not session.get("logged_in"):
        return login()

    if request.method=="GET":
        item=Item.get_by_id(item_id)
        print item.name
        seller=User.get_by_id(item.seller_id)
        

        previous_offer=Offer.query(Offer.bidder==session["user_id"],
                          Offer.item==item_id).get()

        was_previous_offer=False
        if previous_offer :
            was_previous_offer=True


        fields=[]
        fields.append(Field(name="message", 
                        title="Message For Seller", 
                        the_type='text', 
                        identifier='message',
                        placeholder="A short message for the seller. Perhaps, where you can meet or payment options.",
                        tag="textarea"))
        if item.biddable :

            fields.append(Field(name='amount',
                                title="Offer Amount",
                                the_type="number",
                                identifier="amount",
                                placeholder="10.95",
                                step=True))

        title="Make Offer"
        form=Form(fields=fields, title=title)

        notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
        return render_template("browse_item.html", 
                                item=item, 
                                category_id=category_id,
                                bid_form=form,
                                previous_offer=previous_offer,
                                was_previous_offer=was_previous_offer,
                                offer=previous_offer,
                                notifications=notifications)
        
    if request.method=="POST" :

        item=Item.get_by_id(item_id)
        seller=User.get_by_id(item.seller_id)
        

        previous_offer=Offer.query(Offer.bidder==session["user_id"],
                          Offer.item==item_id).get()

        if previous_offer :
            previous_offer.key.delete()


        amount=item.price
        if item.biddable :
            amount=float(request.form["amount"])



        offer=Offer(bidder=session["user_id"],
                    item=item_id,
                    message=request.form["message"],
                    amount=amount,
                    bidder_name=session["first_name"]+" "+session["last_name"],
                    accepted=False)
        offer.put()


        fields=[]
        fields.append(Field(name="message", 
                        title="Message For Seller", 
                        the_type='text', 
                        identifier='message',
                        placeholder="A short message for the seller. Perhaps, where you can meet or payment options.",
                        tag="textarea"))
        if item.biddable :

            fields.append(Field(name='amount',
                                title="Offer Amount",
                                the_type="number",
                                identifier="amount",
                                placeholder="10.95",
                                step=True))

        title="Make Offer"
        form=Form(fields=fields, title=title)

        notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
        return render_template("browse_item.html", 
                                item=item, 
                                category_id=category_id,
                                bid_form=form,
                                offer=offer,
                                was_previous_offer=True,
                                notifications=notifications)

@app.route("/post_item", methods=["GET","POST"])
def post_item() :
    if not session.get("logged_in"):
        return login()

    
    if request.method=="GET" :
        fields=[]
        fields.append(Field(name="name", 
                        title="Name", 
                        the_type='text', 
                        identifier='name',
                        placeholder="Item Name"))
        fields.append(Field(name='description',
                                title="Description",
                                the_type="textarea",
                                identifier='description',
                                placeholder='Descriptive Description',
                                tag="textarea"))
        categories=Category.query()

        options=[]
        for category in categories :
            option={}
            option["name"]=category.name
            option["value"]=category.categoryID
            options.append(option)


        fields.append(Field(name='category',
                                title="Item Category",
                                the_type="select",
                                identifier="category",
                                placeholder="Select Item Category",
                                tag="select",
                                options=options))
        fields.append(Field(name='price',
                                title="Price",
                                the_type="number",
                                identifier="price",
                                placeholder="10.95",
                                step=True))
        fields.append(Field(name='biddable',
                                title="Allow offer amounts other than suggested price.",
                                the_type="number",
                                identifier="biddable",
                                tag="checkbox"))
        title="Post Item"
        form=Form(fields=fields, title=title)

        notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
        return render_template("post_item.html", 
                                item_form=form,
                                notifications=notifications)


    if request.method=="POST" :
        name=request.form.get("name")
        description=request.form.get("description")
        category=request.form.get("category")
        price=float(request.form.get("price"))
        seller_id=session["user_id"]
        biddable=False
        if request.form.get("biddable") :
            biddable=True
        new_item=Item(name=name,
                      description=description,
                      category=category,
                      price=price,
                      seller_id=seller_id,
                      biddable=biddable,
                      sold=False)
        new_item.put()

        return my_items()




def logged_in(user) :
    #Do Log in Stuff
    session["name"]=user.name
    session["user_id"]=user.userID
    session['logged_in']=True
    return render_template('logged_in.html')


@app.route('/fb_login', methods=['GET','POST'])
def fb_login():
    if request.method!= "POST" :
        return "Error", 404
    user=User.get_by_id(request.form["userID"])
    response={}

    response["status"]="existing"
    if not user :
        user=User(id=request.form["userID"],
                  userID=request.form["userID"])
        user.put()

        response["status"]="new"
    
    session['first_name']=request.form["first_name"]
    session['last_name']=request.form["last_name"]
    session['email']=request.form["email"]
    logged_in(user)
    return json.dumps(response)

@app.route('/fb_signup', methods=['GET','POST'])
def fb_signup():
    if request.method!= "POST" :
        return "Error", 404
    user=User(id=request.form["userID"])
    user.put()

@app.route('/login', methods=['GET','POST'])
def login():
    fields=[]
    fields.append(Field(name="email", 
                    title="Email", 
                    the_type='email', 
                    identifier='email',
                    placeholder="Email"))
    fields.append(Field(name='password',
                            title="Password",
                            the_type="password",
                            identifier='password',
                            placeholder='Password'))
    title="Login "
    form=Form(fields=fields, title=title)
    if request.method=='GET' : 
        return render_template('login.html', login_form=form)
    try :
        user=User.get_by_id(request.form['email'])
        if user :
            if user.password==request.form['password'] :
                print "pop"

                return logged_in(user)
            else :
                form.error="User or Password was Incorrect"
                return render_template('login.html', login_form=form) 
        else :
            form.error="User or Password was Incorrect"
            return render_template('login.html', login_form=form)
    except KeyError as err:
        form.error="Email or Password Was Not Filled Out Correctly"
        return render_template('login.html', login_form=form)

def signed_up(user) :
    return render_template('signed_up.html', name=user.name)

@app.route('/signup', methods=['GET','POST'])
def signup():

    fields=[]
    fields.append(Field(name="email", 
                    title="Email", 
                    the_type='email', 
                    identifier='email',
                    placeholder="Email"))
    fields.append(Field(name="name", 
                    title="Name", 
                    the_type='name', 
                    identifier='name',
                    placeholder="Name"))
    fields.append(Field(name='password',
                            title="Password",
                            the_type='password',
                            identifier='password',
                            placeholder='Password'))
    title="Signup"

    form=Form(fields=fields, title=title)

    if request.method=='GET' :
        return render_template('signup.html', signup_form=form)

    try :
        exists=User.get_by_id(request.form['email'])
        if exists :
            form.error="Email Taken"
            return render_template('signup.html', signup_form=form)
        else :
            user=User(email=request.form['email'], 
                              id=request.form['email'], 
                              password=request.form['password'],
                              name=request.form['name'])
            user.put()
            return signed_up(user)
    except  KeyError as err:
        form.error="Email or Password Was Not Filled Out Correctly"
        return render_template('signup.html', signup_form=form)
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
