let deckId = null;
let hand = [];
let turnCard = null;

document.getElementById('draw-deck').addEventListener('click', async () => {
  const response = await fetch('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1');
  const data = await response.json();
  deckId = data.deck_id;
  drawCards();
});

async function drawCards() {
  const response = await fetch(`https://deckofcardsapi.com/api/deck/${deckId}/draw/?count=52`);
  const data = await response.json();
  const cardsContainer = document.getElementById('cards');
  cardsContainer.innerHTML = '';

  data.cards.forEach(card => {
    const cardImg = document.createElement('img');
    cardImg.src = card.image;
    cardImg.dataset.code = card.code;
    cardImg.addEventListener('click', () => selectCard(card));
    cardsContainer.appendChild(cardImg);
  });
}

function selectCard(card) {
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
});
