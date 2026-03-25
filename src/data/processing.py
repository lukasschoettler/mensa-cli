from typing import Dict, List, Tuple, TypedDict

from common.logger import log
from common.models import FetchRead, MealCreate, MenuCreate
from common.providers import SITES
from common.providers.types import MensaSite, ParseResult


class StructuredFetch(TypedDict):
    id: str
    html: str
    timestamp: str
    url: str
    mensa_key: str


def make_fetch_structured(fetch: Tuple[str, str, str, str, str]) -> StructuredFetch:

    structured_fetch: StructuredFetch = {
        "id": fetch[0],
        "html": fetch[1],
        "timestamp": fetch[2],
        "url": fetch[3],
        "mensa_key": fetch[4],
    }
    return structured_fetch


def parse_menu(sites: Dict[str, MensaSite], fetch: FetchRead) -> ParseResult:

    site = sites[fetch.mensa_key]
    parser = site.parser

    menu = parser(fetch.html)
    return menu


class MealProcessor:
    def __init__(self, sites=SITES):
        self.sites = sites

    def process(self, fetch: FetchRead) -> List[MealCreate]:
        meal_list = []
        menu = parse_menu(self.sites, fetch)
        for meal in menu.meals:
            meal_list.append(MealCreate(meal.name, fetch.mensa_key))
        return meal_list


class FetchProcessor:
    def __init__(
        self,
        fetches: List[FetchRead],
        sites=SITES,
        meal_processor: MealProcessor = MealProcessor(),
    ):
        self.sites = sites
        self.fetches = fetches
        self.meal_processor = meal_processor

    def process_one(
        self,
        fetch: FetchRead,
    ) -> Tuple[MenuCreate, List[MealCreate]]:
        log.debug(
            f"Processing fetch {fetch.id} from {fetch.timestamp} of {fetch.mensa_key}"
        )

        fetch_id = fetch.id
        mensa_key = fetch.mensa_key

        menu = MenuCreate(fetch_id, mensa_key)
        meal_list = self.meal_processor.process(fetch)

        return (menu, meal_list)

    def process_all(self) -> List[Tuple[MenuCreate, List[MealCreate]]]:
        fetches_processed: List[Tuple[MenuCreate, List[MealCreate]]] = []
        log.debug(
            f"Initializing processing for {fetches_processed.__len__()} unprocessed Fetches"
        )
        for fetch in self.fetches:
            fetch_processed = self.process_one(fetch)
            fetches_processed.append(fetch_processed)

        return fetches_processed
