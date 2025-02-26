from taxoninsertion import Taxonomy

def test_gbif_abies():
    abies = Taxonomy(taxonname = 'Abies')
    assert hasattr(abies, 'neotoma')
    assert abies.neotoma['taxonname'] == 'Abies', "Adding a test string gets messed up somehow."
    abies.check_neotoma()
    assert abies.neotoma['taxonid'] == 1, "Did not check Neotoma properly for some reason."
    abies.check_gbif()
    assert hasattr(abies, 'external')
    assert len(abies.external) == 1, "Did not return the gbif object properly."
    abies.check_gbif()
    assert len(abies.external) == 1, "Did not return the gbif object properly when re-checking."