from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (for development, you might want to configure this more specifically later)

# Dummy data - replace with your actual logic later
dummy_words = [
    {"word": "言葉", "id": 1},
    {"word": "勉強", "id": 2},
    {"word": "難しい", "id": 3},
    {"word": "例", "id": 4},
    {"word": "文章", "id": 5},
]

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

@app.route('/api/words', methods=['GET'])
def get_words():
    return jsonify(dummy_words)

@app.route('/api/sentences/<word>', methods=['GET'])
def get_sentences(word):
    if word in dummy_sentences:
        return jsonify(dummy_sentences[word])
    else:
        return jsonify([]) # Return empty list if no sentences found for the word


if __name__ == '__main__':
    app.run(debug=True, port=5001) # Run Flask app on port 5000
