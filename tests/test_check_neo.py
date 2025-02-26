from taxoninsertion import Taxonomy

def test_check_neo_with_abies():    
    abies = Taxonomy(taxonname = 'Abies')
    abies.check_neotoma()
    assert abies.neotoma['taxonid'] == 1

def text_check_neo_with_goodname():
    new_tax = Taxonomy(taxonname = 'Alces alces')
    assert new_tax.neotoma['taxonname'] == 'Alces alces', "Adding a test string gets messed up somehow."
    new_tax.check_neotoma()
    assert new_tax.neotoma['taxonid'] == 5826, "Did not fetch from Neotoma properly."

def text_check_neo_with_badname():
    new_tax = Taxonomy(taxonname = 'Alces alfresco')
    assert new_tax.neotoma['taxonname'] == 'Alces alfresco', "Adding a test string gets messed up somehow."
    new_tax.check_neotoma()
    assert new_tax.neotoma['taxonid'] is None, "Fetched something when it should have failed."

def text_check_neo_with_multparam():
    new_tax = Taxonomy(taxonname = 'Alces alces', taxonid = 5826)
    assert new_tax.neotoma['taxonname'] == 'Alces alces', "Adding a test string gets messed up somehow."
    new_tax.check_neotoma()
    assert new_tax.neotoma['valid'], "Did not fetch from Neotoma properly."
