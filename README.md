# pwndwords

Pwned Passwords API inspired by HIBP

## Routes

GET `/<password>` To pass the password as path component

GET `/` To pass the password as GET parameter `password`

Both routes also support `originalPasswordIsAHash` as GET parameter analogous to [HIBP](https://haveibeenpwned.com/API/v2#PwnedPasswords)

## Setting up

Needs a postgresql database with a `passwords` table like this:

```sql
CREATE EXTENSION pgcrypto;
CREATE TABLE passwords ( id bigserial PRIMARY KEY, hash bytea);
CREATE INDEX ON passwords (substring(hash for 7));
```

Supports reading configuration from a file referenced in Env Var `PWNDPW_SETTINGS`. File should look like this:

```
SQLALCHEMY_DATABASE_URI = postgresql+psycopg2://user:password@host/passwords
```

## WSGI and Virtualenv

The `venv.wsgi` file is for running this app via wsgi from a Virtualenv, like described in the [Flask WSGI docs](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/#working-with-virtual-environments).

If you are running an OS with a gimped virtualenv implementation, `activate_this.py` is provided free of charge.
