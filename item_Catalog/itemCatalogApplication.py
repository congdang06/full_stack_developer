from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, ItemCatalog, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog Application'


# Connect to the database and create database session
engine = create_engine(
    'sqlite:///itemcatalogwithloginusers.db' + '?check_same_thread=False')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


"""********************************************************
CATALOG INFORMATION
CRUD ------- CREATE, READ, UPDATE AND DELETE
***********************************************************"""


# JSON API to view Catalog information
@app.route('/catalog/JSON')
def catalogJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[c.serialize for c in catalogs])


@app.route('/catalog/<int:catalog_id>/item/JSON')
def itemCatalogJSON(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(ItemCatalog).filter_by(catalog_id=catalog_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# show all item Catalogs by JSON
@app.route('/catalog/showJSONCatalog')
def showJSONCatalog():
    items = session.query(ItemCatalog).order_by(ItemCatalog.id.asc())
    return jsonify(ItemCatalogs=[i.serialize for i in items])


# show JSON with selected item in the catalog
@app.route('/catalog/<int:catalog_id>/item/<int:item_catalog_id>/JSON')
def showCataloginEachItem(catalog_id, item_catalog_id):
    item_Catalog = session.query(ItemCatalog).filter_by(
                                id=item_catalog_id).one()
    return jsonify(item_Catalog=item_Catalog.serialize)


""" ********************************************************************"""
""" This function prevent
    sqlalchemy.exc.InvalidRequestError:
    it happen everytime I add new categories and items
"""


def with_session(fn):
    def go(*args, **kw):
        session.begin(subtransactions=True)
        try:
            ret = fn(*args, **kw)
            session.commit()
            return ret
        except:
            session.rollback()
            raise
    return go


"""************************************************************************
    CATALOG
        CREATE
        READ/SHOW
        EDIT/UPDATE
        DELETE
***************************************************************************"""


"""SHOW CATALOGS """


@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    categories = session.query(Catalog).order_by(Catalog.name.asc())
    items = session.query(ItemCatalog).order_by(ItemCatalog.id.asc())
    count_categories = categories.count()
    count_items = items.count()
    # user login, can see list of categories and items
    if 'username' not in login_session:
        return render_template(
            'public_catalog.html',
            catalogs=categories,
            items=items)
    else:
        return render_template(
            'catalog_items_list.html',
            catalogs=categories,
            count_categories=count_categories,
            count_items=count_items,
            items=items)


""" CREATE A NEW CATALOG """


@app.route('/catalog/new', methods=['GET', 'POST'])
def newCatalog():
    # if user is not login return login credentials
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if not request.form['name']:
            flash("Name can not be blank.", 'error')
            return render_template('newCatalog.html')
        newCatalog = Catalog(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newCatalog)
        session.commit()
        flash('New Catalog %s Was Successfully Created' % newCatalog.name)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


# EDIT CATALOG
@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    edit_Catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if edit_Catalog.user_id != login_session['user_id']:
        return "<script>function myEditCatalog() {\
            alert('You are not authorized to edit this catalog \
                    Please create your own account \
                   ');} \
                </script> \
            <body onload = 'myEditCatalog()'>"
    if request.method == 'POST':
        if not request.form['name']:
            flash("Name can not be blank")
            return render_template('editCatalog.html', catalog=edit_Catalog)
        if request.form['name']:
            edit_Catalog.name = request.form['name']
            flash('Catalog %s Was Successfully Editted' % edit_Catalog.name)
            return redirect(url_for('showCatalogs'))
    else:
        return render_template(
            'editCatalog.html', catalog=edit_Catalog)


# DELETE CATALOG
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    # Allow user to delete their own catalog
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        return "<script> function myDeleteFunction(){\
                alert('You are not authorize to DELETE \
                    this catalog. Please create your own account\
                ');} \
            </script> \
            <body onload = 'myDeleteFunction()'>"
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('Catalog %s Was Successully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(
            url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template(
            'deleteCatalog.html', catalog=catalogToDelete)


"""************************************************************************
    ITEM CATALOGS
        CREATE
        READ/SHOW
        EDIT/UPDATE
        DELETE
***************************************************************************"""


# SHOW ITEM CATALOGS
@app.route('/catalog/<int:catalog_id>/items/<int:item_catalog_id>/')
def showItemCatalog(catalog_id, item_catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalogs = session.query(Catalog).order_by(Catalog.name.asc())
    item = session.query(ItemCatalog).filter_by(id=item_catalog_id).one()
    items = session.query(ItemCatalog).filter_by(
        catalog_id=catalog_id).order_by(ItemCatalog.id.desc())
    creator = getUserInfo(catalog.user_id)
    get_items = session.query(ItemCatalog).filter_by(
                    catalog_id=catalog_id).order_by(ItemCatalog.id.desc())
    count_categories = get_items.count()
    return render_template(
            'show_categories_description.html',
            catalog=catalog,
            catalogs=catalogs,
            get_items=get_items,
            item=item,
            items=items,
            count_categories=count_categories,
            creator=creator)


# SHOW SPCECIFIC ITEM CATALOG IF SELECTED
@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalog/<int:catalog_id>/categoriesItem/')
def showSpecificCategoryItems(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalogs = session.query(Catalog).order_by(Catalog.name.asc())
    items = session.query(ItemCatalog).filter_by(
        catalog_id=catalog_id).order_by(ItemCatalog.id.desc())
    item = session.query(ItemCatalog).filter_by(id=catalog_id).one()
    count_categories = items.count()
    return render_template(
        'display_specific_item.html',
        catalog=catalog,
        catalogs=catalogs,
        count_categories=count_categories,
        item=item,
        items=items)

# NEW ITEM CATALOG


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItemCatalog():
    catalogs = session.query(Catalog).all()
    if request.method == 'POST':
        if not request.form['name'] or not request.form['description']:
            flash('Either Item Name or Description can not be blank')
            return render_template('newItemCatalog.html', catalogs=catalogs)
        newItem = ItemCatalog(
            name=request.form['name'],
            description=request.form['description'],
            catalog_id=request.form['catalog'],
            user_id=login_session['user_id']
            )
        session.add(newItem)
        session.commit()
        flash("ItemCatalog was %s successfully created" % newItem.name)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newItemCatalog.html', catalogs=catalogs)


# EDIT THE ITEM CATALOG
@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_catalog_id>/edit',
    methods=['GET', 'POST'])
def editItemCatalog(catalog_id, item_catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    editItemCatalog = session.query(ItemCatalog).filter_by(
        id=item_catalog_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalogs = session.query(Catalog).all()
    if login_session['user_id'] != catalog.user_id:
        return "<script>function myEditItem(){\
                alert('You are not authorized to edit this \
                        ItemCatalog. Please create your own account \
                ');}\
                </script>\
                <body onload='myEditItem()'>"
    if request.method == 'POST':
        if not request.form['name'] or not request.form['description']:
            flash('Either Item Name or Description can not be blank')
            return render_template(
                'editItemCatalog.html',
                catalog_id=catalog_id,
                item_catalog_id=item_catalog_id,
                catalogs=catalogs,
                catalog=catalog,
                item=editItemCatalog)
        if request.form['name']:
            editItemCatalog.name = request.form['name']
        if request.form['description']:
            editItemCatalog.description = request.form['description']
        session.add(editItemCatalog)
        session.commit()
        flash(
            "Item Catalog %s was successfully Editted"
            % editItemCatalog.name)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template(
            'editItemCatalog.html',
            catalog_id=catalog_id,
            item_catalog_id=item_catalog_id,
            catalogs=catalogs,
            catalog=catalog,
            item=editItemCatalog)


# DELETE THE ITEM CATALOG
@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_catalog_id>/delete',
    methods=['GET', 'POST'])
def deleteItemCatalog(catalog_id, item_catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemCatalogToDelete = session.query(ItemCatalog).filter_by(
        id=item_catalog_id).one()
    if login_session['user_id'] != catalog.user_id:
        return "<script>function myDeleteItemCatalog(){\
                alert('You are not authorized to delete this \
                        ItemCatalog. Please create your own account');}\
                </script>\
                <body onload='myDeleteItemCatalog()'>"
    if request.method == 'POST':
        session.delete(itemCatalogToDelete)
        session.commit()
        flash(
            'ItemCatalog %s Was Successfully Deleted'
            % itemCatalogToDelete.name)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template(
            'deleteItemCatalog.html',
            item=itemCatalogToDelete)


"""************************************************************************
    GOOGLE LOG IN
***************************************************************************"""

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return the current session state is s% % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You were successfully log out.", 'success')
        return redirect(url_for('showCatalogs'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('showCatalogs'))

# CONNECT - Google login token


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state paramater.'), 401)
        response.header['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credential object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dump('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

# Check the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
                   -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # excute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset users' session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# User Helper Functions


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
