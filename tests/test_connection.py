from taxoninsertion import neo_connect
from dotenv import load_dotenv
from json import loads
from os import getenv

def test_dotenv():
    load_dotenv()
    CONN_STRING = loads(getenv("DBAUTH"))
    assert 'dbname' in CONN_STRING, "No field dbname in the DBAUTH environment variable."
    assert 'host' in CONN_STRING, "No field host in the DBAUTH environment variable."
    assert 'user' in CONN_STRING, "No field user in the DBAUTH environment variable."
    assert 'port' in CONN_STRING, "No field port in the DBAUTH environment variable."
    assert 'password' in CONN_STRING, "No field password in the DBAUTH environment variable."

def test_database_connection():
    load_dotenv()
    CONN_STRING = loads(getenv("DBAUTH"))
    con = neo_connect(CONN_STRING)
    assert hasattr(con, 'info'), "An invalid connection object is being returned."
    assert con.info.vendor == 'PostgreSQL', "We don't seem to be connected to Postgres."
    assert con.info.status == 0, "There is not a good connection."
    con.close()
    assert con.info.status == 1, "The connection is not closing properly."
