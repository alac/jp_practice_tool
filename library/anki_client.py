from dataclasses import dataclass
from typing import List, Optional, Any, Dict
import json
import urllib.request


@dataclass
class AnkiField:
    value: str
    order: int


@dataclass
class CardInfo:
    cardId: int
    fields: dict[str, AnkiField]
    question: str
    answer: str
    modelName: str
    ord: int
    deckName: str
    css: str
    factor: int
    interval: int
    note: int
    type: int
    queue: int
    due: int
    reps: int
    lapses: int
    left: int
    mod: int
    nextReviews: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> 'CardInfo':
        fields_dict = {
            field_name: AnkiField(
                value=field_data['value'],
                order=field_data['order']
            )
            for field_name, field_data in data['fields'].items()
        }

        return cls(
            cardId=data['cardId'],
            fields=fields_dict,
            question=data['question'],
            answer=data['answer'],
            modelName=data['modelName'],
            ord=data['ord'],
            deckName=data['deckName'],
            css=data['css'],
            factor=data['factor'],
            interval=data['interval'],
            note=data['note'],
            type=data['type'],
            queue=data['queue'],
            due=data['due'],
            reps=data['reps'],
            lapses=data['lapses'],
            left=data['left'],
            mod=data['mod'],
            nextReviews=data['nextReviews']
        )

    @property
    def first_field(self) -> str:
        return self.get_field_at_index(0)

    def get_field_at_index(self, index) -> str:
        for field in self.fields:
            anki_field = self.fields[field]
            if anki_field.order == index:
                return anki_field.value
        return ""

    def get_field_with_name(self, name) -> str:
        if name in self.fields:
            return self.fields[name].value
        return ""


class AnkiConnectClient:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.endpoint = f"http://{host}:{port}"

    def _invoke(self, action: str, **params) -> Any:
        """Send a request to AnkiConnect."""
        request = json.dumps({
            "action": action,
            "version": 6,
            "params": params
        }).encode('utf-8')

        try:
            response = urllib.request.urlopen(urllib.request.Request(
                self.endpoint,
                request,
                headers={'Content-Type': 'application/json'}
            ))
            response_data = json.loads(response.read().decode('utf-8'))

            if len(response_data) != 2:
                raise Exception('Response has an unexpected number of fields')

            if 'error' not in response_data:
                raise Exception('Response is missing required error field')

            if 'result' not in response_data:
                raise Exception('Response is missing required result field')

            if response_data['error'] is not None:
                raise Exception(response_data['error'])

            return response_data['result']

        except Exception as e:
            raise Exception(f'Failed to connect to AnkiConnect: {str(e)}')

    def get_failed_cards(self, days: int, limit: int, deck_name: Optional[str] = None) -> List[CardInfo]:
        """Get cards that were failed in the last X days."""
        query = f"rated:{days}:1"
        if deck_name:
            query = f"deck:\"{deck_name}\" {query}"

        card_ids = self._invoke(
            "findCards",
            query=query
        )

        card_ids = card_ids[-limit:]  # Take the most recent ones

        cards_info = self._invoke(
            "cardsInfo",
            cards=card_ids
        )

        return [CardInfo.from_dict(info) for info in cards_info]

    def get_difficult_cards(
            self,
            limit: int,
            deck_name: Optional[str] = None,
            reps: int = 30,
            ease: float = 1.4,
    ) -> List[CardInfo]:
        """Get cards with low ease factor (indicating difficulty)."""
        reps = max(reps, 0)
        query = f"prop:reps>{reps} prop:due>0 prop:ease<{ease}"
        if deck_name:
            query = f"deck:\"{deck_name}\" {query}"

        card_ids = self._invoke(
            "findCards",
            query=query
        )

        card_ids = card_ids[:limit]
        cards_info = self._invoke(
            "cardsInfo",
            cards=card_ids
        )

        return [CardInfo.from_dict(info) for info in cards_info]

    def get_exact_matches_cards(
            self,
            search: str,
            limit: int,
            deck_name: Optional[str] = None,
    ) -> List[CardInfo]:
        query = f"*:\"{search}\""
        if deck_name:
            query = f"deck:\"{deck_name}\" {query}"

        card_ids = self._invoke(
            "findCards",
            query=query
        )

        card_ids = card_ids[:limit]
        cards_info = self._invoke(
            "cardsInfo",
            cards=card_ids
        )

        return [CardInfo.from_dict(info) for info in cards_info]

    def open_card_browser(self, note_id: int) -> None:
        """Open the card browser focused on a specific card."""
        self._invoke(
            "guiBrowse",
            query=f"nid:{note_id}"
        )


if __name__ == "__main__":
    anki = AnkiConnectClient()
    # fetched_cards = anki.get_failed_cards(days=7, limit=10)
    fetched_cards = anki.get_difficult_cards(limit=10, deck_name="Japanese Vocabulary")

    for card in fetched_cards:
        print(card.first_field)
        anki.open_card_browser(card.note)
        break
        # print(f"Due in: {card.nextReviews[0]}")
        # print(f"Number of lapses: {card.lapses}")
