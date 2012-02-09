# -*- coding: utf-8 -*-
"""
    flaskext.sl
    ~~~~~~~~~~~~~~~~~~~~

    Implements basic recognition of Second Life® based (LSL) requests.

    :copyright: (c) 2012 by Bennett Goble.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from functools import wraps
import re, hashlib

from netaddr import IPAddress, IPNetwork
from flask import _request_ctx_stack, request, abort


__all__ = ['SLAware', 'sl_required']


# http://wiki.secondlife.com/wiki/Simulator_IP_Addresses
SL_ADDRESS_RANGES_USED = [
    IPNetwork('216.82.0.0/18'),
    IPNetwork('8.2.32.0/22'),
    IPNetwork('8.4.128.0/22'),
    IPNetwork('8.10.144.0/21'),
    IPNetwork('63.210.156.0/22'),
    IPNetwork('64.154.220.0/22')
]


class SLAware(object):
    """Flask-SecondLife main class. Initializing this extension with
    a Flask application will cause all requests to receive the attribute
    :attr: `from_sl` and a parsed Python object :attr: `sl_object` 
    (:class:`SLRequestObject`) if ``'SL_PARSE_XHEADERS'`` is `True` (Default.)
    """

    def __init__(self, app=None):

        self.bad_request_callback = None
        self.unauthorized_callback = None

        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        self.app.config.setdefault('SL_PARSE_XHEADERS', True)
        self.app.before_request(self.before_request)

    def before_request(self):
        request = _request_ctx_stack.top.request
        request.from_sl = from_sl(request.remote_addr)

        if request.from_sl and self.app.config['SL_PARSE_XHEADERS']:
            #try:
            request.sl_object = SLRequestObject(request=request)
            #except ValueError, AttributeError:
            #    self.bad_request()

    def bad_request_handler(self, callback):
        """Set callback for :meth:`bad_request` method."""
        self.bad_request_handler = callback
    
    def bad_request(self):
        """Called when there is an ill-formatted request"""
        if self.bad_request_callback:
            return self.bad_request_callback()
        abort(400)

    def unauthorized_handler(self, callback):
        """Set callback for :meth:`unauthorized` method."""
        self.unauthorized_callback = callback

    def unauthorized(self):
        """Called when request does not originate from SL
        on a route decorated with :meth:`sl_required`."""
        if self.unauthorized_callback:
            return self.unauthorized_callback()
        abort(401)

    def sl_required(self, fn):
        """Use this decorator to limit routes to requests
        originating from Second Life. Aborts with an 
        Unauthorized 401 response.

            @app.route('/sl')
            @sl.sl_required
            def sl_only():
                pass

        """
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not request.from_sl:
                self.unauthorized() 
            return fn(*args, **kwargs)           
        return decorated_view


def from_sl(address):
    ip = IPAddress(address)
    for network in SL_ADDRESS_RANGES_USED:
        if ip in network:
            return True
    return False


class SLVector3():
    """Container class for parsed vector3 X-SecondLife headers."""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if isinstance(other, Vector3):
            return self.x == other.x and \
                   self.y == other.y and \
                   self.z == other.z
        return self == other

    def __repr__(self):
        return "<%s, %s, %s>" % (self.x, self.y, self.z)

    @staticmethod
    def from_xheader(vector_str):
        x, y, z = re.findall(r"\d+.\d+", vector_str)
        return SLVector3(x=float(x), y=float(y), z=float(y))


class SLQuaternion():
    """Container class for parsed quaternion X-SecondLife headers."""

    def __init__(self, x=0.0, y=0.0, z=0.0, s=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.s = s

    def __eq__(self, other):
        if isinstance(other, SLQuaternion):
            return self.x == other.x and \
                   self.y == other.y and \
                   self.z == other.z and \
                   self.s == other.s
        return self == other

    def __repr__(self):
        return "<%s, %s, %s, %s>" % (self.x, self.y, self.z, self.s)

    @staticmethod
    def from_xheader(quaternion_str):
        x, y, z, s = re.findall(r"\d+.\d+", quaternion_str)
        return SLQuaternion(x=float(x), y=float(y), z=float(y), s=float(s))


class SLRegion(object):
    """Container class for parsed X-SecondLife-Region header."""

    x = 0
    y = 0
    name = ""

    @staticmethod
    def from_xheader(region_str):
        name = re.findall(r"([\w ]+) \(", region_str)[0]
        x, y = re.findall(r"\d+", region_str)
        region = SLRegion()
        region.name = name
        region.x = int(x)
        region.y = int(y)
        return region

    def __repr__(self):
        return "<%s, (%s, %s)>" % (self.name, self.x, self.y)


class SLRequestObject(object):
    """Container class for parsed X-SecondLife HTTP Headers."""

    name       = ""
    key        = ""
    region     = ""
    position   = None
    rotation   = None
    velocity   = None
    owner_name = ""
    owner_key  = ""

    def __init__(self, request=None):
        if request is not None:
            self.from_request(request);

    def from_request(self, request):
        self.name       = request.headers["X-SecondLife-Object-Name"]
        self.key        = request.headers["X-SecondLife-Object-Key"]
        self.region     = SLRegion.from_xheader(request.headers["X-SecondLife-Region"])
        self.position   = SLVector3.from_xheader(request.headers["X-SecondLife-Local-Position"])
        self.rotation   = SLQuaternion.from_xheader(request.headers["X-SecondLife-Local-Rotation"])
        self.velocity   = SLVector3.from_xheader(request.headers["X-SecondLife-Local-Velocity"])
        self.owner_name = request.headers["X-SecondLife-Owner-Name"]
        self.owner_key  = request.headers["X-SecondLife-Owner-Key"]

    def __repr__(self):
        return "<SLRequestObject %s (Owner: %s, Location: %s %s)>" % \
            (self.name, self.owner_name, self.region.name, self.position)
