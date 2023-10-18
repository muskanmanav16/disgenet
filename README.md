# disgenet_muskan
![Alt text](image.png)

## Description

The disgenet_muskan package is a versatile Python tool designed to seamlessly harness the rich resources of [DisGeNET](https://www.disgenet.org), one of the largest publicly available collections of genes and variants associated with human diseases. DisGeNET is a pioneering discovery platform that integrates data from expert-curated repositories, GWAS catalogues, animal models, and the scientific literature. It is homogeneously annotated with controlled vocabularies and community-driven ontologies, and provides original metrics for genotype-phenotype relationship prioritization.
## Installation

```python
pip install disgenet_muskan
```
You can also download the latest version from [PyPI website](https://test.pypi.org/project/disgenet-muskan/)

## Package Structure
This package consists of following files:
- [constant](src/disgenet_muskan/constants.py)
- [DBconnect](src/disgenet_muskan/DBconnect.py)
- [disgenet](src/disgenet_muskan/disgenet.py)
- [models](src/disgenet_muskan/models.py)
- [stdnames](src/disgenet_muskan/stdnames.py)
- [disgenet_rdf](src/disgenet_muskan/disgenet_rdf.py)
- [importer](src/disgenet_muskan/importer.py)

## Data Description

## Disgenet Model Description
![Alt text](image-1.png)
## Importing: Getting started

To make it easy for you to get started with disgenet_muskan package,  here's a list of recommended next steps:

1. Clone this repo into your system 
2. Create and activate a virtual environment
   - python3 -m venv .venv
   - source venv/bin/activate
3. Install the package in your virtual environment
   'python
     pip install . 
4. Open ipython/python from your terminal
5. run the cmds
     - from disgenet_muskan import disgenet
     - disgenet.populate_data()
6. To view the disgenet tables you can use php admin.

## Querying the Graph

## Usage


## Authors and acknowledgment
Author - Muskan Manav

Special Thanks to my instructor - [Christian Ebeling](christian.ebeling@scai.fraunhofer.de) for their constant support and guidance.
## Support
Please reach out via email at muskanmanav16@gmail.com for any questions


