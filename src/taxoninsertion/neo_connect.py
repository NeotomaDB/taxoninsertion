import psycopg

def neo_connect(CONN_STRING: dict) -> psycopg.Connection:
    """_summary_

    Args:
        CONN_STRING (obj): _A valid Python object _

    Returns:
        psycopg.Connection: _description_
    """
    return psycopg.connect(**CONN_STRING, connect_timeout=5)
