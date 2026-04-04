from typing import List, Tuple, TypedDict

from common.logger import log
from common.models import FetchRead, MealCreate, MenuCreate
from common.providers import MENSAS
from common.providers.types import MensaRegistry, ParseResult


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


def parse_menu(sites: MensaRegistry, fetch: FetchRead) -> ParseResult:
    site = sites[fetch.mensa_key]
    parser = site.parser
    menu = parser(fetch.html)
    return menu


class MealProcessor:
    def __init__(self, sites: MensaRegistry | None = None):
        self.sites = sites if sites is not None else MENSAS

    def process(self, fetch: FetchRead) -> List[MealCreate]:
        meal_list = []
        menu = parse_menu(self.sites, fetch)
        for meal in menu.meals:
            meal_list.append(
                MealCreate(
                    meal.name,
                    fetch.mensa_key,
                    meal.pricing.student,
                    meal.pricing.employee,
                    meal.pricing.guest,
                )
            )
        return meal_list


class FetchProcessor:
    def __init__(
        self,
        fetches: List[FetchRead],
        sites: MensaRegistry | None = None,
        meal_processor: MealProcessor | None = None,
    ):
        self.sites = sites if sites is not None else MENSAS
        self.fetches = fetches
        self.meal_processor = (
            meal_processor if meal_processor is not None else MealProcessor()
        )

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
