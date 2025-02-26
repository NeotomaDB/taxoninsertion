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

* Simon Goring

