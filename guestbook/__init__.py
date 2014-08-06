import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession, Base

_current_dir = os.path.abspath(os.path.dirname(__file__))


def main(global_config, **settings):
    """
    Return a new application instance, appropriately configured.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)

    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path(
        os.path.join(_current_dir, "templates"))

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('signup', '/signup')

    config.scan()
    return config.make_wsgi_app()
