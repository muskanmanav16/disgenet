import os
from sqlalchemy import create_engine,inspect
import re

DISGENET = "disgenet"
DISGENET_BASE = "https://www.disgenet.org/static/disgenet_ap1/files/downloads/"
# DISGENET_GDP_ASSOC = DISGENET_BASE + "all_gene_disease_pmid_associations.tsv"#.gz"
# DISGENET_VDP_ASSOC = DISGENET_BASE + "all_variant_disease_pmid_associations"#.tsv.gz"
DISGENET_GDP_ASSOC = DISGENET_BASE + "all_gene_disease_pmid_associations.tsv"#.gz"
DISGENET_VDP_ASSOC = DISGENET_BASE + "all_variant_disease_pmid_associations.tsv"#.gz"
HOME = os.path.expanduser("~")
PROJECT_DIR = os.path.join(HOME, "disgenet") 
DATA_DIR = os.path.join(PROJECT_DIR, "data") #



# Create the connection string
connection_string = f'mysql+pymysql://root:root_passwd@127.0.0.1:3307/disgenet'
#connection_string = f'mysql+pymysql://root:root_passwd@127.0.0.1:3307'
# Create the SQLAlchemy engine
engine = create_engine(connection_string)
# Execute SQL statements
with engine.connect() as connection:
    connection.execute("CREATE DATABASE IF NOT EXISTS disgenet")
    connection.execute("USE disgenet")
print("Database created and selected successfully.")




def get_file_path(url: str, biodb: str):
    """Get standard file path by file_name and DATADIR."""
    file_name = os.path.basename(url)
    bio_db_dir = os.path.join(DATA_DIR, biodb)
    os.makedirs(bio_db_dir, exist_ok=True)
    return os.path.join(bio_db_dir, file_name)


def get_standard_name(name: str) -> str:
    """Return standard name."""
    part_of_name = [x for x in re.findall("[A-Z]*[a-z0-9]*", name) if x]
    new_name = "_".join(part_of_name).lower()
    if re.search(r"^\d+", new_name):
        new_name = "_" + new_name
    return new_name


def standardize_column_names(columns) :
        """Standardize column names.

        Parameters
        ----------
        columns: Iterable[str]
            Iterable of columns names.
        """
        return [get_standard_name(x) for x in columns]