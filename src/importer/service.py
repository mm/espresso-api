from logging import error
from . import BaseImporter, ImportStats
from typing import List, Optional
from src.model import LinkSchema, Link, db
from marshmallow import EXCLUDE

class JSONImporter(BaseImporter):

    def extract_links(self, path: str) -> List[Optional[dict]]:
        raise NotImplementedError


    def transform_links(self, links: List[dict], **kwargs) -> List[Link]:
        schema = LinkSchema(many=True)
        if 'user_id' in kwargs:
            # Pass along the user ID for the current request since we need that:
            links = [{**link, 'user_id': kwargs['user_id']} for link in links]
        result = schema.load(links, unknown=EXCLUDE)
        return result

    def load_links(self, links: List[Link]) -> ImportStats:
        success_counter = 0
        error_counter = 0
        for link in links:
            db.session.add(link)
            success_counter += 1
        try:
            db.session.commit()
        except Exception as e:
            # TODO: better handling
            print("Exception occured while importing")
            success_counter = 0
        return ImportStats(imported=success_counter, errors=error_counter)