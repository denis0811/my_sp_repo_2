import psycopg2
from my_classes.db import db

def get_next_index():

    db.load_config('database1.ini') 
    db_config = db.get_config()

    # Connect to the PostgreSQL database using the configuration details
    conn = psycopg2.connect(**db_config)
    
    # Create a cursor object
    cur = conn.cursor()

    # Create the index table if it doesn't exist
    cur.execute("CREATE TABLE IF NOT EXISTS index_table (next_index INTEGER)")

    # Get the current index value from the table
    cur.execute("SELECT next_index FROM index_table")
    result = cur.fetchone()

    if result is None:
        # If the table is empty, start the index at 1
        next_index = 1
        cur.execute("INSERT INTO index_table (next_index) VALUES (%s)", (next_index,))
    else:
        # Otherwise, increment the current index by 1
        next_index = result[0] + 1
        cur.execute("UPDATE index_table SET next_index = %s", (next_index,))

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

    # Return the next index value to the calling program
    return next_index

# for i in range(900, 2002):
#     print(get_next_index())