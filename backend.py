import os.path

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path

from library.anki_client import AnkiConnectClient
from library.tts import generate_tts_audio_data
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
    days = request.args.get('days', default=7, type=int)
    limit = request.args.get('limit', default=10, type=int)
    recent_failed_cards = anki_client.get_failed_cards(days=days, limit=limit)
    for card in recent_failed_cards:
        card_manager.add_card(card)

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/anki_import_difficult', methods=['GET'])
def anki_import_difficult():
    limit = request.args.get('limit', default=100, type=int)
    reps = request.args.get('reps', default=30, type=int)
    ease = request.args.get('ease', default=1.4, type=float)

    difficult_cards = anki_client.get_difficult_cards(limit=limit, reps=reps, ease=ease)
    for card in difficult_cards:
        card_manager.add_card(card)

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/anki_import_exact', methods=['GET'])
def anki_import_exact():
    search = request.args.get('search', type=str)
    limit = request.args.get('limit', default=100, type=int)

    if not search:
        return jsonify({"error": "Search term is required"}), 400

    exact_match_cards = anki_client.get_exact_matches_cards(search=search, limit=limit)
    for card in exact_match_cards:
        card_manager.add_card(card)

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/remove_card', methods=['POST'])
def remove_card():
    data = request.get_json()
    card_id = data.get('cardId')

    if card_id is None:
        return jsonify({"error": "cardId is required"}), 400

    card_to_remove = None
    for card in card_manager.get_current_cards():
        if card.cardId == card_id:
            card_to_remove = card
            break

    if card_to_remove:
        card_manager.remove_card(card_to_remove)
    else:
        return jsonify({"error": f"Card with id {card_id} not found in current cards"}), 404

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/remove_all_cards', methods=['POST'])
def remove_all_cards():
    current_cards_copy = list(card_manager.get_current_cards())
    for card in current_cards_copy:
        card_manager.remove_card(card)

    current_cards = card_manager.get_current_cards()
    words_data = [{"word": card.first_field, "id": card.cardId} for card in current_cards]
    return jsonify(words_data)


@app.route('/api/anki_open', methods=['POST'])
def anki_open():
    data = request.get_json()
    card_id = data.get('cardId')

    if card_id is None:
        return jsonify({"error": "cardId is required"}), 400

    card_to_open = None
    for card in card_manager.get_current_cards():
        if card.cardId == card_id:
            card_to_open = card
            break

    if card_to_open:
        anki_client.open_card_browser(card_to_open.note)
        return jsonify({"success": "Opened in Anki Browser"})
    else:
        return jsonify({"error": f"Card with id {card_id} not found in current cards"}), 404


@app.route('/api/tts', methods=['GET'])
def tts():
    sentence = request.args.get('sentence')

    if not sentence:
        return jsonify({"error": "Sentence is required"}), 400

    audio_base64 = generate_tts_audio_data(sentence)

    if audio_base64:
        return jsonify({"audio_data": audio_base64})
    else:
        return jsonify({"error": "TTS generation failed"}), 50


if __name__ == '__main__':
    app.run(debug=True, port=5001)

