from sqlalchemy import create_engine,inspect
from sqlalchemy.orm import Session
from disgenet_muskan.constants import DATA_DIR,engine,DISGENET,DISGENET_GDP_ASSOC,DISGENET_VDP_ASSOC,connection_string,download_file
from disgenet_muskan.models import DisgenetGene,DisgenetVariant,DisgenetSource,DisgenetDisease,DisgenetGeneSymbol,Base
from tqdm import tqdm
import pandas as pd
import os
import re

"""DisGeNet."""
class Disgenet:
    """DisGeNet (https://www.disgenet.org)."""

    def __init__(self):
        """Init DisGeNet."""
        #self.client = client
        self.biodb_name = DISGENET
        self.urls = {
            "disgenet_gene": DISGENET_GDP_ASSOC,
            "disgenet_variant": DISGENET_VDP_ASSOC,
        }
        self.engine = create_engine(connection_string)
        #self.engine = create_engine(connection_string_with_db)
        self.session = Session(self.engine)

    def insert_data(self):
        """Insert data into database."""
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


    def get_standard_name(self,name: str) -> str:
        """Return standard name."""
        part_of_name = [x for x in re.findall("[A-Z]*[a-z0-9]*", name) if x]
        new_name = "_".join(part_of_name).lower()
        if re.search(r"^\d+", new_name):
            new_name = "_" + new_name
        return new_name


    def standardize_column_names(self,columns) :
            """Standardize column names.

            Parameters
            ----------
            columns: Iterable[str]
                Iterable of columns names.
            """
            return [self.get_standard_name(x) for x in columns]
    def __get_file_for_model(self, model):
        """Return filepath of given model."""
        #print(get_file_path(self.urls[model.__tablename__], self.biodb_name))
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
        df_sources = pd.read_sql_table(DisgenetSource.__tablename__, self.engine).rename(
            columns={"id": "source_id"}
        )
        return pd.merge(df, df_sources, on="source").drop(columns=["source"])
    

    def _insert_gene_disease_pmid_associations(self) -> int:
        usecols_gene = ["geneId", "diseaseId", "score", "pmid", "source"]
        rename_dict = dict(zip(usecols_gene, self.standardize_column_names(usecols_gene)))
        df = pd.read_csv(self.file_path_gene, sep="\t", usecols=usecols_gene).rename(columns=rename_dict)

        df = self._merge_with_source(df)
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(DisgenetGene.__tablename__, self.engine, if_exists="append")
        return df.shape[0]

    def _insert_variant_disease_pmid_associations(self) -> int:
        usecols_variant = [
            "snpId",
            "chromosome",
            "position",
            "diseaseId",
            "score",
            "pmid",
            "source",
        ]
        rename_dict = dict(zip(usecols_variant, self.standardize_column_names(usecols_variant)))
        df = pd.read_csv(self.file_path_variant, sep="\t", usecols=usecols_variant).rename(columns=rename_dict)

        df = self._merge_with_source(df)
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(DisgenetVariant.__tablename__, self.engine, if_exists="append")
        return df.shape[0]

def populate_data():
    '''defining class instance and calling class method''' 
    download_file(DISGENET_GDP_ASSOC, os.path.join(DATA_DIR, 'all_gene_disease_pmid_associations.tsv.gz'))
    download_file(DISGENET_VDP_ASSOC, os.path.join(DATA_DIR, 'all_variant_disease_pmid_associations.tsv.gz'))                                 
    d = Disgenet()
    Base.metadata.drop_all(engine)       # drop if already exists
    Base.metadata.create_all(engine)     # re create incase it already exists, to avoid duplicates   
    d.insert_data()
    d.session.close()

if __name__ == "__main__":
    populate_data()




