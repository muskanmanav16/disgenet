import os
from sqlalchemy import create_engine,inspect
import requests

#Defining the constants
DISGENET = "disgenet"
DISGENET_BASE = "https://www.disgenet.org/static/disgenet_ap1/files/downloads/"
DISGENET_GDP_ASSOC = DISGENET_BASE + "all_gene_disease_pmid_associations.tsv.gz"
DISGENET_VDP_ASSOC = DISGENET_BASE + "all_variant_disease_pmid_associations.tsv.gz"
current_dir = os.getcwd()
DATA_DIR = os.path.join(current_dir, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def download_file(url, file_path):
    if os.path.exists(file_path):
        print(f"File already exists at {file_path}. Skipping download.")
        return True
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

# download_file(DISGENET_GDP_ASSOC, os.path.join(DATA_DIR, 'all_gene_disease_pmid_associations.tsv.gz'))
# download_file(DISGENET_VDP_ASSOC, os.path.join(DATA_DIR, 'all_variant_disease_pmid_associations.tsv.gz'))
# print(f'Data Downloaded : {DATA_DIR} ')


#creating database if not present:
engine_new = create_engine(f'mysql+pymysql://root:root_passwd@127.0.0.1:3307')
with engine_new.connect() as connection:
    connection.execute("CREATE DATABASE IF NOT EXISTS disgenet")
    connection.execute("USE disgenet")
    # connection.dispose()
print("Database created and selected successfully.")

# Create the connection string
connection_string = f'mysql+pymysql://root:root_passwd@127.0.0.1:3307/disgenet'
engine = create_engine(connection_string)

