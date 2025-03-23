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
    # Convert cards to their numeric values for sorting
    value_map = {'A': 1, 'T': 10, 'J': 11, 'Q': 12, 'K': 13}
    def get_sort_value(card):
        return value_map.get(card[0], int(card[0]))
    
    sorted_cards = sorted(all_cards, key=get_sort_value)
    run_points = 0
    
    # For each possible length
    for length in range(5, 2, -1):
        runs_found = []
        
        # Check each possible subset of cards
        for subset in combinations(sorted_cards, length):
            subset = list(sorted(subset, key=get_sort_value))
            subset_values = [get_sort_value(card) for card in subset]
            
            # Check if it forms a run (consecutive numbers)
            if (max(subset_values) - min(subset_values) == length - 1 and
                all(n in subset_values for n in range(min(subset_values), max(subset_values) + 1))):
                runs_found.append(subset)
        
        # If we found runs of this length
        if runs_found:
            # Add each run to the breakdown and count points
            for run in runs_found:
                breakdown["runs"].append(list(run))
                run_points += length  # Add points for each run found
            return run_points  # Return after finding all runs of the longest length
    
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
