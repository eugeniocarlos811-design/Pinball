html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<title>Super Pinball Arcade</title>

<style>
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #111;
    font-family: Arial, sans-serif;
    touch-action: manipulation;
}

#app {
    height: 100vh;
    height: 100dvh;
    display: flex;
    flex-direction: column;
    background: #dcdcdc;
}

#top {
    color: #fff;
    background: #151515;
    text-align: center;
    padding: 8px;
    font-weight: bold;
    font-size: 14px;
}

#game {
    display: block;
    width: 100%;
    flex: 1;
    min-height: 0;
    background: #05070b;
    touch-action: none;
}

#controls {
    display: grid;
    grid-template-columns: 1fr 1.2fr 1fr;
    gap: 7px;
    padding: 8px;
    background: #e5e5e5;
}

button {
    border: 3px solid #555;
    border-radius: 10px;
    background: #fff;
    color: #37474f;
    font-weight: bold;
    font-size: clamp(11px, 2.8vw, 16px);
    min-height: 62px;
    padding: 8px 3px;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
}

#launch {
    background: #4caf50;
    color: white;
    border-color: #2e7d32;
}

#restart {
    position: absolute;
    top: 42px;
    right: 8px;
    z-index: 2;
    border: 0;
    border-radius: 6px;
    background: #ff5252;
    color: #fff;
    min-height: 0;
    padding: 8px 12px;
    font-size: 14px;
}

button:active,
.pressed {
    filter: brightness(.78);
    transform: scale(.99);
}

@media (min-width: 800px) {
    #controls {
        padding: 10px 12%;
        gap: 14px;
    }

    button {
        min-height: 70px;
        font-size: 16px;
    }

    #top {
        font-size: 16px;
    }
}
</style>
</head>

<body>

<div id="app">

    <div id="top">SUPER PINBALL ARCADE</div>

    <canvas id="game"></canvas>

    <button id="restart">REINICIAR ↻</button>

    <div id="controls">
        <button id="left">
            ← SETA ESQ.<br>PALHETA ESQ.
        </button>

        <button id="launch">
            ▲ ESPAÇO ▲<br>LANÇAR BOLA
        </button>

        <button id="right">
            SETA DIR. →<br>PALHETA DIR.
        </button>
    </div>

</div>

<script>
(() => {

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const status = document.getElementById('top');

let W = 0;
let H = 0;
let util = 0;
let r = 11;

// VELOCIDADE REDUZIDA
const grav = 0.20;
const maxSpeed = 13;

let ball = { x: 0, y: 0 };
let vx = 0;
let vy = 0;

let score = 0;

let record = Number(
    localStorage.getItem('pinballRecord') || 0
);

let launched = false;
let arena = false;
let active = true;

let leftOn = false;
let rightOn = false;

let raf = 0;
let obstacles = [];
let flippers = [];

let lastHit = 0;
let lastFlipperHit = 0;

// SONS
function beep(high = false) {
    try {
        const AudioCtx =
            window.AudioContext ||
            window.webkitAudioContext;

        const a = new AudioCtx();
        const o = a.createOscillator();
        const g = a.createGain();

        o.frequency.value = high ? 880 : 587;
        g.gain.value = 0.025;

        o.connect(g);
        g.connect(a.destination);

        o.start();
        o.stop(a.currentTime + 0.055);

        o.onended = () => a.close();
    } catch (e) {}
}

// REDIMENSIONAR A TELA
function resize() {
    const dpr = Math.min(
        window.devicePixelRatio || 1,
        2
    );

    const rect = canvas.getBoundingClientRect();

    W = rect.width;
    H = rect.height;

    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    util = W - Math.max(42, W * 0.045);

    r = Math.max(
        5,
        Math.min(12, W * 0.014)
    );

    setup();
    draw();
}

// PREPARAR OBSTÁCULOS
function setup() {
    const bumpR = Math.max(13, W * 0.038);

    obstacles = [
        {
            x: util * 0.30,
            y: H * 0.25,
            rad: bumpR,
            color: '#00e5ff',
            points: 10,
            impulse: 0.96,
            high: false
        },
        {
            x: util * 0.70,
            y: H * 0.25,
            rad: bumpR,
            color: '#00e5ff',
            points: 10,
            impulse: 0.96,
            high: false
        },
        {
            x: util * 0.50,
            y: H * 0.38,
            rad: bumpR,
            color: '#e040fb',
            points: 10,
            impulse: 0.96,
            high: false
        },
        {
            x: util * 0.15,
            y: H * 0.12,
            rad: bumpR,
            color: '#ffd700',
            points: 30,
            impulse: 1.00,
            high: true,
            star: true
        },
        {
            x: util * 0.50,
            y: H * 0.10,
            rad: bumpR,
            color: '#ffd700',
            points: 30,
            impulse: 1.00,
            high: true,
            star: true
        },
        {
            x: util * 0.85,
            y: H * 0.12,
            rad: bumpR,
            color: '#ffd700',
            points: 30,
            impulse: 1.00,
            high: true,
            star: true
        },
        {
            x: util * 0.20,
            y: H * 0.52,
            rad: bumpR,
            color: '#ff1744',
            points: 50,
            impulse: 1.02,
            high: true,
            diamond: true
        },
        {
            x: util * 0.80,
            y: H * 0.52,
            rad: bumpR,
            color: '#ff1744',
            points: 50,
            impulse: 1.02,
            high: true,
            diamond: true
        }
    ];

    prepareBall();
}

// PREPARAR BOLA
function prepareBall() {
    ball = {
        x: W - 25,
        y: H - 45
    };

    vx = 0;
    vy = 0;

    launched = false;
    arena = false;

    lastHit = 0;
    lastFlipperHit = 0;

    leftOn = false;
    rightOn = false;

    flippers = [];
}

// LANÇAR BOLA
function start() {

    // Se acabou, inicia uma partida nova.
    if (!active) {
        reset();
    }

    // Não lança duas vezes a mesma bola.
    if (launched) {
        return;
    }

    beep(true);

    ball.x = W - 25;
    ball.y = H - 45;

    vx = 0;

    // LANÇAMENTO MAIS LENTO
    vy = -Math.sqrt(2 * grav * (H - 50)) - 1.5;

    // Limitar a velocidade inicial.
    vy = Math.max(-maxSpeed, vy);

    launched = true;
    arena = false;
    active = true;

    updateStatus();
}

// REINICIAR PARTIDA
function reset() {

    score = 0;

    active = true;

    // Zera completamente o estado anterior.
    launched = false;
    arena = false;

    vx = 0;
    vy = 0;

    leftOn = false;
    rightOn = false;

    lastHit = 0;
    lastFlipperHit = 0;

    // Prepara novamente a bola.
    prepareBall();

    updateStatus();
    draw();
}

// ATUALIZAR PLACAR
function updateStatus() {
    status.textContent =
        `PONTOS: ${score} | RECORDE: ${record}`;
}

// GEOMETRIA DAS PALHETAS
function geometry() {

    const y = H * 0.99;

    const gapL = util * 0.33;
    const gapR = util * 0.67;

    const len = util * 0.15;

    const aL = leftOn ? -22 : 16;
    const aR = rightOn ? 202 : 164;

    const radL = aL * Math.PI / 180;
    const radR = aR * Math.PI / 180;

    flippers = [
        {
            x1: gapL,
            y1: y,
            x2: gapL + Math.cos(radL) * len,
            y2: y + Math.sin(radL) * len,
            active: leftOn,
            side: 'L'
        },
        {
            x1: gapR,
            y1: y,
            x2: gapR + Math.cos(radR) * len,
            y2: y + Math.sin(radR) * len,
            active: rightOn,
            side: 'R'
        }
    ];
}

// COLISÃO COM PALHETAS
function lineHit(f, x, y) {

    const dx = f.x2 - f.x1;
    const dy = f.y2 - f.y1;

    const u = (
        (x - f.x1) * dx +
        (y - f.y1) * dy
    ) / (dx * dx + dy * dy || 1);

    const clamped = Math.max(
        0,
        Math.min(1, u)
    );

    const px = f.x1 + clamped * dx;
    const py = f.y1 + clamped * dy;

    return Math.hypot(
        x - px,
        y - py
    ) < r + 8;
}

// DESENHAR JOGO
function draw() {

    ctx.clearRect(0, 0, W, H);

    ctx.fillStyle = '#05070b';
    ctx.fillRect(0, 0, W, H);

    const startY = H * 0.60;
    const endY = H * 0.99;

    const gL = util * 0.33;
    const gR = util * 0.67;

    // CORREDOR DE LANÇAMENTO
    ctx.strokeStyle = '#858585';
    ctx.lineWidth = 3;

    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(util, 65);
    ctx.lineTo(util, H);
    ctx.stroke();

    ctx.setLineDash([]);

    ctx.strokeStyle = 'yellow';
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(util, 45);
    ctx.lineTo(W, 0);
    ctx.stroke();

    // INDICADORES
    for (let i = 0; i < 3; i++) {

        ctx.fillStyle = '#00ff00';
        ctx.font = 'bold 26px Arial';
        ctx.textAlign = 'center';

        ctx.fillText(
            '▲',
            W - 22,
            H * 0.22 + i * H * 0.19
        );
    }

    // PAREDES INFERIORES
    ctx.fillStyle = '#1e1e1e';
    ctx.strokeStyle = 'yellow';
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(0, startY);
    ctx.lineTo(gL, endY);
    ctx.lineTo(0, endY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(util, startY);
    ctx.lineTo(gR, endY);
    ctx.lineTo(util, endY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // OBSTÁCULOS
    for (const o of obstacles) {

        ctx.beginPath();

        ctx.arc(
            o.x,
            o.y,
            o.rad,
            0,
            Math.PI * 2
        );

        ctx.fillStyle = o.star ? '#222' : o.color;
        ctx.fill();

        ctx.lineWidth = o.star ? 3 : 2;
        ctx.strokeStyle = o.star ? o.color : '#fff';
        ctx.stroke();

        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        ctx.font =
            `bold ${o.star ? 20 : o.diamond ? 22 : 16}px Arial`;

        ctx.fillText(
            o.star ? '★' : o.diamond ? '♦' : '●',
            o.x,
            o.y
        );
    }

    // PALHETAS
    geometry();

    for (const f of flippers) {

        ctx.fillStyle = '#ef5350';
        ctx.strokeStyle = '#b71c1c';
        ctx.lineWidth = 4;

        ctx.beginPath();

        ctx.moveTo(f.x1, f.y1 - 6);
        ctx.lineTo(f.x1, f.y1 + 34);

        ctx.lineTo(
            f.x1 + (f.side === 'L' ? 12 : -12),
            f.y1 + 34
        );

        ctx.lineTo(f.x2, f.y2);

        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }

    // BOLA
    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        r,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = '#f5f5f5';
    ctx.fill();

    ctx.lineWidth = 2;
    ctx.strokeStyle = '#b0b0b0';
    ctx.stroke();

    // GAME OVER
    if (!active) {

        ctx.fillStyle = 'rgba(0,0,0,.72)';
        ctx.fillRect(0, 0, W, H);

        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';

        ctx.font = 'bold 25px Arial';

        ctx.fillText(
            'GAME OVER',
            W / 2,
            H / 2 - 12
        );

        ctx.font = 'bold 15px Arial';

        ctx.fillText(
            'Toque em REINICIAR ou LANÇAR BOLA',
            W / 2,
            H / 2 + 18
        );
    }
}

// MOVIMENTO DA BOLA
function tick() {

    if (active && launched) {

        // GRAVIDADE REDUZIDA
        vy += grav;

        // LIMITAR VELOCIDADE
        vx = Math.max(
            -maxSpeed,
            Math.min(maxSpeed, vx)
        );

        vy = Math.max(
            -maxSpeed,
            Math.min(maxSpeed, vy)
        );

        ball.x += vx;
        ball.y += vy;

        // ENTRADA NA ÁREA PRINCIPAL
        if (!arena) {

            if (ball.x >= util && ball.y <= 110) {

                vx = -7;
                vy = 1.5;

                arena = true;

                ball.x -= 20;
                ball.y += 15;
            }

        } else if (
            ball.x - r < util &&
            ball.x + r >= util &&
            ball.y > 35
        ) {

            vx = -Math.abs(vx);

            ball.x -= 4;
        }

        // PAREDE ESQUERDA E DIREITA
        if (ball.x - r <= 0) {

            vx = Math.abs(vx) * 0.98;
            ball.x = r + 2;

        } else if (ball.x + r >= W) {

            vx = -Math.abs(vx) * 0.98;
            ball.x = W - r - 2;
        }

        // TETO
        if (ball.y - r <= 0) {

            vy = Math.abs(vy) * 0.80;
            ball.y = r + 2;
        }

        const startY = H * 0.60;
        const endY = H * 0.99;

        const gL = util * 0.33;
        const gR = util * 0.67;

        // PAREDES INCLINADAS
        if (
            arena &&
            ball.y >= startY &&
            ball.y <= endY
        ) {

            if (ball.x <= gL) {

                const prop = ball.x / gL;

                const lim =
                    startY + (endY - startY) * prop;

                if (ball.y + r >= lim - 4) {

                    vx = Math.abs(vx) * 0.35 + 1.5;
                    vy = Math.abs(vy) * 0.45 + 1.2;

                    ball.x += 2;
                    ball.y += 1;
                }

            } else if (
                ball.x >= gR &&
                ball.x < util
            ) {

                const prop =
                    (util - ball.x) / (util - gR);

                const lim =
                    startY + (endY - startY) * prop;

                if (ball.y + r >= lim - 4) {

                    vx = -Math.abs(vx) * 0.35 - 1.5;
                    vy = Math.abs(vy) * 0.45 + 1.2;

                    ball.x -= 2;
                    ball.y += 1;
                }
            }
        }

        // COLISÕES COM OBSTÁCULOS
        for (const o of obstacles) {

            const dx = ball.x - o.x;
            const dy = ball.y - o.y;

            const dist = Math.hypot(dx, dy);

            if (
                dist < o.rad + r &&
                performance.now() - lastHit > 100
            ) {

                lastHit = performance.now();

                beep(o.high);

                // DIREÇÃO DA COLISÃO
                const distSafe = Math.max(dist, 1);

                const nx = dx / distSafe;
                const ny = dy / distSafe;

                // Rebate sem aumentar demais a velocidade.
                const dot = vx * nx + vy * ny;

                if (dot < 0) {

                    vx -= 1.65 * dot * nx;
                    vy -= 1.65 * dot * ny;
                }

                vx += nx * 0.7;
                vy += ny * 0.7;

                // PONTUAÇÃO
                score += o.points;

                if (score > record) {

                    record = score;

                    localStorage.setItem(
                        'pinballRecord',
                        record
                    );
                }

                updateStatus();

                // AFASTAR BOLA DO OBSTÁCULO
                ball.x =
                    o.x + nx * (o.rad + r + 1);

                ball.y =
                    o.y + ny * (o.rad + r + 1);
            }
        }

        // PALHETAS
        geometry();

        let touched = false;

        if (arena) {

            for (const f of flippers) {

                if (lineHit(f, ball.x, ball.y)) {

                    // Evita impulsos repetidos no mesmo contato.
                    if (
                        performance.now() - lastFlipperHit < 100
                    ) {
                        continue;
                    }

                    lastFlipperHit = performance.now();

                    beep(false);

                    if (f.active) {

                        // IMPULSO MODERADO
                        vy = -9;

                        vx = f.side === 'L'
                            ? (ball.x - gL) * 0.06 + 2.5
                            : (ball.x - gR) * 0.06 - 2.5;

                    } else {

                        vy = -Math.abs(vy) * 0.85;

                        vx = f.side === 'L'
                            ? Math.abs(vx) * 0.8 + 1
                            : -Math.abs(vx) * 0.8 - 1;
                    }

                    ball.x += f.side === 'L' ? 2 : -2;
                    ball.y -= 5;

                    touched = true;

                    break;
                }
            }
        }

        // GAME OVER
        if (
            arena &&
            ball.y > endY + r &&
            !touched
        ) {

            if (ball.x > gL && ball.x < gR) {

                active = false;
                launched = false;

                vx = 0;
                vy = 0;

                status.textContent =
                    `GAME OVER! PONTOS: ${score} | RECORDE: ${record} — reinicie`;

            } else {

                vy = -3.5;

                vx = ball.x < W / 2
                    ? 1.5
                    : -1.5;

                ball.y -= 12;
            }
        }
    }

    draw();

    // MANTER ANIMAÇÃO FUNCIONANDO
    raf = requestAnimationFrame(tick);
}

// CONTROLES POR TOQUE
function hold(id, down, up) {

    const b = document.getElementById(id);

    b.addEventListener('pointerdown', e => {

        e.preventDefault();

        b.setPointerCapture?.(e.pointerId);

        down();

        b.classList.add('pressed');
    });

    for (const ev of [
        'pointerup',
        'pointercancel',
        'lostpointercapture'
    ]) {

        b.addEventListener(ev, () => {

            up();

            b.classList.remove('pressed');
        });
    }
}

hold(
    'left',
    () => {
        leftOn = true;
        beep();
    },
    () => {
        leftOn = false;
    }
);

hold(
    'right',
    () => {
        rightOn = true;
        beep();
    },
    () => {
        rightOn = false;
    }
);

// BOTÃO LANÇAR
document.getElementById('launch')
.addEventListener('click', start);

// BOTÃO REINICIAR
document.getElementById('restart')
.addEventListener('click', reset);

// TECLADO
window.addEventListener('keydown', e => {

    if ([
        'ArrowLeft',
        'ArrowRight',
        'ArrowUp',
        ' '
    ].includes(e.key)) {

        e.preventDefault();
    }

    if (e.key === 'ArrowLeft') {
        leftOn = true;
    }

    if (e.key === 'ArrowRight') {
        rightOn = true;
    }

    if (e.key === ' ' || e.key === 'ArrowUp') {
        start();
    }

    if (e.key === 'Escape') {
        reset();
    }
});

window.addEventListener('keyup', e => {

    if (e.key === 'ArrowLeft') {
        leftOn = false;
    }

    if (e.key === 'ArrowRight') {
        rightOn = false;
    }
});

// AJUSTAR TELA
window.addEventListener('resize', resize);

// INICIAR
updateStatus();
resize();

cancelAnimationFrame(raf);
raf = requestAnimationFrame(tick);

})();
</script>

</body>
</html>
