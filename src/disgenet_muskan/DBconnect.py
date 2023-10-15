#File create Database connection
from sqlalchemy import create_engine


#creating database if not present:
engine_new = create_engine(f'mysql+pymysql://root:root_passwd@127.0.0.1:3307')
with engine_new.connect() as connection:
    connection.execute("CREATE DATABASE IF NOT EXISTS disgenet")
    connection.execute("USE disgenet")
print("Database created and selected successfully.")

# Create the connection string; using port 3307 instead of 3306
connection_string = f'mysql+pymysql://root:root_passwd@127.0.0.1:3307/disgenet'
engine = create_engine(connection_string)