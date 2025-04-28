let digits = [];
let currentSpan = 3;
const maxSpan = 8;
let index = 0;

const digitDisplay = document.getElementById('digitDisplay');
const instruction = document.getElementById('instruction');
const responseInput = document.getElementById('responseInput');
const startBtn = document.getElementById('startBtn');
const submitBtn = document.getElementById('submitBtn');
const feedback = document.getElementById('feedback');

startBtn.onclick = startTest;
submitBtn.onclick = checkResponse;

function startTest() {
  startBtn.style.display = 'none';
  feedback.innerText = '';
  digits = Array.from({length: currentSpan}, () => Math.floor(Math.random() * 10));
  index = 0;
  instruction.innerText = 'Remember these digits!';
  showNextDigit();
}

function showNextDigit() {
  if (index < digits.length) {
    digitDisplay.innerText = digits[index];
    index++;
    setTimeout(() => {
      digitDisplay.innerText = '';
      setTimeout(showNextDigit, 500);
    }, 1000);
  } else {
    instruction.innerText = 'Type the digits in reverse order:';
    responseInput.style.display = 'inline';
    submitBtn.style.display = 'inline';
    responseInput.value = '';
    responseInput.focus();
  }
}

function checkResponse() {
  const response = responseInput.value.trim();
  const correctAnswer = digits.slice().reverse().join('');
  if (response === correctAnswer) {
    feedback.innerText = 'Correct!';
    currentSpan++;
    if (currentSpan > maxSpan) {
      feedback.innerText = 'Congratulations! Test complete!';
      resetTest();
    } else {
      nextTrial();
    }
  } else {
    feedback.innerText = `Incorrect. Correct was: ${correctAnswer}`;
    resetTest();
  }
}

function nextTrial() {
  responseInput.style.display = 'none';
  submitBtn.style.display = 'none';
  setTimeout(startTest, 2000);
}

function resetTest() {
  responseInput.style.display = 'none';
  submitBtn.style.display = 'none';
  startBtn.style.display = 'inline';
  instruction.innerText = 'Press START to begin again';
  currentSpan = 3;  // Reset span length if incorrect
}
