# # Neo4j Tools
# ## Importing ttl files into Neo4J
# 1. Make sure your Neo4J is running
# 2. Go in podman-Desktop Neo4j Terminal and 

# ```bash
# cd $NEO4J_HOME/plugins
# wget https://github.com/neo4j-labs/neosemantics/releases/download/5.7.0.0/neosemantics-5.7.0.0.jar
# ```

# 3. Stop the Neo4j container ans restart
# 4. Go in podman-Desktop to Volumes
# 5. Click `biodb_biodb_neo4j_data`
# 6. Open the `Inspect`  tab
# 7. Identify the Mountpoint
# 8. Open in you file browser this folder and copy to here the ttl file 

#!pip uninstall neo4j_tools -y
#!pip install -U git+https://github.com/cebel/neo4j-tools.git
#!neo4j_tools set-neo-config -p neo4j_passwd
from neo4j_tools import Db, Node, Edge
db = Db()
db.delete_all_nodes()
#db.import_ttl("/data/hgnc.ttl", init_graph_config=True)
#db.import_ttl("/data/chebi.ttl", init_graph_config=False)
db.import_ttl("/data/disgenet.ttl", init_graph_config=False)
db.get_number_of_edges()
db.get_number_of_nodes()
