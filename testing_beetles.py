"""_Adding taxa to Neotoma (beetle data)_
by: Simon Goring
"""

from taxoninsertion import Taxonomy, tree_from_gbif
import csv
import sys

taxa = []
run_taxa = []

reader = csv.DictReader(open('data/ncbi_join.csv', 'r', encoding='UTF-8'))
for row in reader:
    taxa.append(row)

reader = csv.DictReader(open('validated_names_tank.csv', 'r', encoding='UTF-8'))
for row in reader:
    run_taxa.append(row)

# Sanity check on the number of rows in each:
assert len(taxa) == len(run_taxa)

def assign_metadata(tax: Taxonomy, level:str) -> Taxonomy:
    """_A quick function to assign new metadata to the child taxon element_

    Args:
        tax (Taxonomy): _A valid taxonomy element with a child._

    Returns:
        Taxonomy: _The Taxonomy with the cleaned up child element._
    """    
    # TODO: WRITE NAME CODE PROPERLY BASED ON THE LEVEL
    if level == 'FAMILY':
        code = tax.children[0].neotoma['taxonname'][:3] + 'dae'
    if level == 'GENUS':
        code = tax.children[0].neotoma['taxonname'][:3]
    if level == 'epithet':
        namesplit = tax.children[0].neotoma['taxonname'].split(' ')
        code = tax.children[0].neotoma['taxonname'][:3] + '.' + namesplit[1][:2]
    tax.children[0].neotoma['highertaxonid'] = tax.neotoma['taxonid']
    tax.children[0].neotoma['valid'] = True
    tax.children[0].neotoma['validatorid'] = 202
    tax.children[0].neotoma['taxoncode'] = code
    tax.children[0].neotoma['extinct'] = False
    tax.children[0].neotoma['notes'] = 'Bulk uploaded list from BUGS-SEP by Simon Goring'
    if tax.neotoma['taxagroupid']:
        tax.children[0].neotoma['taxagroupid'] = tax.neotoma['taxagroupid']
    else:
        tax.children[0].neotoma['taxagroupid'] = 'INS'
    return tax


def find_clean(tax):
    """_This is a helper function to return the last valid "Neotoma" taxon._
    
    When we return a taxonomy from the `tree_from_gbif()` function we get the full tree.
    This function pares the tree down to the last leaf (without a taxonid) and the next higher ID.

    Args:
        tax (_Taxonomy_): _description_

    Returns:
        _Taxonomy_: _description_
    """
    if len(tax.children) > 0:
        if tax.children[0].neotoma['taxonid'] is None:
            return tax
        else:
            return find_clean(tax.children[0])
    else:
        return tax

def check_good(name:str, level:str, good_list:object):
    """_Is the name and phylogenetic level in the "good_set" of records._
    The set of records are structured as a list:
    'TAXONNAME': {'FAMILY': 12324, 'GENUS': 12345}

    Args:
        name (str): _The taxon name._
        level (str): _The taxonomic level._
        good_list (object): _The dict list._

    Returns:
        _type_: _description_
    """    
    if name in good_list.keys():
        if good_list[name][level]:
            return good_list[name][level]
    return None

def clean_from_gbif(taxon:Taxonomy)->dict:
    """_Check the GBIF backbone, and generate a taxonomy and message._

    Args:
        taxon (Taxonomy): _A Neotoma Taxonomy object._

    Returns:
        dict: _A dict with keys 'taxonomy' and 'message'_
    """    
    result = {'message': None, 'taxonomy': None}
    taxon.check_gbif()
    if len(taxon.external) == 0:
        result['message'] = 'No record in GBIF'
        result['taxonomy'] = None
    else:
        print(f'----> {taxon.neotoma['taxonname']} is in GBIF.')
        new_tree = tree_from_gbif(taxon, check_neotoma = True)
        try:
            result['taxonomy'] = find_clean(new_tree)
        except Exception:
            print(f'-----> Could not generate a proper tree for {i['FAMILY']} (synonomy?).')
            result['message'] = 'GBIF found record, but possibly synonomy.'
    return result

# We loop through each taxon in the list.
# First, check if it's been added to the list using `check_good()`
# If the taxon is not in Neotoma, check to see if it is in GBIF.
# If we don't find a link in GBIF, then assign it a GBIF ID of -99999
# Otherwise, pull in the "tree" for the GBIF taxon, and work to append
# it into Neotoma.

names = {'FAMILY': 'familyid', 'GENUS': 'genusid', 'epithet': 'taxonid'}

good_set = []

sp_end = r'.*((sp)*(spp)*(indet)*)+\.$'

for i in taxa:
    i['familyid'] = None
    i['genusid'] = None
    i['speciesid'] = None
    i['FAMILY'] = i['FAMILY'].title()
    i['GENUS'] = i['GENUS'].title()

for index, i in enumerate(taxa):
    print('.', end = '')
    sys.stdout.flush()
    if run_taxa[index]['familyid'] == '':
        try:
            # Get the familyid if the taxon is already in the database.
            taxonid = [j['familyid'] for j in taxa if j['FAMILY'] == i['FAMILY'] and i['familyid'] is not None]
            if len(taxonid) > 0:
                i['familyid'] = taxonid[0]
            new_fam = Taxonomy(taxonname = i['FAMILY'], taxonid = i['familyid'])
            new_fam.check_neotoma(dbname='neotoma')
            # If the taxon is not in Neotoma:
            if new_fam.neotoma['taxonid'] is None:
                print(f"\nNo entries for family: {i['FAMILY']}")
                continue
            else:
                if i['GENUS'] == i['FAMILY']:
                    # These are high level links between the family and the epithet.
                    new_fam.add_node(Taxonomy(taxonname=i['epithet']))
                    new_fam = assign_metadata(new_fam, 'epithet')
                    new_fam.check_neotoma(check_all = True, dbname = 'neotoma')
                    if new_fam.children[0].neotoma['taxonid'] is None:
                        new_fam.children[0].post_neotoma(dbname='neotoma')
                    i['familyid'] = new_fam.neotoma['taxonid']
                    i['speciesid'] = new_fam.children[0].neotoma['taxonid']
                else:
                    # We have both genus and species to manage.
                    taxonid = [j['genusid'] for j in taxa if j['GENUS'] == i['GENUS'] and i['genusid'] is not None]
                    if len(taxonid) > 0:
                        i['genusid'] = taxonid[0]
                    new_fam.add_node(Taxonomy(taxonname=i['GENUS'], taxonid = i['genusid']))
                    new_fam = assign_metadata(new_fam, 'GENUS')
                    new_fam.check_neotoma(check_all = True, dbname = 'neotoma')
                    if new_fam.children[0].neotoma['taxonid'] is None:
                        new_fam.children[0].post_neotoma(dbname='neotoma')
                    new_fam.children[0].add_node(Taxonomy(taxonname=i['epithet']))
                    new_fam.children[0] = assign_metadata(new_fam.children[0], 'epithet')
                    new_fam.check_neotoma(check_all = True)
                    if new_fam.children[0].children[0].neotoma['taxonid'] is None:
                        new_fam.children[0].children[0].post_neotoma(dbname='neotoma')
                    i['familyid'] = new_fam.neotoma['taxonid']
                    i['genusid'] = new_fam.children[0].neotoma['taxonid']
                    i['speciesid'] = new_fam.children[0].children[0].neotoma['taxonid']
        except Exception as e:
            print('\n')
            print(e)
    else:
        taxa[index] = run_taxa[index]

with open('validated_names_tank.csv', 'w', newline='') as csvfile:
    fieldnames = taxa[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(taxa)
