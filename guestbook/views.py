import json
import datetime
import logging

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render_to_response

from sqlalchemy.exc import DBAPIError

from .models import DBSession, Guest
from .render_react import render as render_react

log = logging.getLogger(__name__)


@view_config(route_name='index')
def index_view(request):
    """
    Lists all the guests going -- when rendering HTML, also provides
    the main announcement and sign-up page.
    """
    try:
        guests = DBSession.query(Guest).order_by(Guest.signed_up_at).all()
    except DBAPIError:
        return Response(conn_err, content_type='text/plain', status_int=500)

    data = {
        "title": "game night",
        "subtitle": "friday, august 22nd",
        "announcement": '''
    The inimitable <a href="http://socialtables.com">Social Tables</a> is
    organizing a <a href="https://twitter.com/hashtag/dctech">#dctech</a>
    game night at <a href="http://1776dc.com">1776</a>! Whether you prefer a
    traditional LAN party or a (currently disturbingly topical) game of
    <em>Pandemic</em>, everyone is welcome!
        ''',
        "guests": guests
    }

    # Only go through the bother of rendering the Javascript and so on if
    # we're asking for HTML
    if request.accept.accept_html:
        content = render_react("static/jsx/app.jsx", "MainComponent", data)
        response = render_to_response(
            "templates/index.html",
            {"rendered_content": content, "initial_data": data},
            request=request)
        log.debug("rendered: %r", content)
    else:
        response = render_to_response("json", data, request=request)

    return response


@view_config(route_name="signup", renderer="json")
def signup_view(request):
    """
    Accepts a POST of signup data, sets the appropriate values, and
    sends the updated list of guests as a response.
    """
    if request.method != "POST":
        request.response.status = "405 Method Not Allowed"
        return {"error": "Only POSTs are accepted here."}

    try:
        log.debug("Got POST: %r", request.body)
        new_guest_data = request.json_body
        new_guest_data["signed_up_at"] = datetime.datetime.now()
        if "id" in new_guest_data:
            del new_guest_data["id"]  # drop any client-side ID
        new_guest = Guest(**new_guest_data)
    except Exception as e:
        log.error(e)
        return Response(status_int=400)

    try:
        DBSession.add(new_guest)
        DBSession.flush()
        guests = DBSession.query(Guest).order_by(Guest.signed_up_at).all()
    except DBAPIError:
        return Response(conn_err, content_type='text/plain', status_int=500)

    request.response.status = "201 Created"
    return {"guests": guests}


# Handy scaffold-generated connection error message
conn_err = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_guestbook_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
