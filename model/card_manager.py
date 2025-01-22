from dataclasses import dataclass, asdict
from typing import List, Dict
import json
from pathlib import Path

from library.anki_client import CardInfo, AnkiField


@dataclass
class CardManager:
    current_cards: List[CardInfo]
    history: List[CardInfo]
    save_path: Path

    @classmethod
    def load_from_file(cls, save_path: Path) -> 'CardManager':
        if not save_path.exists():
            return cls([], [], save_path)

        with save_path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        def dict_to_cardinfo(card_dict: Dict) -> CardInfo:
            fields = {
                k: AnkiField(**v) if isinstance(v, dict) else v
                for k, v in card_dict['fields'].items()
            }
            card_dict['fields'] = fields
            return CardInfo(**card_dict)

        current_cards = [dict_to_cardinfo(card) for card in data.get('current_cards', [])]
        history = [dict_to_cardinfo(card) for card in data.get('history', [])]

        return cls(current_cards, history, save_path)

    def _save_to_file(self) -> None:
        data = {
            'current_cards': [asdict(card) for card in self.current_cards],
            'history': [asdict(card) for card in self.history]
        }

        with self.save_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _get_card_key(card: CardInfo) -> tuple:
        return card.cardId, card.deckName

    def add_card(self, card: CardInfo) -> None:
        self.history = [h for h in self.history
                        if self._get_card_key(h) != self._get_card_key(card)]

        if not any(self._get_card_key(c) == self._get_card_key(card)
                   for c in self.current_cards):
            self.current_cards.append(card)
            self._save_to_file()

    def remove_card(self, card: CardInfo) -> None:
        self.current_cards = [c for c in self.current_cards
                              if self._get_card_key(c) != self._get_card_key(card)]

        if not any(self._get_card_key(h) == self._get_card_key(card)
                   for h in self.history):
            self.history.append(card)
            self._save_to_file()

    def get_current_cards(self) -> List[CardInfo]:
        return self.current_cards.copy()

    def get_history(self) -> List[CardInfo]:
        return self.history.copy()

    def clear_history(self) -> None:
        self.history = []
        self._save_to_file()
