"""
    Application specific functions/filters/tests in Jinja2
    (note: this is not complete, but it works for me! I hope it can be useful for you)

    The Integration code was originally based on
    http://lethain.com/entry/2008/jul/22/replacing-django-s-template-language-with-jinja2/
    But I changed it so much that nothing much is left from the original.


    This module provides jinja2 integration with django that features
    automatic loading of application-specific functions/filters/tests to the
    environment of Jinja
    (plus enabling auto escape)


    To define global functions:
      put a jtemp.py module in your application directory, and it will be imported
    into the globals dictionary of the environment under the namespace of your
    application.
    so if your app is called "news" and you define a function "top_stories" in jtemp.py
    then from the template, you can access it as "news.top_stories()", for example:
    {% set top_stories = news.top_stories() %}

    To define filters:
      put a jfilters.py module in your application directory, and any function in it
    that  starts with "filter_" will be added to the filters dictionary of the
    environment without the filter_ prefix (so filter_url will be called "url")

    To define tests:
      put a jtests.py module in your application directory, and any function in it that
    starts with "is_" will be added to the tests dictionary of the environment without
    the "is_" prefix, (so is_odd will be called "odd")


    To use this, i put it in a file called jinja.py and if I need to respond to an http
    request with a page that's rendered in jinja, I just say:
    # from myproj.jinja import jrespond
    and when I return a response:
    # return jrespond( template_file_name, context )
"""


from django.conf import settings
from django.http import HttpResponse
from jinja2 import Environment, FileSystemLoader, PackageLoader, ChoiceLoader, exceptions as jexceptions
#from eve.lib.context_processors import what_browser
from django.template.context import get_standard_processors

def import_module(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

# environment setup:
#  the loader here searches "template dirs", plus any templates folder in any installed app
#  autoescape set to true explicitly, because in Jinja2 it's off by defualt
jenv = Environment(autoescape=False,
                   line_statement_prefix='#',
                   trim_blocks=True,
                   #extensions=['jinja2.ext.do'],
                   loader = ChoiceLoader(
                        [FileSystemLoader(settings.TEMPLATE_DIRS)]
                        + [PackageLoader(app) for app in settings.INSTALLED_APPS]
                    )
)

# Search for and load application specific functions, filters and tests.
for app in settings.INSTALLED_APPS: #import jtemp.py from each app and add it to globals
    try:
        jtemp = import_module( app + '.jtags' )
        app_name = app.split('.')[-1] #application name
        #if jtemp defines jinja_name, use it as the module name in jinja, otherwise use application name
        name = getattr( jtemp, 'jinja_name', app_name )
        jenv.globals[name] = jtemp
    except ImportError:
        pass
    try:
        filters = import_module( app + '.jfilters' )
        filter_functions = [getattr(filters,filter) for filter in dir(filters) if callable(getattr(filters,filter)) and filter.startswith("filter_")]
        for func in filter_functions:
            jenv.filters[getattr(func, 'jinja_name', func.__name__[7:])] = func
    except ImportError:
        pass
    try:
        tests = import_module( app + '.jtests' )
        test_functions = [getattr(tests,test) for test in dir(tests) if callable(getattr(tests,test)) and test.startswith("is_")]
        for func in test_functions:
            jenv.tests[getattr(func, 'jinja_name', func.__name__[3:])] = func
    except ImportError:
        pass

def get_select_template( filenames ):
    """ get or select template; accepts a file name or a list of file names """
    if type( filenames ) == type([]):
        for file in filenames:
            try: return jenv.get_template( file )
            except jexceptions.TemplateNotFound: pass
        raise jexceptions.TemplateNotFound( filenames )
    else:
        file = filenames #for better readability
        return jenv.get_template( file )

def jrender(filename, context={}):
    """ renders a jinja template to a string """
    template = get_select_template(filename)
    return template.render(**context)

def render_to_response( filename, context={}, request=None ):
    """ renders a jinja template to an HttpResponse """
    if request:
        for processor in get_standard_processors():
            context.update(processor(request))

    return HttpResponse( jrender( filename, context ) )
