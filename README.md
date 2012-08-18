Flask-SL
========
Version 0.02

Flask-SL is an extension for [Flask][flask] that adds basic recognition
of [Second Life][sl]&reg; based ([LSL][lsl] script) requests. It can 
parse [X-SecondLife][headers] headers into a Python object for easy reference 
within Flask applications.

Installation
------------

To install from source:

    $ git clone git@github.com:nivardus/flask-sl.git
    $ cd flask-sl
    $ python setup.py build
    $ python setup.py install

Configuration
-------------

After configuring your application pass it to a *SLAware* 
object:

```python
from flask import Flask
from flask.ext.sl import SLAware

app = Flask(__name__)
app.config.from_pyfile('my_config.cfg')
sl = SLAware(app)
```

If you are using an application factory the extension may be
configured with the standard *init_app* function.

Usage
-----

Flask-SL adds a *from_sl* attribute to the Flask request 
object. See the [example application][examples].

In addition, if the configuration value SL_PARSE_XHEADERS is True
(default) then SL objects' [X-SecondLife][headers] headers are parsed into a 
*SLRequestObject* available as the attribute *sl_object*:

```python
@app.route('/')
def index():
    if request.from_sl:
        return 'Hello, %s!' % request.sl_object.name
    else:
        return 'Hello, visitor!'
```

A decorator *SLAware.sl_required* is provided to limit routes to SL-based 
requests:

```python
@app.route('/sl_only')
@sl.sl_required
def sl_only():
    return 'Hello, SL object.' 
```

Bad Response Callbacks
----------------------
If Flask-SL receives a non-SL originating request on a route
restricted with `sl_required` it will `abort` the response with
status 401. If you wish to handle this differently decorate a
function with `SLAware.unauthorized_handler`.

```python
@sl.unauthorized_handler
def unauthorized():
    return 'Request not from SL.'
```

The decorator `SLAware.bad_request_handler` is also supplied to
specify a callback for requests with un-parsable X-SecondLife
headers. Generally this should never happen, but if Flask-SL
is adapted for use with Non-Linden Labs&reg; servers it may
be useful. 

[flask]: http://flask.pocoo.org/
[sl]: http://secondlife.com/ "Official Second Life Homepage"
[lsl]: http://wiki.secondlife.com/wiki/LSL_Portal "Linden Scripting Language"
[headers]: http://wiki.secondlife.com/wiki/LlHTTPRequest "X-SecondLife HTTP Header Documentation"
[examples]: https://github.com/nivardus/Flask-SL/tree/master/examples "Flask-SL Examples"
[repo]: https://github.com/nivardus/Flask-SL "Flask-SL Github Repository"
