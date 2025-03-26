let deckId = null;
let hand = [];
let turnCard = null;

const suits = ['S', 'H', 'D', 'C'];
const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K'];

document.getElementById('draw-deck').addEventListener('click', () => {
  const cardsDiv = document.getElementById('cards');
  cardsDiv.innerHTML = ''; // Clear previous cards

  // Generate and display an ordered deck
  const deck = [];
  for (const suit of suits) {
    for (const rank of ranks) {
      const cardCode = `${rank}${suit}`;
      deck.push(cardCode);
      const img = document.createElement('img');
      img.src = `https://deckofcardsapi.com/static/img/${cardCode}.png`;
      img.alt = cardCode;
      img.dataset.code = cardCode;
      img.style.width = '100px';
      img.style.height = '140px';
      img.addEventListener('click', () => selectCard({ code: cardCode, image: img.src }));
      cardsDiv.appendChild(img);
    }
  }
});

function selectCard(card) {
  // Check if card is already in hand
  const handIndex = hand.indexOf(card.code);
  if (handIndex !== -1) {
    // Remove from hand
    hand.splice(handIndex, 1);
    document.getElementById('hand').removeChild(
      Array.from(document.getElementById('hand').children)
        .find(img => img.src === card.image)
    );
    return;
  }

  // Check if card is the turn card
  if (turnCard === card.code) {
    turnCard = null;
    document.getElementById('turn-card').innerHTML = '';
    return;
  }

  // Add card if possible
  if (hand.length < 4) {
    hand.push(card.code);
    displayCard(card, 'hand');
  } else if (!turnCard) {
    turnCard = card.code;
    displayCard(card, 'turn-card');
  }
}

function displayCard(card, containerId) {
  const cardImg = document.createElement('img');
  cardImg.src = card.image;
  cardImg.style.width = '100px';
  cardImg.style.height = '140px';
  document.getElementById(containerId).appendChild(cardImg);
}

document.getElementById('score-btn').addEventListener('click', async () => {
  if (hand.length !== 4 || !turnCard) {
    alert('Please select 4 cards for your hand and 1 turn card.');
    return;
  }

  const response = await fetch('/score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hand, turn_card: turnCard })
  });

  const result = await response.json();
  document.getElementById('score').innerText = result.error || `Score: ${result.score}`;

  if (result.breakdown) {
    console.log(result.breakdown);
    displayScoreBreakdown(result.breakdown);
  } else {
    console.log("No breakdown received");
  }
});

function displayScoreBreakdown(breakdown) {
  const breakdownDiv = document.getElementById('score-breakdown');
  breakdownDiv.innerHTML = '<h3>Score Breakdown:</h3>';

  function createCardImages(cards) {
    return cards.map(card => 
      `<img src="https://deckofcardsapi.com/static/img/${card}.png" 
           alt="${card}" 
           style="width: 50px; height: 70px; margin: 2px;">`
    ).join('');
  }

  // Display 15s breakdown
  if (breakdown['15s'] && breakdown['15s'].length > 0) {
    let fifteensHTML = '<h4>15s:</h4><ul>';
    breakdown['15s'].forEach(combo => {
      fifteensHTML += `<li>${createCardImages(combo)} = 2 points</li>`;
    });
    fifteensHTML += '</ul>';
    breakdownDiv.innerHTML += fifteensHTML;
  }

  // Display Pairs breakdown
  if (breakdown['pairs'] && breakdown['pairs'].length > 0) {
    let pairsHTML = '<h4>Pairs:</h4><ul>';
    breakdown['pairs'].forEach(pair => {
      pairsHTML += `<li>${createCardImages(pair)} = 2 points</li>`;
    });
    pairsHTML += '</ul>';
    breakdownDiv.innerHTML += pairsHTML;
  }

  // Display Runs breakdown
  if (breakdown['runs'] && breakdown['runs'].length > 0) {
    let runsHTML = '<h4>Runs:</h4><ul>';
    breakdown['runs'].forEach(run => {
      runsHTML += `<li>${createCardImages(run)} = ${run.length} points</li>`;
    });
    runsHTML += '</ul>';
    breakdownDiv.innerHTML += runsHTML;
  }

  // Display Flushes breakdown
  if (breakdown['flushes'] && breakdown['flushes'].length > 0) {
    let flushesHTML = '<h4>Flushes:</h4><ul>';
    breakdown['flushes'].forEach(flush => {
      flushesHTML += `<li>${createCardImages(flush)} = ${flush.length === 5 ? 5 : 4} points</li>`;
    });
    flushesHTML += '</ul>';
    breakdownDiv.innerHTML += flushesHTML;
  }

  // Display His Nobs breakdown
  if (breakdown['his_nobs'] && breakdown['his_nobs'].length > 0) {
    let hisNobsHTML = '<h4>His Nobs:</h4><ul>';
    breakdown['his_nobs'].forEach(jack => {
      hisNobsHTML += `<li>${createCardImages([jack])} = 1 point</li>`;
    });
    hisNobsHTML += '</ul>';
    breakdownDiv.innerHTML += hisNobsHTML;
  }

  if (!Object.keys(breakdown).length) {
    breakdownDiv.innerHTML = 'No breakdown available';
  }
}