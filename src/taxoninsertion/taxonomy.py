from .neo_connect import neo_connect
from psycopg import sql
from dotenv import load_dotenv
from json import loads, dumps
from os import getenv
from pygbif import species

class Taxonomy:
    def __init__(self, taxonid:int = None, taxonname:str = None, author:str = None, 
                       valid: bool = None, highertaxonid:int = None,
                       extinct: bool = None, taxagroupid:str = None,
                       publicationid:int = None, taxoncode:str = None,
                       validatorid: int = None, validatedate: str = None,
                       notes:str = None):
        self.neotoma = {'taxonid': taxonid,
                        'taxonname': taxonname,
                        'taxoncode': taxoncode,
                        'author': author,
                        'valid': valid,
                        'highertaxonid': highertaxonid,
                        'taxagroupid': taxagroupid,
                        'extinct': extinct,
                        'publicationid': publicationid,
                        'validatorid': validatorid,
                        'validatedate': validatedate,
                        'notes':notes}  
        self.external = []
        self.children = []
    def __repr__(self):
        pass
    def post_neotoma(self, dbname:str = 'neotoma'):
        load_dotenv()
        CONN_STRING = loads(getenv("DBAUTH"))
        CONN_STRING['dbname'] = dbname
        con = neo_connect(CONN_STRING)
        query = """
            SELECT ts.inserttaxon(_code := %(taxoncode)s, _name := %(taxonname)s, _valid := %(valid)s,
               _higherid := %(highertaxonid)s, _extinct := %(extinct)s, _groupid := %(taxagroupid)s,
               _validatorid := %(validatorid)s, _notes := %(notes)s)"""
        with con.cursor() as cur:
            cur.execute(query, self.neotoma)
            resultset = cur.fetchone()
            self.neotoma['taxonid'] = resultset[0]
        con.commit()
        con.close()
    def get_lower(self):
        return self.children
    def add_node(self, taxon):
        assert type(taxon) is Taxonomy, "You must pass a Taxonomy object."
        taxon.neotoma['highertaxonid'] = self.neotoma['taxonid']
        self.children.append(taxon)
    def check_neotoma(self, dbname:str = 'neotoma', check_all:bool = True):
        assert any([i is None for i in self.neotoma.values()]) is not None, "All keys are None, assign values first."
        load_dotenv()
        CONN_STRING = loads(getenv("DBAUTH"))
        CONN_STRING['dbname'] = dbname
        con = neo_connect(CONN_STRING)
        query = """
            SELECT * FROM ndb.taxa
            WHERE {conditions} = %s
            """
        fields = [i for i in self.neotoma if self.neotoma[i] is not None]
        values = [i for i in self.neotoma.values() if i is not None]
        composed = sql.SQL(query).format(
            conditions = sql.SQL('=%s AND ').join(
                [sql.Identifier(i) for i in fields])
            )
        with con.cursor() as cur:
            cur.execute(composed, values)
            resultset = cur.fetchall()
            if len(resultset) == 1:
                columns =  [desc[0] for desc in cur.description]
                for i in columns:
                    self.neotoma[i] = resultset[0][columns.index(i)]
            elif len(resultset) > 1:
                con.close()
                raise ValueError(f'Error trying to match {self.neotoma['taxonname']}: appears multiple times in the database.')
        con.close()
        if check_all:
            for i in self.children:
                i.neotoma['highertaxonid'] = self.neotoma['taxonid']
                i.check_neotoma(dbname, check_all)
    def update_neotoma(self, commit:bool = False):
        assert self.neotoma['taxonid'] is not None, "To update a taxon in Neotoma you must have an existing taxonid."
    def check_gbif(self, rank = None, family = None, kingdom = None, genus = None):
        # We generate a hash to make sure things are stable/similar if we do a check.
        old_gbif = [hash(dumps(i['data'], sort_keys=True)) for i in self.external if i['source'] == 'gbif']
        name_check = species.name_backbone(name=self.neotoma['taxonname'], rank = rank, family = family, kingdom = kingdom, genus = genus)
        if 'canonicalName' in name_check.keys():
            if name_check['canonicalName'] != self.neotoma['taxonname']:
                print('GBIF indicates a synonymy for this taxon.')
                return None
            if len(old_gbif) == 1:
                if old_gbif[0] == hash(dumps(name_check, sort_keys=True)):
                    print("No update the the GBIF backbone since the last validation.")
                    return None
            if name_check['matchType']:
                new_obj = {'source': 'gbif',
                        'url': 'https://api.gbif.org/species',
                        'id': name_check['usageKey'],
                        'data': name_check}
                self.external.append(new_obj)
    def list_names(self):
        nodes = [self.neotoma['taxonname']]
        for i in self.children:
            nodes.append(i.list_names())
        return nodes
    def list_neotoma(self):
        nodes = [self.neotoma]
        for i in self.children:
            nodes.append(i.list_neotoma())
        return nodes

def tree_from_gbif(tax_to_parse, check_neotoma:bool = False):
    """_Generate a Taxonomy tree for the entire tree object._

    Args:
        tax_to_parse (_Taxonomy_): _A valid Taxonomy object from the taxoninsertion package._
        check_neotoma (bool, optional): _Should we validate the taxa against Neotoma?_. Defaults to False.

    Returns:
        _type_: _description_
    """    
    assert type(tax_to_parse) is Taxonomy, "You must pass a taxonomy."
    assert any(['gbif' in i['source'] for i in tax_to_parse.external]), "You must have a GBIF reference in your Taxonomy object."
    levels = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'subgenus', 'species']
    gbif_taxonomy = [i for i in tax_to_parse.external if i['source'] == 'gbif'][0]['data']
    new_obj = None
    for i in reversed([i for i in levels if i in gbif_taxonomy.keys()]):
        if new_obj is None and gbif_taxonomy[i] is not None:
            new_obj = Taxonomy(taxonname = gbif_taxonomy[i])
        elif type(new_obj) is Taxonomy and gbif_taxonomy[i] is not None:
            new_tax = Taxonomy(taxonname = gbif_taxonomy[i])
            new_tax.add_node(new_obj)
            new_obj = new_tax
    if check_neotoma:
        new_obj.check_neotoma(check_all = True)
    return new_obj
