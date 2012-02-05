========
Flask-SL
========
:Version: 0.01

Flask-SL is an extension for `Flask`_ that adds basic recognition
of `Second Life`_ |trademark| based (`LSL`_ script) requests. It can 
parse `X-SecondLife`_ headers into a Python object for easy reference 
within Flask applications.

Installation
------------

To install from source:
::

    $ tar xvfz flask-sl-v0.01.tar.gz 
    $ cd flask-sl-v0.01
    $ python setup.py build
    $ python setup.py install

Configuration
-------------

After configuring your application pass it to a *SLAware* 
object::

    from flask import Flask
    from flask.ext.sl import SLAware

    app = Flask(__name__)
    app.config.from_pyfile('my_config.cfg')
    sl = SLAware(app)

If you are using an application factory the extension may be
configured with the standard *init_app* function.

Usage
-----

Flask-SL adds a *from_sl* attribute to the `Flask`_ *request* 
object. An `example application`_ is available in the `git repository`_.

In addition, if the configuration value SL_PARSE_XHEADERS is True
(default) then SL objects' `X-SecondLife`_ Headers are parsed into a 
*SLRequestObject* available as the attribute *sl_object*::

    @app.route('/')
    def index():
        response.headers['Content-Type'] = 'text/plain'
        if request.from_sl:
            return 'Hello, %s!' % request.sl_object.name
        else:
            return 'Hello, visitor!'

A decorator *sl_required* is provided to limit routes to SL-based 
requests::

    @app.route('/sl_only')
    @sl_required
    def sl_only():
        pass  
        
.. _Flask: http://flask.pocoo.org/
.. _Second Life: http://secondlife.com/
.. _LSL: http://wiki.secondlife.com/wiki/LSL_Portal
.. _X-SecondLife: http://wiki.secondlife.com/wiki/LlHTTPRequest
.. _example application: 
   https://github.com/nivardus/flask-secondlife/tree/master/examples
.. _git repository: https://github.com/nivardus/flask-secondlife/
 
.. |trademark| unicode:: 0xAE
