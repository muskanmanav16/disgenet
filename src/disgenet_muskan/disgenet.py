from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from disgenet_muskan.constants import DATA_DIR,DISGENET,DISGENET_GDP_ASSOC,DISGENET_VDP_ASSOC
from disgenet_muskan.DBconnect import connection_string
from disgenet_muskan.models import DisgenetGene,DisgenetVariant,DisgenetSource,DisgenetDisease,DisgenetGeneSymbol
from disgenet_muskan.stdnames import standardize_column_names
from tqdm import tqdm
import pandas as pd
import os
import re


"""DisGeNet."""
class Disgenet:
    """DisGeNet (https://www.disgenet.org),
        e(BE:L):(https://github.com/e-bel)  
    """

    def __init__(self):
        """Init DisGeNet."""
        self.biodb_name = DISGENET
        self.urls = {
            "disgenet_gene": DISGENET_GDP_ASSOC,
            "disgenet_variant": DISGENET_VDP_ASSOC,
        }
        self.engine = create_engine(connection_string)
        self.session = Session(self.engine)

    def insert_data(self):
        """Insert data into the database.

        This method inserts various types of data (e.g., sources, gene symbols, disease names,
        gene-disease-PMID associations, variant-disease-PMID associations) into the database.

        Returns:
            dict: A dictionary containing the number of records inserted for each data type.
        """
        inserted = dict()

        with tqdm(total=5, desc="Inserting data into database") as pbar:
            inserted["sources"] = self._insert_sources()
            pbar.update(1)
            inserted["gene_symbols"] = self._insert_gene_symbols()
            pbar.update(1)
            inserted["gene_disease_names"] = self._insert_disease_names()
            pbar.update(1)
            inserted["gene_disease_pmid_associations"] = self._insert_gene_disease_pmid_associations()
            pbar.update(1)
            inserted["variant_disease_pmid_associations"] = self._insert_variant_disease_pmid_associations()
            pbar.update(1)
        return inserted
    def get_file_path(self,url: str, biodb: str):
        """Get standard file path by file_name and DATADIR."""
        file_name = os.path.basename(url)
        return os.path.join(DATA_DIR, file_name)


    def __get_file_for_model(self, model):
        """Return filepath of given model."""
        return self.get_file_path(self.urls[model.__tablename__], self.biodb_name)

    @property
    def file_path_gene(self):
        """Return filepath of gene."""
        return self.__get_file_for_model(DisgenetGene)

    @property
    def file_path_variant(self):
        """Return filepath of variant."""
        return self.__get_file_for_model(DisgenetVariant)
    
    def _insert_sources(self):
        """Insert sources into the database.

        Returns:
            int: The number of sources inserted into the database.
        """
        df_g = pd.read_csv(self.file_path_gene, sep="\t", usecols=["source"]).drop_duplicates()
        df_v = pd.read_csv(self.file_path_variant, sep="\t", usecols=["source"]).drop_duplicates()
        df = pd.concat([df_g, df_v]).drop_duplicates()
        df.reset_index(inplace=True, drop=True)
        df.index += 1
        df.index.rename("id", inplace=True)

        # Reset the index to avoid including it in the INSERT statement
        df.reset_index(drop=True, inplace=True)
        df.to_sql(DisgenetSource.__tablename__, self.engine, if_exists='append', index=False)
        return df.shape[0]

    def _insert_disease_names(self) -> int:
        """Insert gene symbols into the database.

        Returns:
            int: The number of gene symbols inserted into the database.
        """
        columns_disease = {"diseaseId": "disease_id", "diseaseName": "disease_name"}

        df_gene = (
            pd.read_csv(self.file_path_gene, sep="\t", usecols=list(columns_disease.keys()))
            .rename(columns=columns_disease)
            .drop_duplicates()
            .set_index("disease_id")
        )

        df_variant = (
            pd.read_csv(self.file_path_variant, sep="\t", usecols=list(columns_disease.keys()))
            .rename(columns=columns_disease)
            .drop_duplicates()
            .set_index("disease_id")
        )
        df_concat = pd.concat([df_gene, df_variant]).drop_duplicates()
        df_concat.to_sql(DisgenetDisease.__tablename__, self.engine, if_exists="append")
        return df_concat.shape[0]
   

    def _insert_gene_symbols(self) -> int:
        """Insert gene symbols into the database.

        Returns:
            int: The number of gene symbols inserted into the database.
        """
        columns_gene_symols = {"geneId": "gene_id", "geneSymbol": "gene_symbol"}
        df = (
            pd.read_csv(self.file_path_gene, sep="\t", usecols=list(columns_gene_symols.keys()))
            .rename(columns=columns_gene_symols)
            .drop_duplicates()
            .set_index("gene_id")
        )
        df.to_sql(DisgenetGeneSymbol.__tablename__, self.engine, if_exists='append')
        return df.shape[0]

    def _merge_with_source(self, df):
        """Merge the data with source information.

        Args:
            df (pd.DataFrame): The DataFrame to be merged with source information.

        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        df_sources = pd.read_sql_table(DisgenetSource.__tablename__, self.engine).rename(
            columns={"id": "source_id"}
        )
        return pd.merge(df, df_sources, on="source").drop(columns=["source"])
    

    def _insert_gene_disease_pmid_associations(self) -> int:
        """Insert gene-disease-PMID associations into the database.

        Returns:
            int: The number of associations inserted into the database.
        """
        usecols_gene = ["geneId", "diseaseId", "score", "pmid", "source"]
        rename_dict = dict(zip(usecols_gene, standardize_column_names(usecols_gene)))
        df = pd.read_csv(self.file_path_gene, sep="\t", usecols=usecols_gene).rename(columns=rename_dict)

        df = self._merge_with_source(df)
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(DisgenetGene.__tablename__, self.engine, if_exists="append")
        return df.shape[0]

    def _insert_variant_disease_pmid_associations(self) -> int:
        """Insert variant-disease-PMID associations into the database.

        Returns:
            int: The number of associations inserted into the database.
        """
        usecols_variant = ["snpId","chromosome","position","diseaseId","score","pmid","source"]
        rename_dict = dict(zip(usecols_variant, standardize_column_names(usecols_variant)))
        df = pd.read_csv(self.file_path_variant, sep="\t", usecols=usecols_variant).rename(columns=rename_dict)

        df = self._merge_with_source(df)
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(DisgenetVariant.__tablename__, self.engine, if_exists="append")
        return df.shape[0]







