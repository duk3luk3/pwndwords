from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://erlacher@/passwords'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

from werkzeug.routing import PathConverter

class EverythingConverter(PathConverter):
    regex = '.*?'

app.url_map.converters['everything'] = EverythingConverter

@app.route('/<everything:hash>')
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
