# Activate python environment

```sh
python3 -m venv venv
```
```sh
source venv/bin/activate
```

# Install dependencies

```sh
pip install -r requirements.txt
```

## Setting up the database

### Install invoke

```sh
pip install invoke
```

```sh
invoke init-db
```

This will do the following:
- create the words.db (Sqlite3 database)
- run the migrations found in `seeds/`
- run the seed data found in `seed/`

Please note that migrations and seed data is manually coded to be imported in the `lib/db.py`. So you need to modify this code if you want to import other seed data.

## Clearing the database

Simply delete the `words.db` to clear entire database.



## Running the backend api

```sh
python app.py 
```

This should start the flask app on port `5000`
