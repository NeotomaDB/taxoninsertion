from taxoninsertion import Taxonomy, tree_from_gbif
import more_itertools

def test_gbif_abies():
    abies = Taxonomy(taxonname = 'Abies')
    abies.check_neotoma()
    abies.check_gbif()
    clean_tree = tree_from_gbif(abies, check_neotoma = True)
    assert type(clean_tree) is Taxonomy
    all_names = clean_tree.list_names()
    flat_result = more_itertools.collapse(all_names)
    assert any([i == 'Abies' for i in flat_result]), "We've lost the original name."
