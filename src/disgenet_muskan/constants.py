#File for defining the contastant and urls for downloading the database
import os

#Defining the constants 
DISGENET = "disgenet"
DISGENET_BASE = "https://www.disgenet.org/static/disgenet_ap1/files/downloads/" #url from disgenet
DISGENET_GDP_FILE = "all_gene_disease_pmid_associations.tsv.gz"
DISGENET_VDP_FILE = "all_variant_disease_pmid_associations.tsv.gz"
DISGENET_GDP_ASSOC = DISGENET_BASE + DISGENET_GDP_FILE
DISGENET_VDP_ASSOC = DISGENET_BASE + DISGENET_VDP_FILE
current_dir = os.getcwd()
DATA_DIR = os.path.join(current_dir, 'data')
os.makedirs(DATA_DIR, exist_ok=True)



