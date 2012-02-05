"""
Flask-SL Example App

"""
from flask import Flask, request, Response
from flask.ext.sl import SLAware, sl_required


app = Flask(__name__)
app.config.from_pyfile('app.cfg')
sl = SLAware(app)


@app.route('/')
def index():
    response = Response(mimetype='text/plain')
    if request.from_sl:
        response.data = 'Hello, %s!' % request.sl_object.name
    else:
        response.data = 'Hello, visitor!'
    return response
    

@sl_required
@app.route('/sl')
def sl_only():
    response = Response(mimetype='text/plain')
    response.data = "Hello, SL Object from %s." % \
        request.sl_object.region.name
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
