"""_Adding taxa to Neotoma (beetle data)_
by: Simon Goring
"""

from taxoninsertion import Taxonomy, tree_from_gbif
import csv

taxa = []

reader = csv.DictReader(open('validated_names.csv', 'r', encoding='UTF-8'))
for row in reader:
    taxa.append(row)

good_fam = {}

def find_clean(tax):
    """_This is a helper function to return the last valid "Neotoma" taxon._
    
    When we return a taxonomy from the `tree_from_gbif()` function we get the full tree.
    This function pares the tree down to the last leaf (without a taxonid) and the next higher ID.

    Args:
        tax (_Taxonomy_): _description_

    Returns:
        _Taxonomy_: _description_
    """
    if tax.children[0].neotoma['taxonid'] is None:
        return tax
    else:
        return find_clean(tax.children[0])

def check_good(name:str, good_list:object):
    if name in good_list.keys():
        return good_list[name]
    else:
        return None

# We loop through each taxon in the list.
# First, check if it's been added to the list using `check_good()`
# If the taxon is not in Neotoma, check to see if it is in GBIF.
# If we don't find a link in GBIF, then assign it a GBIF ID of -99999
# Otherwise, pull in the "tree" for the GBIF taxon, and work to append
# it into Neotoma.
for i in taxa:
    new_fam = Taxonomy(taxonname = i['FAMILY'].title())
    if check_good(i['FAMILY'].title(), good_fam) is None:
        print(f'--> Checking {i['FAMILY'].title()}.')
        try:
            new_fam.check_neotoma(dbname='neotomatank')
            if new_fam.neotoma['taxonid'] is None:
                print(f'---> {i['FAMILY'].title()} is not currently in Neotoma.')
                new_fam.check_gbif()
                if len(new_fam.external) == 0:
                    print(f'----> {i['FAMILY'].title()} is not currently in GBIF.')
                    i['familyid'] = -99999
                    good_fam[i['FAMILY'].title()] = -99999
                else:
                    print(f'----> {i['FAMILY'].title()} is in GBIF.')
                    new_tree = tree_from_gbif(new_fam, check_neotoma = True)
                    try:
                        clean_set = find_clean(new_tree)
                    except Exception:
                        print(f'-----> Could not generate a proper tree for {i['FAMILY'].title()} (synonomy?).')
                        i['familyid'] = -99999
                        good_fam[i['FAMILY'].title()] = -99999
                        continue
                    print(f'----> Generating metadata for {i['FAMILY'].title()}.')
                    clean_set.children[0].neotoma['highertaxonid'] = clean_set.neotoma['taxonid']
                    clean_set.children[0].neotoma['valid'] = True
                    clean_set.children[0].neotoma['validatorid'] = 202
                    clean_set.children[0].neotoma['taxoncode'] = clean_set.children[0].neotoma['taxonname'][:3] + 'dae'
                    clean_set.children[0].neotoma['extinct'] = False
                    clean_set.children[0].neotoma['notes'] = 'Bulk uploaded list from BUGS-SEP by Simon Goring'
                    clean_set.children[0].neotoma['taxagroupid'] = 'INS'
                    clean_set.children[0].post_neotoma(dbname = 'neotomatank')
                    print(f'---> Adding {i['FAMILY'].title()}.')
                    i['familyid'] = clean_set.children[0].neotoma['taxonid']
                    good_fam[i['FAMILY'].title()] = clean_set.children[0].neotoma['taxonid']
            else:
                print(f'---> {i['FAMILY'].title()} is already present in Neotoma.')
                good_fam[i['FAMILY'].title()] = new_fam.neotoma['taxonid']
                i['familyid'] = new_fam.neotoma['taxonid']
        except:
            good_fam[i['FAMILY'].title()] = -99998
    else:
        i['familyid'] = check_good(i['FAMILY'].title(), good_fam)

# Adds ~ 142 families.

good_genera = {}

# Now add the genera:
for i in taxa[0:50]:
    new_fam = Taxonomy(taxonname = i['FAMILY'].title())
    new_fam.add_node(Taxonomy(taxonname = i['GENUS'].title()))
    if i['familyid'] == -99999:
        # We already failed to match the family, just go to the next entry.
        i['genusid'] = -99999
        good_genera[i['GENUS'].title()] = -99999
        continue
    if check_good(i['GENUS'].title(), good_genera) is None:
        # We haven't run this genera yet:
        print(f'--> Checking {i['GENUS'].title()}.')
        try:
            new_fam.check_neotoma(dbname='neotomatank', check_all = True)
            new_fam.children[0].check_neotoma(dbname='neotomatank')
            if new_fam.children[0].neotoma['taxonid'] is None:
                print(f'---> {i['GENUS'].title()} is not currently in Neotoma.')
                new_fam.children[0].check_gbif(rank = 'genus', family = i['FAMILY'])
                if len(new_fam.children[0].external) == 0:
                    print(f'----> {i['GENUS'].title()} is not currently in GBIF.')
                    i['genusid'] = -99999
                    good_genera[i['GENUS'].title()] = -99999
                else:
                    print(f'----> {i['GENUS'].title()} is in GBIF.')
                    new_tree = tree_from_gbif(new_fam.children[0], check_neotoma = True)
                    try:
                        clean_set = find_clean(new_tree)
                    except Exception:
                        print(f'-----> Could not generate a proper tree for {i['GENUS'].title()} (synonomy?).')
                        i['genusid'] = -99999
                        good_genera[i['GENUS'].title()] = -99999
                        continue
                    print(f'----> Generating metadata for {i['GENUS'].title()}.')
                    clean_set.children[0].neotoma['highertaxonid'] = clean_set.neotoma['taxonid']
                    clean_set.children[0].neotoma['valid'] = True
                    clean_set.children[0].neotoma['validatorid'] = 202
                    clean_set.children[0].neotoma['taxoncode'] = clean_set.children[0].neotoma['taxonname'][:3]
                    clean_set.children[0].neotoma['extinct'] = False
                    clean_set.children[0].neotoma['notes'] = 'Bulk uploaded list from BUGS-CEP by Simon Goring'
                    clean_set.children[0].neotoma['taxagroupid'] = 'INS'
                    clean_set.children[0].post_neotoma(dbname = 'neotomatank')
                    print(f'---> Adding {i['GENUS'].title()}.')
                    i['genusid'] = clean_set.children[0].neotoma['taxonid']
                    good_genera[i['GENUS'].title()] = clean_set.children[0].neotoma['taxonid']
            else:
                print(f'---> {i['GENUS'].title()} is already present in Neotoma.')
                good_genera[i['GENUS'].title()] = new_fam.children[0].neotoma['taxonid']
                i['genusid'] = new_fam.children[0].neotoma['taxonid']
        except:
            good_genera[i['GENUS'].title()] = -99998
    else:
        i['genusid'] = check_good(i['GENUS'].title(), good_genera)


good_species = {}

# Now add the specific epithet:
for i in taxa[0:50]:
    new_fam = Taxonomy(taxonname = i['FAMILY'].title())
    new_fam.add_node(Taxonomy(taxonname = i['GENUS'].title()))
    new_fam.children[0].add_node(Taxonomy(taxonname = i['epithet']))
    if i['familyid'] == -99999:
        # We already failed to match the family, just go to the next entry.
        i['speciesid'] = -99999
        good_species[i['epithet']] = -99999
        continue
    if check_good(i['epithet'], good_species) is None:
        # We haven't run this genera yet:
        print(f'--> Checking {i['epithet']}.')
        try:
            new_fam.check_neotoma(dbname='neotomatank', check_all = True)
            if new_fam.children[0].children[0].neotoma['taxonid'] is None:
                print(f'---> {i['epithet']} is not currently in Neotoma.')
                new_fam.children[0].children[0].check_gbif(family = i['FAMILY'], genus = i['GENUS'], rank = 'SPECIES')
                if len(new_fam.children[0].children[0].external) == 0:
                    print(f'----> {i['epithet'].title()} is not currently in GBIF.')
                    i['taxonid'] = -99999
                    good_species[i['epithet']] = -99999
                else:
                    print(f'----> {i['epithet']} is in GBIF.')
                    new_tree = tree_from_gbif(new_fam.children[0].children[0])
                    ## TODO: There's some issue with tree_from_gbif and the check_neotoma flag.
                    new_tree.check_neotoma(dbname = 'neotomatank')
                    try:
                        clean_set = find_clean(new_tree)
                    except Exception:
                        print(f'-----> Could not generate a proper tree for {i['GENUS'].title()} (synonomy?).')
                        i['taxonid'] = -99999
                        good_species[i['epithet']] = -99999
                        continue
                    print(f'----> Generating metadata for {i['epithet']}.')
                    clean_set.children[0].neotoma['highertaxonid'] = clean_set.neotoma['taxonid']
                    clean_set.children[0].neotoma['valid'] = True
                    clean_set.children[0].neotoma['validatorid'] = 202
                    clean_set.children[0].neotoma['taxoncode'] = i['GENUS'][:3] + '.' + i['SPECIES'][:2]
                    clean_set.children[0].neotoma['extinct'] = False
                    clean_set.children[0].neotoma['notes'] = 'Bulk uploaded list from BUGS-CEP by Simon Goring'
                    clean_set.children[0].neotoma['taxagroupid'] = 'INS'
                    clean_set.children[0].post_neotoma(dbname = 'neotomatank')
                    print(f'---> Adding {i['epithet']}.')
                    i['taxonid'] = clean_set.children[0].neotoma['taxonid']
                    good_species[i['epithet']] = clean_set.children[0].neotoma['taxonid']
            else:
                print(f'---> {i['epithet']} is already present in Neotoma.')
                good_species[i['epithet']] = new_fam.children[0].neotoma['taxonid']
                i['taxonid'] = new_fam.children[0].children[0].neotoma['taxonid']
        except:
            good_genera[i['epithet']] = -99998
    else:
        i['taxonid'] = check_good(i['epithet'], good_species)


with open('validated_names.csv', 'w', newline='') as csvfile:
    fieldnames = taxa[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(taxa)
