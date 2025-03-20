from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def calculate_cribbage_score(hand, turn_card):
    # Placeholder scoring function, implement actual cribbage logic here
    return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def score_hand():
    data = request.json
    hand = data.get('hand', [])
    turn_card = data.get('turn_card', None)

    if len(hand) != 4 or not turn_card:
        return jsonify({"error": "Invalid hand or turn card"}), 400

    score = calculate_cribbage_score(hand, turn_card)
    return jsonify({"score": score})

if __name__ == '__main__':
    app.run(debug=True)
