const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scale = 20;
let score = 0;

let snake = [{x: scale * 5, y: scale * 5}, {x: scale * 4, y: scale * 5}, {x: scale * 3, y: scale * 5}];
let direction = 'right';
let newDirection = 'right'; // Buffer for next direction
let food = {x: Math.floor(Math.random() * (canvas.width / scale)) * scale, y: Math.floor(Math.random() * (canvas.height / scale)) * scale};
let lastUpdateTime = 0;
const gameSpeed = 150; // Milliseconds between updates

// --- Control ---
document.addEventListener('keydown', changeDirection);

function changeDirection(event) {
    const key = event.key;
    if ((key === 'ArrowUp' || key === 'w') && direction !== 'down') {
        newDirection = 'up';
    } else if ((key === 'ArrowDown' || key === 's') && direction !== 'up') {
        newDirection = 'down';
    } else if ((key === 'ArrowLeft' || key === 'a') && direction !== 'right') {
        newDirection = 'left';
    } else if ((key === 'ArrowRight' || key === 'd') && direction !== 'left') {
        newDirection = 'right';
    }
}

// --- Drawing ---
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    snake.forEach(part => {
        ctx.fillStyle = 'green';
        ctx.fillRect(part.x, part.y, scale, scale);
    });
    ctx.fillStyle = 'red';
    ctx.fillRect(food.x, food.y, scale, scale);
    ctx.fillStyle = 'black';
    ctx.font = '24px Arial';
    ctx.fillText(`Score: ${score}`, 10, 30);
}

// --- Utility Functions ---
function getRandomPosition() {
    return {
        x: Math.floor(Math.random() * (canvas.width / scale)) * scale,
        y: Math.floor(Math.random() * (canvas.height / scale)) * scale
    };
}

function isPositionOnSnake(position, snakeArray) {
    return snakeArray.some(part => part.x === position.x && part.y === position.y);
}

// --- Game Logic ---
function moveSnake() {
    let head = {x: snake[0].x, y: snake[0].y};
    if (direction === 'right') head.x += scale;
    if (direction === 'left') head.x -= scale;
    if (direction === 'up') head.y -= scale;
    if (direction === 'down') head.y += scale;
    snake.unshift(head); // Add new head
}

function placeFood() {
    let newFoodPosition;
    do {
        newFoodPosition = getRandomPosition();
    } while (isPositionOnSnake(newFoodPosition, snake)); // Keep trying until food is not on the snake
    food = newFoodPosition;
}

function checkFoodCollision() {
    if (snake[0].x === food.x && snake[0].y === food.y) {
        score++;
        placeFood(); // Place new food correctly
        // Don't pop the tail, effectively growing the snake
    } else {
        snake.pop(); // Remove tail if no food eaten
    }
}

function checkGameOverCollision() {
    const head = snake[0];
    const hitLeftWall = head.x < 0;
    const hitRightWall = head.x >= canvas.width;
    const hitTopWall = head.y < 0;
    const hitBottomWall = head.y >= canvas.height;
    const hitSelf = snake.slice(1).some(part => part.x === head.x && part.y === head.y);

    if (hitLeftWall || hitRightWall || hitTopWall || hitBottomWall || hitSelf) {
        alert('Game Over! Final Score: ' + score);
        resetGame();
    }
}

function resetGame() {
    score = 0;
    snake = [{x: scale * 5, y: scale * 5}, {x: scale * 4, y: scale * 5}, {x: scale * 3, y: scale * 5}];
    direction = 'right';
    newDirection = 'right';
    placeFood(); // Place initial food correctly
}

function update() {
    moveSnake();
    checkFoodCollision();
    checkGameOverCollision();
}

// --- Game Loop ---
function loop(currentTime) {
    requestAnimationFrame(loop); // Request next frame

    const timeSinceLastUpdate = currentTime - lastUpdateTime;

    // Only update game state if enough time has passed
    if (timeSinceLastUpdate > gameSpeed) {
        lastUpdateTime = currentTime; // Reset the timer

        // Update direction based on buffered input
        direction = newDirection;

        update(); // Update game logic
        draw();   // Redraw the game
    }
}

// Initial setup
resetGame(); // Set initial game state

// Start the game loop
requestAnimationFrame(loop);
