"""DisGeNet RDBMS model definition."""
from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String,insert,inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


def object_as_dict(obj, exclude: list = []) -> dict:
    """Convert a SQLAlchemy object's attributes to a dictionary.
    Args:
        obj: The SQLAlchemy object to be converted to a dictionary.
        exclude (list, optional): A list of attribute names to be excluded from the dictionary.
            Defaults to an empty list.
    Returns:
        dict: A dictionary representation of the object's attributes.
    """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs if c.key not in exclude}

#Add declarative base
Base = declarative_base()
''' source: e(BE:L):(https://github.com/e-bel)''' 
class DisgenetGene(Base):
    """Class definition for the disgeneåt_gene table."""

    __tablename__ = "disgenet_gene"
    id = Column(Integer, primary_key=True)

    gene_id = Column(Integer, ForeignKey("disgenet_gene_symbol.gene_id"))
    gene_symbol = relationship("DisgenetGeneSymbol", back_populates="gene_disease_pmid_associations")
    disease_id = Column(String(100), ForeignKey("disgenet_disease.disease_id"))
    disease = relationship("DisgenetDisease", foreign_keys=[disease_id])
    score = Column(Float)
    pmid = Column(BigInteger)
    source_id = Column(Integer, ForeignKey("disgenet_source.id"))
    source = relationship("DisgenetSource", foreign_keys=[source_id])

    def as_dict(self):
        """Convert object attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the object's attributes.
        """
        rs = object_as_dict(self, exclude=["id", "source_id"])
        rs.update(
            {
                "gene_symbol": self.gene_symbol.gene_symbol,
                "disease_name": self.disease.disease_name,
                "source": self.source.source,
            }
        )
        return rs


class DisgenetGeneSymbol(Base):
    """Class definition for the disgenet_gene_symbol table."""

    __tablename__ = "disgenet_gene_symbol"
    gene_id = Column(Integer, primary_key=True)
    gene_symbol = Column(String(50), index=True)

    gene_disease_pmid_associations = relationship("DisgenetGene", back_populates="gene_symbol")

    def as_dict(self):
        """Convert object attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the object's attributes.
        """
        return object_as_dict(self)


class DisgenetVariant(Base):
    """Class definition for the disgenet_variant table."""

    __tablename__ = "disgenet_variant"
    id = Column(Integer, primary_key=True)

    snp_id = Column(String(20), index=True)
    chromosome = Column(String(2))
    position = Column(BigInteger)
    disease_id = Column(String(100), ForeignKey("disgenet_disease.disease_id"))
    disease = relationship("DisgenetDisease", foreign_keys=[disease_id])
    score = Column(Float)
    pmid = Column(BigInteger, index=True)
    source_id = Column(Integer, ForeignKey("disgenet_source.id"))
    source = relationship("DisgenetSource", foreign_keys=[source_id])

    def as_dict(self):
        """Convert object attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the object's attributes.
        """
        rs = object_as_dict(self, exclude=["id", "source_id"])
        rs.update({"disease_name": self.disease.disease_name, "source": self.source.source})
        return rs


class DisgenetDisease(Base):
    """Class definition for the disgenet_disease table."""

    __tablename__ = "disgenet_disease"
    disease_id = Column(String(100), primary_key=True) 
    disease_name = Column(String(255), index=True)

    def as_dict(self):
        """Convert object attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the object's attributes.
        """
        return object_as_dict(self)


class DisgenetSource(Base):
    """Class definition for the disgenet_source table."""

    __tablename__ = "disgenet_source"
    id = Column(Integer, primary_key=True)
    source = Column(String(100), index=True)

    def as_dict(self):
        """Convert object attributes to a dictionary.

        Returns:
            dict: A dictionary representation of the object's attributes.
        """
        return object_as_dict(self, exclude=["id"])
