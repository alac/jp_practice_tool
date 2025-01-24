import os.path

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

from library.anki_client import AnkiConnectClient
from model.card_manager import CardManager

ANKI_CONNECT_HOST = "localhost"
ANKI_CONNECT_PORT = 8765
CARD_MANAGER_FILE = os.path.join("data", "card_manager_save.json")

app = Flask(__name__)
CORS(app)

anki_client = AnkiConnectClient(ANKI_CONNECT_HOST, ANKI_CONNECT_PORT)
card_manager = CardManager.load_from_file(Path(CARD_MANAGER_FILE))


@app.route('/api/words', methods=['GET'])
def get_words():
    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/sentences/<word>', methods=['GET'])
def get_sentences(word):
    dummy_sentences = {
        "言葉": [
            {"sentence": "これは言葉の例です。", "id": 101},
            {"sentence": "言葉はコミュニケーションの基本です。", "id": 102},
            {"sentence": "美しい言葉を使いましょう。", "id": 103},
        ],
        "勉強": [
            {"sentence": "毎日勉強するのは大変です。", "id": 201},
            {"sentence": "日本語の勉強は楽しいです。", "id": 202},
            {"sentence": "勉強すればするほど賢くなります。", "id": 203},
        ],
        "難しい": [
            {"sentence": "この問題は難しいですね。", "id": 301},
            {"sentence": "難しい漢字はたくさんあります。", "id": 302},
            {"sentence": "難しい決断を迫られています。", "id": 303},
        ],
        "例": [
            {"sentence": "例を挙げてください。", "id": 401},
            {"sentence": "例としてこれを考えてみましょう。", "id": 402},
            {"sentence": "例はたくさんありますが、一つだけ挙げます。", "id": 403},
        ],
        "文章": [
            {"sentence": "この文章は理解しやすいです。", "id": 501},
            {"sentence": "文章を書くのは難しいです。", "id": 502},
            {"sentence": "長い文章を読むのは疲れます。", "id": 503},
        ],
    }
    if word in dummy_sentences:
        return jsonify(dummy_sentences[word])
    else:
        return jsonify([])


@app.route('/api/anki_import_recent', methods=['GET'])
def anki_import_recent():
    from flask import request
    days = request.args.get('days', default=7, type=int)
    recent_failed_cards = anki_client.get_failed_cards(days=days, limit=100)
    for card in recent_failed_cards:
        card_manager.add_card(card)

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


if __name__ == '__main__':
    app.run(debug=True, port=5001) # Run Flask app on port 5000
