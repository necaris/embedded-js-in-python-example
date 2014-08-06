import time
import json
import logging

import PyV8

from .utils import absolute_path_in_app, ORMEncoder

log = logging.getLogger(__name__)


JSX_TRANSFORMER_PATH = absolute_path_in_app(
    "static/js/JSXTransformer-0.11.1.js")
REACT_LIB_PATH = absolute_path_in_app(
    "static/js/react-with-addons-0.11.1.min.js")


def transform_jsx(source, path=None):
    """
    Transform the given JSX source into regular Javascript and return
    the generated source.

    Also compile it into a PyV8 object and create an extension to
    embed in future PyV8 contexts.
    """
    log.debug("Transforming JSX for %r", path)
    if "lib/jsx" in PyV8.JSExtension.extensions:
        log.debug("JSX extension already loaded")
    else:
        with open(JSX_TRANSFORMER_PATH) as jsxf:
            jsx_transformer_js = jsxf.read()
        # Inject the `global` var which it needs to function -- ensure
        # that it doesn't clobber any existing global var though!
        jsx_transformer_js = """
var global = ("undefined"!==typeof global) ? global : {};
%s
var JSXTransfomer = global.JSXTransformer;
""" % jsx_transformer_js

        log.debug("Read JSXTransformer")
        ext = PyV8.JSExtension("lib/jsx", jsx_transformer_js)
        log.debug("Created extension: %r ; now the set is %r",
                  ext, PyV8.JSExtension.extensions)

    log.debug("Evaluating JSX")
    script = """
var jsxSource = %r;
global.JSXTransformer.transform(jsxSource);
""" % source

    with PyV8.JSContext(extensions=["lib/jsx"]) as ctx:
        log.debug("running in context: %r", ctx)
        result = ctx.eval(script)
        log.debug("evaluated: %r", result)
        result_code = result.code

    log.debug("Transformed JSX")
    return result_code


def make_js_bundle(app_js_path):
    """
    Compile the given application Javascript into a PyV8 JSExtension.
    Caches extensions it's compiled under their path, so if the path
    is already compiled doesn't do the work again.

    Transforms any JSX, not only compiling it as an extension but also
    writing it to a corresponding .js file for client-side loading.

    Also bundles the React and Moment.js libraries, which are used by
    the client-side code.
    """
    if app_js_path in PyV8.JSExtension.extensions:
        log.debug("Application code already loaded")
        return

    log.debug("Loading React library")
    if "lib/react" in PyV8.JSExtension.extensions:
        log.debug("Extension already loaded")
    else:
        start = time.time()
        with open(REACT_LIB_PATH, 'r') as react_f:
            react_js = react_f.read()
        log.debug("TIME: Read in %.3f", (time.time() - start) * 1000)
        # Ensure the `global` var is defined, as it's needed, but
        # don't destroy any existing context
        react_js = """
var global = ("undefined"!==typeof global) ? global : {};
%s
var React = global.React;
""" % react_js
        # Register the extension for later use
        ext = PyV8.JSExtension("lib/react", react_js)
        log.debug("Created extension: %r", ext)

    if "lib/moment" in PyV8.JSExtension.extensions:
        log.debug("Moment extension already loaded")
    else:
        start = time.time()
        with open(absolute_path_in_app("static/js/moment.min.js"), 'r') as m_f:
            moment_js = m_f.read()
        log.debug("TIME: Moment read in %.3f", (time.time() - start) * 1000)
        # Ensure global and window are defined so we can access the
        # library later
        moment_js = """
var window = ("undefined"!==typeof global) ? global : {};
%s
var moment = global.moment;
""" % moment_js
        # Register the extension for later use
        ext = PyV8.JSExtension("lib/moment", moment_js)
        log.debug("Created Moment extension: %r", ext)

    log.debug("Loading JS application code")
    start = time.time()
    with open(absolute_path_in_app(app_js_path), 'r') as app_f:
        app_js = app_f.read()

    if app_js_path.endswith('.jsx'):
        log.debug("Transforming JSX")
        app_js = transform_jsx(app_js, app_js_path)
        log.debug("Writing transformed JS")
        transformed_path = app_js_path.replace('jsx', 'js')
        with open(absolute_path_in_app(transformed_path), 'w') as out:
            out.write(app_js)
        log.debug("...done")

    log.debug("TIME: Loaded in %.3f", (time.time() - start) * 1000)

    start = time.time()
    ext = PyV8.JSExtension(app_js_path, app_js)
    log.debug("TIME: Compiled in %.3f", (time.time() - start) * 1000)


def render(app_js_path, component_name, component_data):
    """
    Use React's `renderComponentToString` function to render the given
    component using the given data.
    """
    make_js_bundle(app_js_path)  # compilation is a side effect...
    log.debug("Initializing JS context")

    start = time.time()
    serialized_data = json.dumps(component_data, cls=ORMEncoder)
    log.debug("TIME: Serialized component data in %.3f",
              (time.time() - start) * 1000)

    script = '''
// Force output to string
React.renderComponentToString(%s(%s));
''' % (component_name, serialized_data)
    start = time.time()
    ctx = PyV8.JSContext(extensions=["lib/react", "lib/moment", app_js_path])
    log.debug("TIME: Created context in %.3f", (time.time() - start) * 1000)
    start = time.time()
    with ctx:
        try:
            result = ctx.eval(script)
        except Exception as e:
            log.error("Javascript error! %r", e)
            raise

    log.debug("TIME: Evaluated bundle in %.3f", (time.time() - start) * 1000)
    return result


if __name__ == '__main__':
    print(render("static/jsx/app.jsx", "MainComponent", {
            "title": "test",
            "subtitle": "a sample subtitle",
            "announcement": '''Some content here'''
        }))
