import os.path

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path

from library.ai_requests import run_ai_request_stream
from library.anki_client import AnkiConnectClient
from library.database_interface import DATABASE_ROOT
from library.tts import generate_tts_audio_data
from library.grab_examples import get_examples_for_word
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


@app.route('/api/examples/<word>', methods=['GET'])
def get_examples(word):
    examples = get_examples_for_word(word, DATABASE_ROOT)
    examples_data = []
    for example in examples:
        examples_data.append({
            "filename": example.filename,
            "line_number": example.line_number,
            "sentences": example.sentences,
            "example_line": example.example_line
        })
    return jsonify(examples_data)


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


@app.route('/api/exercises/disambiguate/<word>', methods=['GET'])
def get_disambiguate_exercise(word):
    prompt = f"""
Generate a disambiguation exercise for the Japanese word "{word}".
Include a list of 3-4 Japanese words that are similar to "{word}" and their English definitions.
Create a question that asks the user to match each Japanese word with its correct English definition.
Present the definitions in a scrambled order.
Return two sections:
1. <task>Question in markdown format (including the word matching exercise)</task>
2. <answer>Explanation in markdown format</answer>

Example output format:

<task>
<question>
**Match the Japanese words to their English definitions.**

Words:
1.  走る
2.  駆ける
3.  逃げる

Definitions:
- (A) To run away; to escape
- (B) To run; to dash; to sprint
- (C) To run; to travel (e.g., a vehicle); to flow (e.g., water, time); to elapse

Match the words to the definitions (e.g., 1-B, 2-C, 3-A):
</question>
<answer>
**Explanation:**

*   走る: Broadest sense of "run," including vehicles and flowing liquids.
*   駆ける:  Implies running quickly, dashing or sprinting.
*   逃げる: Specifically means "to run away" or "to escape."
</answer>
</task>

"""
    result_text = ""
    for tok in run_ai_request_stream(prompt, ["</task>"], print_prompt=False, temperature=0.1, ban_eos_token=False, max_response=1000):
        result_text += tok

    task_start = result_text.find("<question>")
    task_end = result_text.find("</question>")
    answer_start = result_text.find("<answer>")
    answer_end = result_text.find("</answer>")

    if task_start != -1 and task_end != -1 and answer_start != -1 and answer_end != -1:
        question = result_text[task_start + len("<question>"):task_end].strip()
        explanation = result_text[answer_start + len("<answer>"):answer_end].strip()
        return jsonify({"question": question, "explanation": explanation})
    else:
        return jsonify({"error": "Could not parse LLM response", "raw_response": result_text}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
