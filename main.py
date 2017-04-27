"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, render_template, request, session, send_file
from google.appengine.ext import ndb
from google.appengine.api import images
from entities import User, Field, Category, Item, Offer, Notification, Conversation, Message, Admin, Review, Tag, Item_Tag
from forms import Form

import datetime, json, io
app = Flask(__name__)
app.secret_key="pop"
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@ndb.transactional(retries=4)
def update_user_rating(user_id, rating) :
    user=User.get_by_id(user_id)
    user.number_ratings+=1.0
    user.rating=user.rating/((user.number_ratings-1.0)/user.number_ratings)+rating/(user.number_ratings)
    user.put()

@ndb.transactional(retries=0)
def flag_review(review_id) :
    review=Review.get_by_id(review_id)
    review.flagged=True
    review.put()


def check_login():
    if not session.get("logged_in"):
        return login()

@app.route('/')
def splash():
    """Return a friendly HTTP greeting."""
    return "splash!"


@app.route("/create_admins")
def create_admins():
    users=User.query()

    for user in users :
        admin=Admin(id=user.key.id(),
                    admin_id=user.key.id())

        admin.put()
    return "Admin Created"



@app.route('/logout')
def logout():
    session.clear()
    return "logged out"

# @app.route("/notifications/<notification_id>")
# def notifications(item_id) :
#     notification_id=int(notification_id)

#     notification=Notification.get_by_id(notification_id)

#     if notification.ntype=="item-removed"
#     accepted-offer
#     rejected-offer
#     item-removed

@app.route("/search")
def search() :
    if not session.get("logged_in"):
        return login()


    query_string=request.args.get("query").lower()

    items=Item.query()

    result_items=[]
    item_ids=set()
    for item in items :
        if query_string in item.name.lower():
            if not item.key.id() in item_ids :
                result_items.append(item)
                item_ids.add(item.key.id())

    item_tags=Item_Tag.query(Item_Tag.tag==query_string)

    for item_tag in item_tags :
        if not item_tag.item in item_ids :
            item=Item.get_by_id(item_tag.item)
            result_items.append(item) #can append it with value "only found in the tags"
            item_ids.add(item.key.id()) #dont need to append it since all unique in this second query anyways

    return render_template("search_results.html", 
                            result_items=result_items,
                            query=query_string)



@app.route("/history")
def history() :
    if not session.get("logged_in"):
        return login()

    sold_offers=[]
    sold_items=Item.query(Item.seller_id==session["user_id"],Item.sold==True)
    for item in sold_items :
        temp_offer=Offer.query(Offer.item==item.key.id()).get()
        sold_offers.append(temp_offer)

    purchased_offers=Offer.query(Offer.confirmed==True, Offer.bidder==session["user_id"])

    return render_template("history.html", 
                            sold_offers=sold_offers,
                            purchased_offers=purchased_offers)


@app.route('/c')
def c():
    """Return a friendly HTTP greeting."""
    for i in xrange(10) :
        category=Category(categoryID=str(i),
                          name=str(i))
        category.put()
    return "splash!"

@app.route("/admin_page" , methods=["GET", "POST"])
def admin() :
    if not session.get("admin"):
        return login()

    if request.method=="POST" :
        file=request.files.get("file",None)
        content_type=None
        photo=None
        if file :
            file_data=file.read()
            content_type=file.content_type
            # photo=images.Image(file_data)
            photo=images.resize(file_data,width=500, height=500)

        category=Category(id=request.form["name"].strip(),
                          categoryID=request.form["name"],
                          name=request.form["name"],
                          photo=photo,
                          photo_mimetype=content_type
                          )
        category.put()

    fields=[]

    fields.append(Field(name="name", 
                        title="Category Name", 
                        the_type='text', 
                        identifier='name',
                        placeholder="Category Name"))
    fields.append(Field(name='file',
                                title="Upload Photo",
                                the_type="file",
                                placeholder="Upload Photo",
                                identifier="file",
                                tag="file"))
    title="Create Category"
    form=Form(fields=fields, title=title)
    reviews=Review.query(Review.flagged==True)
    categories=Category.query()
    return render_template("admin_homepage.html",
                            reviews=reviews,
                            categories=categories,
                            category_form=form);  

@app.route("/home")
def home() :
    if not session.get("logged_in"):
        return login()


    the_categories=Category.query()
    # categories=[]
    # num_categories=0
    # for category in the_categories :
    #     categories.append(category)
    #     num_categories+=1

    # dividers=[2,4,3]
    # category_lists=[]
    # count=2
    # index=0
    # current_list=[]
    # left_over=False
    # for category in categories :
    #     left_over=True
    #     current_list.append(category)
    #     count-=1
    #     if count==0 :
    #         category_lists.append((current_list,100.0/len(current_list)))
    #         current_list=[]
    #         index+=1
    #         count=dividers[index]
    #         left_over=False

    # if left_over :
    #     category_lists.append((current_list,100.0/len(current_list)))


    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
    # return render_template("home2.html", 
    #                         category_lists=category_lists,
    #                         notifications=notifications)
    return render_template("home.html", 
                            categories=the_categories,
                            notifications=notifications)


@app.route("/reviews/<review_id>", methods=["GET", "POST"])
def reviews(review_id) :
    review_id=int(review_id)
    if request.method=="POST" :
        if request.form["reason"]=="flag" :
            flag_review(review_id)
            return "flagged"
        elif request.form["reason"]=="remove" :
            if session.get("admin") :
                review=Review.get_by_id(review_id)
                review.key.delete()
                return "removed"
    return "uninformative error", 400


@app.route("/user/<user_id>", methods=["GET", "POST"])
def view_user(user_id) :



    user=User.get_by_id(user_id)

    if request.method=="POST" :
        if user_id==session["user_id"] :
            return render_template("tsktsk.html")
        review=Review(rating=int(request.form["rating"]),
                      reason=request.form["reason"],
                      user=user_id,
                      reviewer=session["user_id"],
                      flagged=False)
        review.put()

        update_user_rating(user_id,int(request.form["rating"]))

    return render_template("view_user.html", user=user)


@app.route("/my_items")
def my_items() :
    if not session.get("logged_in"):
        return login()


    items=Item.query(Item.seller_id==session.get("user_id"))

    for item in items :
        item.item_id=item.key.id()

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("my_items.html", items=items)



@app.route("/delete_item/<item_id>", methods=["GET", "POST"])
def delete_item(item_id):
    if not session.get("logged_in"):
        return login()

    item_id=int(item_id)

    item=Item.get_by_id(item_id)

    if item.seller_id!= session["user_id"] :
        return "oops", 500


    previous_notifications=Notification.query(Notification.item==item_id)
    

    notification_body=item.name+" was removed by seller."
    for prev_not in previous_notifications :

        notification=Notification(user=prev_not.user,
                                  body=notification_body,
                                  ntype="item-removed",
                                  item=item.key.id(),
                                  item_category=item.category,
                                  noticed=False)
        notification.put()
        prev_not.key.delete()

    offers=Offer.query(Offer.item==item.key.id())

    conversation=Conversation.query(Conversation.item==item_id).get()
    if conversation :
        messages=Message.query(Message.conversation==conversation.key.id())
        for message in messages :
            message.key.delete()
        conversation.key.delete()

    for offer in offers :
        offer.key.delete()


    item_tags=Item_Tag.query(Item_Tag.item==item.key.id())

    for item_tag in item_tags :
        item_tag.key.delete()


    item.key.delete()

    return "success"


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
                                  item_category=item.category,
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

    if request.form["reason"]=="reject" :
        if item.seller_id!=session["user_id"] :
            return "uninformative error", 404

        offer.accepted=True
        offer.put()
        previous_notification=Notification.query(Notification.user==offer.bidder,
                                                 Notification.item==item.key.id(),
                                                 Notification.ntype=="accepted-offer").get()
        if previous_notification :
            previous_notification.key.delete()
        notification_body=session["first_name"]+" "+session["last_name"]+" has rejected your offer for their "+item.name+" posting."
        notification=Notification(user=offer.bidder,
                                  body=notification_body,
                                  ntype="rejected-offer",
                                  item=item.key.id(),
                                  item_category=item.category,
                                  noticed=False)
        notification.put()
        return "success"

    if request.form["reason"]=="confirm" :
        if item.seller_id!=session["user_id"] :
            return "uninformative error", 404

        item.sold=True
        item.put()
        offer.confirmed=True
        offer.put()
        offers=Offer.query(Offer.item==item.key.id(),Offer.bidder!=offer.bidder)
        for temp_offer in offers :
            notification_body=item.name+" was sold to someone else."
            notification=Notification(user=offer.bidder,
                                  body=notification_body,
                                  ntype="item-sold",
                                  item=item.key.id(),
                                  item_category=item.category,
                                  noticed=False)
            notification.put()
            temp_offer.key.delete()
        return "Offer confirmed"
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
@app.route("/messages", methods=["GET","POST"]) 
def messages() :
    if not session.get("logged_in"):
        return login()

    conversation=Conversation.get_by_id(int(request.form["conversation"]))
    recipient=conversation.user1
    if session["user_id"]==recipient :
        recipient=conversation.user2

    message=Message(sender=session["user_id"],
                    recipient=recipient,
                    body=request.form["message_body"],
                    conversation=conversation.key.id())
    message.put()

    return "success"
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

@app.route("/my_items/<item_id>", methods=["GET","POST"])
def my_item(item_id) :
    if not session.get("logged_in"):
        return login()

    item_id=int(item_id)

    item=Item.get_by_id(item_id)


    if request.method=="POST" :

        if item.seller_id!=session["user_id"] :
            return "Uninformative Error", 500


        if request.form.get("tags") :
            tags=request.form["tags"].split(" ")

            for tag in tags :
                tag=tag.strip().lower()
                exists=Tag.get_by_id(tag)

                if not exists :
                    new_tag=Tag(id=tag, name=tag)
                    new_tag.put()

                exists=Item_Tag.get_by_id(str(item_id)+tag)

                if not exists :
                    new_item_tag=Item_Tag(id=str(item_id)+tag,item=item_id,tag=tag)
                    new_item_tag.put()


        else :
            item.name=request.form.get("name")
            item.description=request.form.get("description")
            item.category=request.form.get("category")
            item.price=float(request.form.get("price"))
            item.biddable=False
            if request.form.get("biddable") :
                item.biddable=True

            item.put()



    offers=Offer.query(Offer.item==item_id).order(Offer.amount)


    fields=[]
    fields.append(Field(name="name", 
                        title="Name", 
                        the_type='text', 
                        identifier='name',
                        placeholder="Item Name",
                        value=item.name))
    fields.append(Field(name='description',
                                title="Description",
                                the_type="textarea",
                                identifier='description',
                                placeholder='Descriptive Description',
                                tag="textarea",
                                value=item.description))
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
                                options=options,
                                value=item.category))
    fields.append(Field(name='price',
                                title="Price",
                                the_type="number",
                                identifier="price",
                                placeholder="10.95",
                                step=True,
                                value=item.price))
    fields.append(Field(name='biddable',
                                title="Allow offer amounts other than suggested price.",
                                the_type="number",
                                identifier="biddable",
                                tag="checkbox",
                                value="checked" if item.biddable else ""))
    fields.append(Field(name='item_id',
                                the_type="hidden",
                                identifier="item_id",
                                value=item.key.id(),
                                hidden="hidden"))
    title="Edit Item"
    form=Form(fields=fields, 
                title=title)


    fields1=[]

    fields1.append(Field(name="tags", 
                        title="Tags", 
                        the_type='text', 
                        identifier='name',
                        placeholder="Enter descriptive words seperated by spaces."))

    title1=""
    submit="Add Tag"
    form1=Form(fields=fields1, title=title1, submit=submit)

    tags=Item_Tag.query(Item_Tag.item==item_id)
    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    return render_template("view_my_item.html", 
                            offers=offers,
                            item=item,
                            notifications=notifications,
                            item_form=form,
                            tag_form=form1,
                            tags=tags)

@app.route("/browse/<category_id>")
def browse(category_id) :
    if not session.get("logged_in"):
        return login()

    items=Item.query(Item.category==category_id)

    for item in items :
        item.item_id=item.key.id()

    notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)

    category=Category.get_by_id(category_id)

    return render_template("browse.html", 
                            items=items,
                            category=category,
                            category_id=category_id,
                            notifications=notifications)
    
@app.route("/browse_item/<item_id>", methods=["GET", "POST"])
def browse_item(item_id) :
    item_id=int(item_id)
    if not session.get("logged_in"):
        return login()

    if request.method=="GET":
        item=Item.get_by_id(item_id)
        category_id=item.category
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

        tags=Item_Tag.query(Item_Tag.item==item_id)
        notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
        return render_template("browse_item.html", 
                                item=item, 
                                category_id=category_id,
                                bid_form=form,
                                previous_offer=previous_offer,
                                was_previous_offer=was_previous_offer,
                                offer=previous_offer,
                                notifications=notifications,
                                tags=tags)
        
    if request.method=="POST" :

        item=Item.get_by_id(item_id)

        if not item or item.sold :
            return page_was_not_found("Sorry but the item you tried to bid on has been removed by the seller")

        category_id=item.category
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
                    accepted=False,
                    confirmed=False)
        offer.put()

        if item.biddable:
            item.update_best_offer(amount)



        notification=Notification(user=item.seller_id,
                                  body=notification_body,
                                  ntype="item-removed",
                                  item=item.key.id(),
                                  item_category=item.category,
                                  noticed=False)

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
        form=Form(fields=fields, title=title, submit="Make Offer")


        tags=Item_Tag.query(Item_Tag.item==item_id)
        notifications=Notification.query(Notification.user==session["user_id"]).order(-Notification.time)
        return render_template("browse_item.html", 
                                item=item, 
                                category_id=category_id,
                                bid_form=form,
                                offer=offer,
                                was_previous_offer=True,
                                notifications=notifications,
                                tags=tags)



def page_was_not_found(message) :
    return render_template("page_not_found.html", message=message)

@app.route("/item_photo/<item_id>")
def item_photo(item_id) :
    item_id=int(item_id)
    item=Item.get_by_id(item_id)
    if not item.photo :
        return "error", 500
    return send_file(io.BytesIO(item.photo),
                     attachment_filename='item_photo.png',
                     mimetype=item.photo_mimetype)

@app.route("/category_photo/<category_id>")
def category_photo(category_id) :
    category=Category.get_by_id(category_id)
    if not category.photo :
        return "error", 500
    return send_file(io.BytesIO(category.photo),
                     attachment_filename='category_photo.png',
                     mimetype=category.photo_mimetype)

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

        fields.append(Field(name='file',
                                title="Upload Photo",
                                the_type="file",
                                placeholder="Upload Photo",
                                identifier="file",
                                tag="file"))

        fields.append(Field(name='biddable',
                                title="Allow offer amounts other than suggested price.",
                                the_type="number",
                                identifier="biddable",
                                tag="checkbox"))
        title="Post Item"
        form=Form(fields=fields, title=title, submit="Post")

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

        # print "nooo"
        # return json.dumps(request.files)

        file=request.files.get("file",None)
        # print "whaattt??"
        file_data=None
        content_type=None 
        photo=None
        if file :
            file_data=file.read()
            photo=images.resize(file_data,width=500, height=500)
            content_type=file.content_type


        new_item=Item(name=name,
                      description=description,
                      category=category,
                      price=price,
                      seller_id=seller_id,
                      seller_name=session["first_name"]+" "+session["last_name"],
                      biddable=biddable,
                      sold=False,
                      best_offer=0.0,
                      photo=photo,
                      photo_mimetype=content_type)
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
                  userID=request.form["userID"],
                  name=request.form["first_name"]+" "+request.form["last_name"],
                  email=request.form["email"],
                  rating=2.5,
                  number_ratings=1)
        user.put()

        response["status"]="new"
    
    if Admin.get_by_id(user.key.id()) :
        session["admin"]=True
    else :
        session["admin"]=False
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


