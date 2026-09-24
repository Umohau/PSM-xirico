from Projeto_xirico.use_cases.catalog_use_cases.add_bird_to_catalog import AddBirdToCatolog
from Projeto_xirico.use_cases.catalog_use_cases.recovery_bird_in_catalog import RecoveryBirdInCtalog
from Projeto_xirico.use_cases.catalog_use_cases.remove_bird_in_catalog_by_id import RemoveBirdsInCatalogById
from Projeto_xirico.use_cases.catalog_use_cases.search_birds import SearchBirdById, SearchBirdByName
from Projeto_xirico.use_cases.catalog_use_cases.show_catalog import ShowCatalog
from Projeto_xirico.use_cases.catalog_use_cases.update_bird_name_in_catalog import UpdateBirdNameInCatalogById
from Projeto_xirico.use_cases.catalog_use_cases.update_cientific_bird_name_in_catalog import UpdateBirdCientificNameInCatalog


class CatalogApp:
    def __init__(
        self,
        birds_repo,
        audit,
        profile):

        self.add_bird= AddBirdToCatolog(
            repo= birds_repo,
            profile= profile,
            audit= audit
        )


        self.remove_bird_in_catalog_by_id= RemoveBirdsInCatalogById(
            repo= birds_repo,
            profile= profile,
            audit= audit
        )


        self.recovery_bird= RecoveryBirdInCtalog(
            repo= birds_repo,
            profile= profile,
            audit= audit
        )


        self.update_bird_cientific_name= UpdateBirdCientificNameInCatalog(
            repo= birds_repo,
            profile= profile,
            audit= audit
        )


        self.update_bird_name_by_id= UpdateBirdNameInCatalogById(
            repo= birds_repo,
            profile= profile,
            audit= audit
        )


        self.show_catalog= ShowCatalog(
            repo= ShowCatalog
        )


        self.search_bird_by_id= SearchBirdById(
            repo= birds_repo
        )


        self.search_bird_by_name= SearchBirdByName(
            repo= birds_repo
        )
