# guestbook

A toy web application that demonstrates one use case for having Javascript embedded in Python -- rendering single-page application views on the server.

Uses [Pure CSS](http://purecss.io) and [React](http://facebook.github.io/react) for the front end and [Pyramid](http://pylonsproject.org) for the back end.

## Getting Started

    ``` bash
    $ pip install -r requirements.txt
    # note that PyV8 may be difficult to install -- get a binary from
    # https://github.com/emmetio/pyv8-binaries if you have trouble
    $ cd <directory containing this file>
    $ $VIRTUAL_ENV/bin/python setup.py develop
	$ $VIRTUAL_ENV/bin/initialize_guestbook_db development.ini
    # note that you can't use the Pyramid default webserver here because
    # it interacts weirdly with PyV8 -- use `wsgiref.simple_server` instead
	$ $VIRTUAL_ENV/bin/python wsgi.py
    ```
