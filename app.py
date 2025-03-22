from flask import Flask, render_template, request, jsonify
import requests
from itertools import combinations
from collections import Counter


app = Flask(__name__)

from itertools import combinations

def card_value(card):
    """Returns the value of the card for scoring 15s."""
    if card[0].isdigit():
        return int(card[0])
    elif card[0] in ['T', 'J', 'Q', 'K']:
        return 10
    elif card[0] == 'A':
        return 1
    return 0

def calculate_cribbage_score(hand, turn_card):
    """Calculate the score for a Cribbage hand and turn card with a breakdown."""
    all_cards = hand + [turn_card]
    total_score = 0

    # Convert card strings like '5S' to values and suits
    values = [card[:-1] for card in all_cards]
    suits = [card[-1] for card in all_cards]

    breakdown = {
        "15s": [],
        "pairs": [],
        "runs": [],
        "flushes": [],
        "his_nobs": []
    }

    # Scoring for 15s
    for i in range(2, 6):
        for combo in combinations(all_cards, i):
            if sum(card_value(card) for card in combo) == 15:
                total_score += 2
                breakdown["15s"].append([card for card in combo])

    # Scoring for pairs, triples, and four of a kind
    value_counts = Counter(values)
    for value, count in value_counts.items():
        cards_with_value = [card for card in all_cards if card[0] == value]
        if count == 4:  # Four of a kind (worth 12 points - 6 different pairs)
            total_score += 12
            for pair in combinations(cards_with_value, 2):
                breakdown["pairs"].append(list(pair))
        elif count == 3:  # Three of a kind (6 points - 3 different pairs)
            if not any(c == 4 for c in value_counts.values()):
                total_score += 6
                for pair in combinations(cards_with_value, 2):
                    breakdown["pairs"].append(list(pair))
        elif count == 2:  # One pair (2 points)
            if not any(c >= 3 for c in value_counts.values()):
                total_score += 2
                for pair in combinations(cards_with_value, 2):
                    breakdown["pairs"].append(list(pair))

    # Scoring for runs
    run_points = calculate_runs(all_cards, breakdown)
    total_score += run_points

    # Scoring for flushes
    if suits.count(suits[0]) == 5:
        total_score += 5
        breakdown["flushes"].append(all_cards)
    elif suits.count(suits[0]) == 4 and suits[-1] != suits[0]:
        total_score += 4
        breakdown["flushes"].append(all_cards)

    # His Nobs (Jack matching the turn card suit)
    for card in hand:
        if card[0] == 'J' and card[-1] == turn_card[-1]:
            total_score += 1
            breakdown["his_nobs"].append(card)

    return total_score, breakdown

def calculate_runs(all_cards, breakdown):
    """Calculate the total points for runs in the hand."""
    sorted_cards = sorted(all_cards, key=lambda x: card_value(x))  # Sort cards by their numeric value
    run_points = 0
    seen_runs = set()

    # Find all possible runs
    for i in range(len(sorted_cards)):
        for j in range(i + 3, len(sorted_cards) + 1):  # Runs need to have at least 3 cards
            run = sorted_cards[i:j]
            run_values = [card_value(card) for card in run]
            run_suits = [card[-1] for card in run]

            # Check if the run is a valid consecutive sequence and has at least 3 unique cards
            if len(set(run_values)) == len(run_values) and max(run_values) - min(run_values) == len(run_values) - 1:
                run_tuple = tuple(sorted(run))  # Create a tuple to store in seen_runs (to avoid counting duplicates)
                if run_tuple not in seen_runs:
                    seen_runs.add(run_tuple)
                    run_points += len(run_values)  # Add points for the run (points = length of the run)
                    breakdown["runs"].append([card for card in run])
    
    return run_points


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

    score, breakdown = calculate_cribbage_score(hand, turn_card)
    return jsonify({
        "score": score,
        "breakdown": breakdown  # Return both the score and the breakdown
    })

if __name__ == '__main__':
    app.run(debug=True)
