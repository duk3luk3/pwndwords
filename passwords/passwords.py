from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
# Default settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://erlacher@/passwords'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Override settings as needed (http://flask.pocoo.org/docs/dev/config/#configuring-from-files)
app.config.from_envvar('PWNDPW_SETTINGS', silent=True)
db = SQLAlchemy(app)

from sqlalchemy import Column, Integer, text
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import codecs, string

Base = declarative_base()

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    hash = Column(BYTEA)

# Everything converter adapted from https://stackoverflow.com/a/24001029
from werkzeug.routing import PathConverter

class EverythingConverter(PathConverter):
    regex = '..*?'

app.url_map.converters['everything'] = EverythingConverter

def lookup(hash):
    def try_decode(hash):
        if len(hash)==40 and not request.args.get('originalPasswordIsAHash'):
            if all(c in string.hexdigits for c in hash):
                return codecs.decode(hash, 'hex')
    if hash:
        decoded_hash = try_decode(hash)
        if decoded_hash is not None:
            query = db.session.query(Password).filter(text('substring(:hash for 7) = substring(hash for 7) and :hash = hash')).params(hash=decoded_hash)
            print ('querying hash directly')
        else:
            query = db.session.query(Password).filter(text('substring(digest(:hash,\'sha1\') for 7) = substring(hash for 7) and digest(:hash,\'sha1\') = hash')).params(hash=hash)
#        print(str(query.statement.compile(dialect=postgresql.dialect())))
        hit = query.count()
        if hit > 0:
            return ('Found!', 200, {'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/plain'})
        else:
            return ('Not found!', 404, {'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/plain'})
    else:
        return ('No password', 400, {'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/plain'})

# Route that works like https://haveibeenpwned.com/API/v2#PwnedPasswords
# (and has similar problems with url parsing)
@app.route('/<everything:hash>')
def by_path(hash):
    return lookup(hash)

# This route exists in case you have problems with the path-like passing of
# the password and hash, since e.g. having / characters in them can screw you up.
# Both flask/werkzeug and your webserver can screw you here.
@app.route('/')
def by_param():
    return lookup(request.args.get('password'))
