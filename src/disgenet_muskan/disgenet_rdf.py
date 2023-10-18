from disgenet_muskan.DBconnect import engine
from rdflib import Graph, Namespace, RDF, Literal,URIRef
import pandas as pd

def makedataframe(engine=engine):
    """Create a DataFrame by querying a database using the specified engine.

    Args:
        engine (sqlalchemy.engine.base.Connection, optional): An SQLAlchemy engine to connect to the database.
            Defaults to the 'engine' from the imported module.

    Returns:
        tuple: A tuple containing two Pandas DataFrames:
            - The first DataFrame contains gene symbols, disease IDs, and disease names from the 'disgenet_gene' table.
            - The second DataFrame contains data from the 'disgenet_variant' table.
    """    
    query = """
        SELECT gs.gene_symbol,d.disease_id,d.disease_name
        FROM disgenet_gene g
        INNER JOIN disgenet_gene_symbol gs ON gs.gene_id = g.gene_id 
        INNER JOIN disgenet_disease d ON d.disease_id = g.disease_id 
        WHERE score >=0.5;
    """
    combined_df = pd.read_sql_query(query, con=engine)
    snp_query='''
            Select * from disgenet_variant
            WHERE score >=0.5;
            '''
    df_snp = pd.read_sql(snp_query, con=engine)
    return combined_df,df_snp

def create_ttl(ttl_file:str,engine=engine):
    """Create an RDF Turtle file from data in a database.

    This function queries the database using the provided engine to obtain gene-disease and SNP data.
    It then creates an RDF graph representing this data and serializes it to a Turtle file.

    Args:
        ttl_file (str): The path to the Turtle file where the RDF data will be saved.
        engine (sqlalchemy.engine.base.Connection, optional): An SQLAlchemy engine to connect to the database.
        Defaults to the 'engine' from the imported module.

    Returns:
        str: The serialized RDF data in Turtle format.
    """    
    combined_df,df_snps= makedataframe(engine)

    #Define Classes
    disease= URIRef(f"http://hgnc.com/#disease")
    snp = URIRef(f"http://hgnc.com/#snp")
    g=Graph()
    #Define properties
    conceptid = URIRef(f"http://hgnc.com/#disease_id") 
    diseasename = URIRef(f"http://hgnc.com/#disease_Name") 
    snpid_uri=URIRef(f"http://hgnc.com/#snp_id") 
    chromosome_uri=URIRef(f"http://hgnc.com/#chromosome")
    position_uri=URIRef(f"http://hgnc.com/#position")
    score_uri=URIRef(f"http://hgnc.com/#score")
    #Relations
    has_associated_with=URIRef(f"http://hgnc.com/#HasAssociatedWith") 
    #Add gene , disease nodes & properties in the graph
    for id, props in combined_df.iterrows():
        uri_ref_gene=URIRef(f'https://www.genenames.org/data/gene-symbol-report/#!/symbol/{props.gene_symbol}')
        uri_ref_disease= URIRef(f'https://www.ncbi.nlm.nih.gov/medgen/{props.disease_id}')
        g.add((uri_ref_disease,RDF.type,disease))
        g.add((uri_ref_disease,conceptid,Literal(props.disease_id)))
        g.add((uri_ref_disease,diseasename,Literal(props.disease_name)))
        g.add((uri_ref_gene,has_associated_with,uri_ref_disease))
    #Add Snp nodes & properties in the graph
    for id, props in df_snps.iterrows():
        uri_ref_snp= URIRef(f'http://identifiers.org/dbsnp/{props.snp_id}')
        g.add((uri_ref_snp,RDF.type,snp))
        g.add((uri_ref_snp,snpid_uri,Literal(props.snp_id)))
        g.add((uri_ref_snp,chromosome_uri,Literal(props.chromosome)))
        g.add((uri_ref_snp,position_uri,Literal(props.position)))
        g.add((uri_ref_snp,score_uri,Literal(props.score)))
        g.add((uri_ref_disease,has_associated_with,uri_ref_snp))
    return g.serialize(ttl_file, format="turtle")