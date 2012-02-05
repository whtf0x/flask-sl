# -*- coding: utf-8 -*-
"""
    flaskext.sl
    ~~~~~~~~~~~~~~~~~~~~

    Impliments basic recognition of Second Life® based (LSL) requests.

    :copyright: (c) 2011 by Bennett Goble.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from functools import wraps
import re, hashlib

from netaddr import IPAddress, IPNetwork
from flask import _request_ctx_stack, abort


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
    (:class: `SLRequestObject`) if ``'SL_PARSE_XHEADERS'`` is `True` (Default.)
    """

    def __init__(self, app=None):

        app.config.setdefault('SL_PARSE_XHEADERS', True)

        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        self.app.before_request(self.before_request)

    def before_request(self):
        request = _request_ctx_stack.top.request
        request.from_sl = from_sl(request.remote_addr)

        if request.from_sl and self.app.config['SL_PARSE_XHEADERS']:
            request.sl_object = SLRequestObject(request=request)


def sl_required(fn):
    """Use this decorator to limit routes to requests
    originating from Second Life. Aborts with an 
    Unauthorized 401 response.

        @app.route('/sl')
        @sl_required
        def sl_only():
            pass

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.from_sl():
            abort(401)


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
        try:
            x, y, z = re.split('\(|, |\)', vector_str)[1:4]
            return SLVector3(x=float(x), y=float(y), z=float(y))
        except ValueError:
            return SLVector3()

    @staticmethod
    def from_xheader_vel(vector_str):
        try:
            x, y, z = vector_str.split(', ')
            return SLVector3(x=float(x), y=float(y), z=float(y))
        except ValueError:
            return SLVector3()


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
        try:
            x, y, z, s = quaternion_str.split(', ')
            return SLVector3(x=float(x), y=float(y), z=float(y), s=float(s))
        except ValueError:
            return SLQuaternion()


class SLRegion(object):
    """Container class for parsed X-SecondLife-Region header."""

    x = 0
    y = 0
    name = ""

    @staticmethod
    def from_xheader(region_str):
        try:
            name, x, y = re.split(',|\(|\)|', region_str)[:3]
            region = SLRegion()
            region.name = name
            region.x = int(x)
            region.y = int(y)
        except ValueError:
            return SLRegion()
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
        self.velocity   = SLVector3.from_xheader_vel(request.headers["X-SecondLife-Local-Velocity"])
        self.owner_name = request.headers["X-SecondLife-Owner-Name"]
        self.owner_key  = request.headers["X-SecondLife-Owner-Key"]

    def __repr__(self):
        return "<SLRequestObject %s (Owner: %s, Location: %s %s)>" % \
            (self.name, self.owner_name, self.region.name, self.position)


def SLHMAC(plaintext, key):
    return hashlib.sha1(key + hashlib.sha1(key + plaintext).hexdigest()).hexdigest()
