import os
from neo4j_tools import Db, Node, Edge
from disgenet_muskan.constants import DATA_DIR,DISGENET_GDP_ASSOC,DISGENET_VDP_ASSOC,DISGENET_GDP_FILE,DISGENET_VDP_FILE
from disgenet_muskan.DBconnect import engine
from disgenet_muskan.disgenet import Disgenet
from disgenet_muskan.models import Base
import requests

def download_file(url, file_path, update=False):
    """
    Downloads a file from a given URL to the specified file path.

    Args:
        url (str): The URL of the file to download.
        file_path (str): The local file path where the downloaded file will be saved.
        force_download (bool, optional): If True, the file will be downloaded even if it already exists locally.
            If False, the download will be skipped if the file already exists.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    if os.path.exists(file_path) and not update: #give user update option for the already downloaded file
        print(f"File already exists at {file_path}. Skipping download.") #skipping download if file already exists
        return True
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return True
    return False


def populate_data(engine=engine,update=False):
    """defining wrapper methods which can download the file and populating the database

    Args:
        engine (sqlalchemy.engine.base.Connection, optional): The SQLAlchemy engine for the database connection.
            If not provided, Defaults to engine.
        update(Bool): allows user to have a option to update the files if already present,
            Defaults to False.
    """    
    download_file(DISGENET_GDP_ASSOC, os.path.join(DATA_DIR, DISGENET_GDP_FILE,update=update))
    download_file(DISGENET_VDP_ASSOC, os.path.join(DATA_DIR, DISGENET_VDP_FILE,update=update))                                 
    d = Disgenet()
    Base.metadata.drop_all(engine)       # drop if already exists
    Base.metadata.create_all(engine)     # re-create incase it already exists, to avoid duplicates   
    d.insert_data()
    d.session.close()

def create_neo4jgraph(file: str, graph_config=True, delete_nodes=False):
    """Takes the name of the file which is already copied into the Neo4j container

    Args:
        file (str): name of the file
        graph_config (bool, optional): It should be True if
        only one file is loaded, else it should be False. Defaults to True.
        delete_nodes (bool, optional): If True, delete all nodes before importing the new data. Defaults to False.

    Returns:
        list: list of the number of edges and nodes in the graph
    """    
    db = Db()
    
    if not delete_nodes:
        db.delete_all_nodes()
        print('Delete existing nodes')
    file_name = 'file:///data/' + file
        
    db.import_ttl(file_name, init_graph_config=graph_config)
    
    return [db.get_number_of_edges(), db.get_number_of_nodes()]