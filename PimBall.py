html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<title>Super Pinball Arcade</title>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    min-height: 100vh;
    background: radial-gradient(circle at top, #202c59, #080b19 75%);
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px;
    overflow-x: hidden;
}

.game-container {
    width: 100%;
    max-width: 480px;
    text-align: center;
}

h1 {
    color: #ffe45c;
    font-size: clamp(25px, 7vw, 36px);
    text-shadow: 0 0 12px #ff8800;
    margin-bottom: 8px;
}

.info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-weight: bold;
    font-size: 15px;
}

.info div {
    background: #172044;
    border: 1px solid #5369b3;
    border-radius: 8px;
    padding: 9px 10px;
    flex: 1;
}

#status {
    color: #7dffb0;
    margin-bottom: 8px;
    min-height: 20px;
    font-size: 14px;
}

canvas {
    display: block;
    width: 100%;
    height: auto;
    background: #090d25;
    border: 3px solid #647bff;
    border-radius: 12px;
    box-shadow: 0 0 20px #384eff88;
    touch-action: none;
}

.buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 12px;
}

button {
    border: none;
    border-radius: 10px;
    padding: 14px 8px;
    font-size: 16px;
    font-weight: bold;
    color: white;
    cursor: pointer;
    touch-action: manipulation;
    user-select: none;
    -webkit-user-select: none;
}

#launchBtn {
    background: linear-gradient(#19bb65, #087c3a);
    box-shadow: 0 4px #045526;
}

#restartBtn {
    background: linear-gradient(#ff9d25, #d45a00);
    box-shadow: 0 4px #813700;
}

button:active {
    transform: translateY(2px);
}

.controls {
    display: flex;
    gap: 12px;
    margin-top: 14px;
}

.flipper-btn {
    flex: 1;
    background: linear-gradient(#6379ff, #293db3);
    box-shadow: 0 4px #18216c;
    padding: 18px 5px;
    font-size: 17px;
}

.instructions {
    color: #c5cbee;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 12px;
}

@media (max-height: 700px) {
    body {
        align-items: flex-start;
    }

    h1 {
        font-size: 25px;
    }

    .flipper-btn {
        padding: 12px 5px;
    }

    button {
        padding-top: 11px;
        padding-bottom: 11px;
    }
}
</style>
</head>

<body>

<div class="game-container">

    <h1>🎯 SUPER PINBALL</h1>

    <div class="info">
        <div>Pontos: <span id="score">0</span></div>
        <div>Recorde: <span id="record">0</span></div>
    </div>

    <div id="status">Pressione LANÇAR para começar!</div>

    <canvas id="gameCanvas" width="420" height="680"></canvas>

    <div class="buttons">
        <button id="launchBtn">🚀 LANÇAR BOLA</button>
        <button id="restartBtn">🔄 REINICIAR</button>
    </div>

    <div class="controls">
        <button id="leftBtn" class="flipper-btn">◀ ESQUERDA</button>
        <button id="rightBtn" class="flipper-btn">DIREITA ▶</button>
    </div>

    <div class="instructions">
        Use os botões para controlar as palhetas.<br>
        No computador, use as setas ← → ou as teclas A e D.<br>
        Se a bola cair, pressione REINICIAR e depois LANÇAR.
    </div>

</div>

<script>
"use strict";

// ========================================
// CONFIGURAÇÕES DO JOGO
// ========================================

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const scoreElement = document.getElementById("score");
const recordElement = document.getElementById("record");
const statusElement = document.getElementById("status");

const launchBtn = document.getElementById("launchBtn");
const restartBtn = document.getElementById("restartBtn");
const leftBtn = document.getElementById("leftBtn");
const rightBtn = document.getElementById("rightBtn");

// Gravidade menor para a bola não ficar muito rápida.
const grav = 0.20;

// Limite de velocidade da bola.
const maxSpeed = 13;

const ballRadius = 8;

// ========================================
// ESTADO DO JOGO
// ========================================

let score = 0;
let record = 0;

try {
    record = Number(localStorage.getItem("pinballRecord")) || 0;
} catch (e) {
    record = 0;
}

let active = true;
let launched = false;
let gameOver = false;

let vx = 0;
let vy = 0;

let leftPressed = false;
let rightPressed = false;

let animationStarted = false;
let lastTime = 0;

let ball = {
    x: W - 25,
    y: H - 45,
    r: ballRadius
};

let particles = [];

let bumpers = [
    { x: 115, y: 170, r: 23, color: "#ff4fcb", points: 100 },
    { x: 210, y: 125, r: 25, color: "#44eaff", points: 150 },
    { x: 305, y: 185, r: 23, color: "#ffe45c", points: 100 },
    { x: 145, y: 285, r: 20, color: "#7dff85", points: 100 },
    { x: 270, y: 300, r: 20, color: "#ff8050", points: 100 }
];

let bumpCooldown = [0, 0, 0, 0, 0];

// ========================================
// INTERFACE
// ========================================

function updateScore() {
    scoreElement.textContent = score;
    recordElement.textContent = record;
}

function updateStatus(text) {
    if (text) {
        statusElement.textContent = text;
        return;
    }

    if (gameOver) {
        statusElement.textContent = "Fim de jogo! Reinicie para jogar novamente.";
    } else if (!launched) {
        statusElement.textContent = "Pressione LANÇAR para começar!";
    } else {
        statusElement.textContent = "Boa sorte! Não deixe a bola cair!";
    }
}

// ========================================
// PREPARAR A BOLA
// ========================================

function prepareBall() {
    ball.x = W - 25;
    ball.y = H - 45;

    vx = 0;
    vy = 0;

    launched = false;

    leftPressed = false;
    rightPressed = false;

    bumpCooldown.fill(0);
    particles = [];
}

// ========================================
// REINICIAR JOGO
// ========================================

function reset() {
    score = 0;

    // IMPORTANTE:
    // O jogo volta a ficar ativo.
    // A bola fica pronta para um novo lançamento.
    active = true;
    gameOver = false;
    launched = false;

    prepareBall();

    updateScore();
    updateStatus("Jogo reiniciado! Pressione LANÇAR.");
    draw();
}

// ========================================
// LANÇAR A BOLA
// ========================================

function start() {

    // Se o jogo acabou, prepara uma nova partida.
    if (gameOver || !active) {
        reset();
    }

    // Evita lançar a mesma bola duas vezes.
    if (launched) {
        return;
    }

    // Garante que o jogo esteja ativo.
    active = true;
    gameOver = false;

    // Posição inicial da bola.
    ball.x = W - 25;
    ball.y = H - 45;

    // Velocidade horizontal inicial.
    vx = -0.4;

    // Lançamento vertical moderado.
    vy = -Math.sqrt(2 * grav * (H - 50)) - 1.5;

    // Limita a velocidade.
    vy = Math.max(-maxSpeed, vy);

    launched = true;

    updateStatus("Bola lançada!");
}

// ========================================
// PONTUAÇÃO
// ========================================

function addScore(points) {
    score += points;

    if (score > record) {
        record = score;

        try {
            localStorage.setItem("pinballRecord", record);
        } catch (e) {
            // O jogo continua funcionando mesmo sem armazenamento.
        }
    }

    updateScore();
}

// ========================================
// PARTÍCULAS
// ========================================

function createParticles(x, y, color) {
    for (let i = 0; i < 9; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5,
            life: 25,
            color: color
        });
    }
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];

        p.x += p.vx;
        p.y += p.vy;
        p.life--;

        if (p.life <= 0) {
            particles.splice(i, 1);
        }
    }
}

// ========================================
// COLISÃO COM CÍRCULOS
// ========================================

function collideCircle(obj, index) {
    const dx = ball.x - obj.x;
    const dy = ball.y - obj.y;

    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = ball.r + obj.r;

    if (distance >= minDistance || distance === 0) {
        return;
    }

    const nx = dx / distance;
    const ny = dy / distance;

    // Afasta a bola para evitar ficar presa dentro do objeto.
    const overlap = minDistance - distance;

    ball.x += nx * overlap;
    ball.y += ny * overlap;

    // Reflete a velocidade em relação à superfície.
    const dot = vx * nx + vy * ny;

    if (dot < 0) {
        vx -= 2 * dot * nx;
        vy -= 2 * dot * ny;
    }

    // Impulso moderado.
    vx += nx * 1.5;
    vy += ny * 1.5;

    // Evita somar pontos repetidamente enquanto há contato.
    if (bumpCooldown[index] <= 0) {
        addScore(obj.points);
        createParticles(obj.x, obj.y, obj.color);
        bumpCooldown[index] = 14;
    }

    limitSpeed();
}

// ========================================
// LIMITAR VELOCIDADE
// ========================================

function limitSpeed() {
    vx = Math.max(-maxSpeed, Math.min(maxSpeed, vx));
    vy = Math.max(-maxSpeed, Math.min(maxSpeed, vy));
}

// ========================================
// COLISÃO COM AS PAREDES
// ========================================

function collideWalls() {

    // Parede esquerda.
    if (ball.x - ball.r < 12) {
        ball.x = 12 + ball.r;
        vx = Math.abs(vx) * 0.82;
    }

    // Parede direita.
    if (ball.x + ball.r > W - 12) {
        ball.x = W - 12 - ball.r;
        vx = -Math.abs(vx) * 0.82;
    }

    // Parede superior.
    if (ball.y - ball.r < 12) {
        ball.y = 12 + ball.r;
        vy = Math.abs(vy) * 0.82;
    }

    // Parte superior do canal de lançamento.
    if (ball.x > W - 47 && ball.y > H - 125) {
        if (ball.x - ball.r < W - 48) {
            ball.x = W - 48 + ball.r;
            vx = Math.abs(vx) * 0.75;
        }
    }
}

// ========================================
// PALETAS DO PINBALL
// ========================================

function drawFlipper(x1, y1, x2, y2, pressed) {
    ctx.save();

    ctx.lineCap = "round";
    ctx.lineWidth = 15;

    ctx.strokeStyle = pressed ? "#fff07a" : "#ff4f91";

    ctx.shadowColor = pressed ? "#fff07a" : "#ff1680";
    ctx.shadowBlur = 14;

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    ctx.restore();
}

function flipperCollision(x1, y1, x2, y2, pressed, direction) {
    const dx = x2 - x1;
    const dy = y2 - y1;

    const lengthSquared = dx * dx + dy * dy;

    if (lengthSquared === 0) {
        return;
    }

    let t = ((ball.x - x1) * dx + (ball.y - y1) * dy) / lengthSquared;
    t = Math.max(0, Math.min(1, t));

    const closestX = x1 + t * dx;
    const closestY = y1 + t * dy;

    const distX = ball.x - closestX;
    const distY = ball.y - closestY;

    const distance = Math.sqrt(distX * distX + distY * distY);
    const minDistance = ball.r + 7;

    if (distance >= minDistance || distance === 0) {
        return;
    }

    const nx = distX / distance;
    const ny = distY / distance;

    ball.x = closestX + nx * minDistance;
    ball.y = closestY + ny * minDistance;

    // Impulso para devolver a bola para cima.
    if (pressed) {
        vx += direction * 2.0;
        vy = -Math.max(7, Math.abs(vy) * 0.65 + 5.5);
        addScore(10);
    } else {
        const dot = vx * nx + vy * ny;

        if (dot < 0) {
            vx -= 1.7 * dot * nx;
            vy -= 1.7 * dot * ny;
        }

        // Evita que a bola fique parada sobre a paleta.
        if (vy > -1) {
            vy = -2.5;
        }
    }

    limitSpeed();
}

function updateFlippers() {
    const left = leftPressed;
    const right = rightPressed;

    // Posição das paletas.
    const leftBase = { x: 125, y: 570 };
    const rightBase = { x: 295, y: 570 };

    const leftTip = left
        ? { x: 205, y: 545 }
        : { x: 200, y: 568 };

    const rightTip = right
        ? { x: 215, y: 545 }
        : { x: 220, y: 568 };

    flipperCollision(
        leftBase.x, leftBase.y,
        leftTip.x, leftTip.y,
        left, -1
    );

    flipperCollision(
        rightBase.x, rightBase.y,
        rightTip.x, rightTip.y,
        right, 1
    );
}

// ========================================
// ATUALIZAR A BOLA
// ========================================

function updateBall() {
    if (!active || !launched || gameOver) {
        return;
    }

    // Gravidade.
    vy += grav;

    limitSpeed();

    // Movimento.
    ball.x += vx;
    ball.y += vy;

    // Atrito leve.
    vx *= 0.999;

    collideWalls();

    // Colisão com os bumpers.
    for (let i = 0; i < bumpers.length; i++) {
        if (bumpCooldown[i] > 0) {
            bumpCooldown[i]--;
        }

        collideCircle(bumpers[i], i);
    }

    // Colisão com as paletas.
    updateFlippers();

    // Pequenos obstáculos triangulares.
    collideTriangle(70, 390, 125, 430);
    collideTriangle(350, 390, 295, 430);

    // A bola caiu.
    if (ball.y - ball.r > H) {
        endGame();
    }
}

// ========================================
// COLISÃO COM OBSTÁCULOS INCLINADOS
// ========================================

function collideTriangle(x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;

    const lengthSquared = dx * dx + dy * dy;

    let t = ((ball.x - x1) * dx + (ball.y - y1) * dy) / lengthSquared;
    t = Math.max(0, Math.min(1, t));

    const px = x1 + t * dx;
    const py = y1 + t * dy;

    const dxBall = ball.x - px;
    const dyBall = ball.y - py;

    const distance = Math.sqrt(dxBall * dxBall + dyBall * dyBall);

    if (distance < ball.r + 5 && distance > 0) {
        const nx = dxBall / distance;
        const ny = dyBall / distance;

        ball.x = px + nx * (ball.r + 5);
        ball.y = py + ny * (ball.r + 5);

        const dot = vx * nx + vy * ny;

        if (dot < 0) {
            vx -= 1.7 * dot * nx;
            vy -= 1.7 * dot * ny;
        }

        addScore(5);
        limitSpeed();
    }
}

// ========================================
// FIM DE JOGO
// ========================================

function endGame() {
    active = false;
    gameOver = true;
    launched = false;

    vx = 0;
    vy = 0;

    leftPressed = false;
    rightPressed = false;

    updateStatus("Fim de jogo! Pressione REINICIAR.");
    draw();
}

// ========================================
// DESENHAR O TABULEIRO
// ========================================

function drawBackground() {
    const gradient = ctx.createLinearGradient(0, 0, 0, H);

    gradient.addColorStop(0, "#141b45");
    gradient.addColorStop(1, "#07091a");

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, W, H);

    // Estrelas decorativas.
    ctx.fillStyle = "#ffffff";

    for (let i = 0; i < 45; i++) {
        const x = (i * 83 + 17) % W;
        const y = (i * 137 + 31) % H;

        ctx.globalAlpha = 0.2 + ((i % 5) / 8);
        ctx.fillRect(x, y, 2, 2);
    }

    ctx.globalAlpha = 1;
}

function drawWalls() {
    ctx.save();

    ctx.strokeStyle = "#6377ff";
    ctx.lineWidth = 5;
    ctx.shadowColor = "#4c62ff";
    ctx.shadowBlur = 12;

    ctx.beginPath();
    ctx.moveTo(12, 12);
    ctx.lineTo(W - 12, 12);
    ctx.lineTo(W - 12, H - 12);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(12, 12);
    ctx.lineTo(12, H - 12);
    ctx.stroke();

    // Canal de lançamento.
    ctx.beginPath();
    ctx.moveTo(W - 48, H - 125);
    ctx.lineTo(W - 48, 15);
    ctx.stroke();

    ctx.restore();
}

function drawBumpers() {
    for (const b of bumpers) {
        ctx.save();

        ctx.shadowColor = b.color;
        ctx.shadowBlur = 18;

        const gradient = ctx.createRadialGradient(
            b.x - 7, b.y - 7, 2,
            b.x, b.y, b.r
        );

        gradient.addColorStop(0, "#ffffff");
        gradient.addColorStop(0.25, b.color);
        gradient.addColorStop(1, "#171a48");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = b.color;
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.restore();
    }
}

function drawObstacles() {
    ctx.save();

    ctx.lineWidth = 8;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#ffc857";
    ctx.shadowColor = "#ff9d25";
    ctx.shadowBlur = 10;

    ctx.beginPath();
    ctx.moveTo(70, 390);
    ctx.lineTo(125, 430);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(350, 390);
    ctx.lineTo(295, 430);
    ctx.stroke();

    ctx.restore();

    // Guias inferiores.
    ctx.save();

    ctx.strokeStyle = "#3549b7";
    ctx.lineWidth = 4;

    ctx.beginPath();
    ctx.moveTo(35, 490);
    ctx.lineTo(100, 555);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(W - 35, 490);
    ctx.lineTo(W - 100, 555);
    ctx.stroke();

    ctx.restore();
}

function drawFlippersOnBoard() {
    const leftTip = leftPressed
        ? { x: 205, y: 545 }
        : { x: 200, y: 568 };

    const rightTip = rightPressed
        ? { x: 215, y: 545 }
        : { x: 220, y: 568 };

    drawFlipper(125, 570, leftTip.x, leftTip.y, leftPressed);
    drawFlipper(295, 570, rightTip.x, rightTip.y, rightPressed);

    // Eixos das paletas.
    ctx.fillStyle = "#fff07a";

    ctx.beginPath();
    ctx.arc(125, 570, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(295, 570, 8, 0, Math.PI * 2);
    ctx.fill();
}

function drawBall() {
    ctx.save();

    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 18;

    const gradient = ctx.createRadialGradient(
        ball.x - 3, ball.y - 4, 1,
        ball.x, ball.y, ball.r
    );

    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(0.5, "#d9f6ff");
    gradient.addColorStop(1, "#7598ff");

    ctx.fillStyle = gradient;

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
}

function drawParticles() {
    for (const p of particles) {
        ctx.save();

        ctx.globalAlpha = Math.max(0, p.life / 25);
        ctx.fillStyle = p.color;

        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }
}

function drawOverlay() {
    if (!gameOver) {
        return;
    }

    ctx.save();

    ctx.fillStyle = "rgba(0, 0, 0, 0.68)";
    ctx.fillRect(20, 250, W - 40, 125);

    ctx.textAlign = "center";

    ctx.fillStyle = "#ffe45c";
    ctx.font = "bold 29px Arial";
    ctx.fillText("FIM DE JOGO", W / 2, 300);

    ctx.fillStyle = "#ffffff";
    ctx.font = "17px Arial";
    ctx.fillText("Pontos: " + score, W / 2, 332);

    ctx.font = "14px Arial";
    ctx.fillText("Pressione REINICIAR", W / 2, 357);

    ctx.restore();
}

function draw() {
    drawBackground();
    drawWalls();
    drawObstacles();
    drawBumpers();
    drawFlippersOnBoard();
    drawBall();
    drawParticles();
    drawOverlay();
}

// ========================================
// CICLO PRINCIPAL
// ========================================

function tick(timestamp) {
    if (!animationStarted) {
        animationStarted = true;
    }

    // O ciclo continua mesmo quando a partida termina.
    // Isso permite desenhar a tela de fim de jogo e reiniciar.
    const delta = lastTime === 0 ? 1 : Math.min((timestamp - lastTime) / 16.67, 2);
    lastTime = timestamp;

    if (active && launched && !gameOver) {
        // Pequenos passos para movimento mais estável.
        const steps = Math.max(1, Math.ceil(delta));

        for (let i = 0; i < steps; i++) {
            updateBall();
        }
    }

    updateParticles();
    draw();

    requestAnimationFrame(tick);
}

// ========================================
// BOTÕES
// ========================================

launchBtn.addEventListener("click", function() {
    start();
});

restartBtn.addEventListener("click", function() {
    reset();
});

// ========================================
// CONTROLES DAS PALETAS
// ========================================

function pressLeft(event) {
    if (event) event.preventDefault();
    leftPressed = true;
}

function releaseLeft(event) {
    if (event) event.preventDefault();
    leftPressed = false;
}

function pressRight(event) {
    if (event) event.preventDefault();
    rightPressed = true;
}

function releaseRight(event) {
    if (event) event.preventDefault();
    rightPressed = false;
}

leftBtn.addEventListener("pointerdown", pressLeft);
leftBtn.addEventListener("pointerup", releaseLeft);
leftBtn.addEventListener("pointerleave", releaseLeft);
leftBtn.addEventListener("pointercancel", releaseLeft);

rightBtn.addEventListener("pointerdown", pressRight);
rightBtn.addEventListener("pointerup", releaseRight);
rightBtn.addEventListener("pointerleave", releaseRight);
rightBtn.addEventListener("pointercancel", releaseRight);

// ========================================
// TECLADO
// ========================================

document.addEventListener("keydown", function(event) {
    if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") {
        event.preventDefault();
        leftPressed = true;
    }

    if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") {
        event.preventDefault();
        rightPressed = true;
    }

    if (event.key === " " || event.key === "Enter") {
        event.preventDefault();

        if (!launched) {
            start();
        }
    }

    if (event.key.toLowerCase() === "r") {
        reset();
    }
});

document.addEventListener("keyup", function(event) {
    if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") {
        leftPressed = false;
    }

    if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") {
        rightPressed = false;
    }
});

// Solta as paletas se a janela perder o foco.
window.addEventListener("blur", function() {
    leftPressed = false;
    rightPressed = false;
});

// ========================================
// INICIALIZAÇÃO
// ========================================

updateScore();
prepareBall();
updateStatus();
draw();

// Apenas um ciclo de animação é iniciado.
// Ele continua rodando durante todo o jogo.
requestAnimationFrame(tick);

</script>

</body>
</html>
