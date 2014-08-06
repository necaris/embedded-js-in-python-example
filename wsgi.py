# Trivial server script, to get us going since Waitress isn't working out
import logging
from wsgiref.simple_server import make_server
from pyramid.paster import get_app


if __name__ == '__main__':
    # Set up the logging
    logging.config.fileConfig("development.ini")
    # Now create and serve the WSGI application
    application = get_app('development.ini')
    server = make_server('127.0.0.1', 6543, application)
    print("Serving on 127.0.0.1:6543...")
    server.serve_forever()
