[![NSF-2410965](https://img.shields.io/badge/NSF-2410965-blue.svg)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2410965&HistoricalAwards=false)
[![NSF-2410961](https://img.shields.io/badge/NSF-2410961-blue.svg)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2410961&HistoricalAwards=false)

[![DOI](https://zenodo.org/badge/939668660.svg)](https://doi.org/10.5281/zenodo.15485153)

# Taxon Insertion in Neotoma

This is a package intended to help support both bulk and individual taxon insertion in Neotoma.

What the package does:

1. Connects to the Neotoma Paleoecology Database (both main and tank).
2. Takes a taxon name and checks the name with GBIF and NCBI.
3. Finds the appropriate insertion point within Neotoma for insertion.
4. Returns a set of rows to be inserted into Neotoma to support the new taxonname.
5. Inserts new rows into Neotoma.
6. Supports rollback and commit features.

## Contributors

* [Simon Goring](http://goring.org): University of Wisconsin - Madison [![orcid](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605)

## Using this Repository

Secrets to connect to the database are in an "ignored" file named `.env`. It should have the format:

```bash
DBAUTH={"host":"localhost","port":5432,"user":"postgres","password":"postgres","dbname":"neotoma"}
```

The repository uses the `uv` package manager to help manage dependencies and ensure a stable development platform. To use this repository, first clone the repository locally, and then, run `uv init` to install all neccessary packages. Once the packages are installed, the script `testing_beetles.py` can be run using `uv run testing_beetles.py`.

The script may be slow to run because it must interact with the Neotoma database (and could interact with GBIF and NCBI if wanted).

## Current Expected Input and Output

The script in this repository is designed to work with a CSV file provided by the [BUGSCep](https://bugscep.com/) research data group. That CSV has the format:

```csv
CODE,FAMILY,GENUS,SPECIES,AUTHORITY,epithet,neotoma_path,gbifid,ncbi_id,taxonRank,taxonomicStatus,ncbi_lineage_names
```

The `testing_beetles.py` file parses this document row by row and returns a similar CSV, with the additional columns `familyid`, `genusid`, and `speciesid`, with the associated Neotoma taxon IDs.
