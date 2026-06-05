from app.services.query_examples import QUERY_EXAMPLES
from app.services.travel_service import TravelService


class MainController:
    def __init__(self):
        self.service = TravelService()

    def query_examples(self):
        return QUERY_EXAMPLES

    def run_query(self, sql):
        return self.service.database.fetch_all(sql)
