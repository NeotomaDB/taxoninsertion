from taxoninsertion import Taxonomy
import more_itertools

def test_new_taxonomy():
    new_tax = Taxonomy()
    assert hasattr(new_tax, 'neotoma')
    assert hasattr(new_tax, 'external')
    assert new_tax.neotoma['taxonid'] is None, "New elements are being added with information we don't want."
    new_tax = Taxonomy(taxonname = 'Alces alces')
    assert new_tax.neotoma['taxonname'] == 'Alces alces', "Adding a test string gets messed up somehow."

def test_add_node():
    new_tax = Taxonomy(taxonname = 'Abies')
    new_tax.add_node(Taxonomy(taxonname = 'Abies balsamea'))   
    assert len(new_tax.get_lower()) == 1, "The lower node was not added."

def test_list_names():
    names = ['a', 'b', 'c', 'd']
    parent = Taxonomy(taxonname = "top")
    for i in names:
        parent.add_node(Taxonomy(taxonname = i))
    result = parent.list_names()
    flat_result = more_itertools.collapse(result)
    assert all([i in names for i in flat_result if i != 'top']), "Some names were not returned."

def test_structured_taxon():
    new_sp = Taxonomy(taxonname = "Acer negundo")
    new_gen = Taxonomy(taxonname = "Acer")
    new_gen.add_node(new_sp)
    new_gen.check_neotoma(dbname='neotomatank', check_all = True)
    assert type(new_gen.list_neotoma()[1][0]) is dict, "Not getting the child node."
