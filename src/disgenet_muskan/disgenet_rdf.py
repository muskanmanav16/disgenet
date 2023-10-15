from disgenet_muskan.DBconnect import engine
from rdflib import Graph, Namespace, RDF, Literal,URIRef
from sqlalchemy import create_engine, MetaData, Table, select,inspect
import pandas as pd
#connect to the database
inspector = inspect(engine)

# Get a list of all table names in the database
#table_names = inspector.get_table_names()
# Define the SQL query to join the tables
def makedataframe(engine=engine):
    """_summary_

    Args:
        engine (_type_, optional): _description_. Defaults to engine.
    """    
    query = """
        SELECT gs.gene_symbol,d.disease_id,d.disease_name
        FROM disgenet_gene g
        INNER JOIN disgenet_gene_symbol gs ON gs.gene_id = g.gene_id 
        INNER JOIN disgenet_disease d ON d.disease_id = g.disease_id 
        WHERE score >=0.5;
    """
    combined_df = pd.read_sql_query(query, con=engine)
    snps_query='''
            Select * from disgenet_variant
            WHERE score >=0.5;
            '''
    df_snps = pd.read_sql(snps_query, con=engine)
    return combined_df,df_snps

def create_ttl(ttl_file:str,engine=engine):
    """_summary_

    Args:
        ttl_file (str): _description_
        engine (_type_, optional): _description_. Defaults to engine.

    Returns:
        _type_: _description_
    """    
    combined_df,df_snps= makedataframe(engine)

    #Define Classes
    disease= URIRef(f"http://hgnc.com/#disease")
    snp = URIRef(f"http://hgnc.com/#snp")
    g=Graph()
    #define properties
    conceptid = URIRef(f"http://hgnc.com/#disease_id") 
    diseasename = URIRef(f"http://hgnc.com/#disease_Name") 
    snpid_uri=URIRef(f"http://hgnc.com/#snp_id") 
    chromosome_uri=URIRef(f"http://hgnc.com/#chromosome")
    position_uri=URIRef(f"http://hgnc.com/#position")
    score_uri=URIRef(f"http://hgnc.com/#score")
    #relation
    has_associated_with=URIRef(f"http://hgnc.com/#HasAssociatedWith") 
    #Add gene and disease nodes & properties
    for id, props in combined_df.iterrows():
        uri_ref_gene=URIRef(f'https://www.genenames.org/data/gene-symbol-report/#!/symbol/{props.gene_symbol}')
        uri_ref_disease= URIRef(f'https://www.ncbi.nlm.nih.gov/medgen/{props.disease_id}')
        g.add((uri_ref_disease,RDF.type,disease))
        g.add((uri_ref_disease,conceptid,Literal(props.disease_id)))
        g.add((uri_ref_disease,diseasename,Literal(props.disease_name)))
        g.add((uri_ref_gene,has_associated_with,uri_ref_disease))
    #Add Snp nodes & properties
    for id, props in df_snps.iterrows():
        uri_ref_snp= URIRef(f'http://identifiers.org/dbsnp/{props.snp_id}')
        g.add((uri_ref_snp,RDF.type,snp))
        g.add((uri_ref_snp,snpid_uri,Literal(props.snp_id)))
        g.add((uri_ref_snp,chromosome_uri,Literal(props.chromosome)))
        g.add((uri_ref_snp,position_uri,Literal(props.position)))
        g.add((uri_ref_snp,score_uri,Literal(props.score)))
        g.add((uri_ref_disease,has_associated_with,uri_ref_snp))
    return g.serialize(ttl_file, format="turtle")