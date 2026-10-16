


from apps.database.connection import get_connection


def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            customer TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()