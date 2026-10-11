<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Super Pinball Arcade</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#111;font-family:Arial,sans-serif;touch-action:manipulation}
#app{height:100dvh;display:flex;flex-direction:column;background:#dcdcdc}
#top{color:#fff;background:#151515;text-align:center;padding:6px;font-weight:bold;font-size:14px}
#game{display:block;width:100%;flex:1;min-height:0;background:#05070b;touch-action:none}
#controls{display:grid;grid-template-columns:1fr 1.2fr 1fr;gap:7px;padding:8px;background:#e5e5e5}
button{border:3px solid #555;border-radius:10px;background:#fff;color:#37474f;font-weight:bold;font-size:clamp(11px,2.8vw,16px);min-height:62px;padding:8px 3px;touch-action:none}
#launch{background:#4caf50;color:white;border-color:#2e7d32}
#restart{position:absolute;top:42px;right:8px;z-index:2;border:0;border-radius:6px;background:#ff5252;color:#fff;min-height:0;padding:8px 12px;font-size:14px}
button:active,.pressed{filter:brightness(.78);transform:scale(.99)}
@media (min-width:800px){#controls{padding:10px 12%;gap:14px}button{min-height:70px;font-size:16px}#top{font-size:16px}}
</style>
</head>
<body>
<div id="app">
  <div id="top">SUPER PINBALL ARCADE</div>
  <canvas id="game"></canvas>
  <button id="restart">REINICIAR ↻</button>
  <div id="controls">
    <button id="left">← SETA ESQ.<br>PALHETA ESQ.</button>
    <button id="launch">▲ ESPAÇO ▲<br>LANÇAR BOLA</button>
    <button id="right">SETA DIR. →<br>PALHETA DIR.</button>
  </div>
</div>
<script>
(() => {
const canvas=document.getElementById('game'), ctx=canvas.getContext('2d');
const status=document.getElementById('top');
let W=0,H=0,util=0,r=11,grav=.42,ball={x:0,y:0},vx=0,vy=0,score=0,record=Number(localStorage.getItem('pinballRecord')||0);
let launched=false,arena=false,active=true,leftOn=false,rightOn=false,raf=0,last=0;
let obstacles=[],flippers=[];
function beep(high=false){try{const a=new (window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator(),g=a.createGain();o.frequency.value=high?880:587;g.gain.value=.035;o.connect(g);g.connect(a.destination);o.start();o.stop(a.currentTime+.055);o.onended=()=>a.close()}catch(e){}}
function resize(){
 const dpr=Math.min(devicePixelRatio||1,2),rect=canvas.getBoundingClientRect();
 W=rect.width;H=rect.height;canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
 util=W- Math.max(42,W*.045);r=Math.max(5,Math.min(12,W*.014));
 setup();
}
function setup(){
 const bumpR=Math.max(13,W*.038);
 obstacles=[
 {x:util*.30,y:H*.25,rad:bumpR,color:'#00e5ff',points:10,impulse:1.18,high:false},
 {x:util*.70,y:H*.25,rad:bumpR,color:'#00e5ff',points:10,impulse:1.18,high:false},
 {x:util*.50,y:H*.38,rad:bumpR,color:'#e040fb',points:10,impulse:1.18,high:false},
 {x:util*.15,y:H*.12,rad:bumpR,color:'#ffd700',points:30,impulse:1.22,high:true,star:true},
 {x:util*.50,y:H*.10,rad:bumpR,color:'#ffd700',points:30,impulse:1.22,high:true,star:true},
 {x:util*.85,y:H*.12,rad:bumpR,color:'#ffd700',points:30,impulse:1.22,high:true,star:true},
 {x:util*.20,y:H*.52,rad:bumpR,color:'#ff1744',points:50,impulse:1.35,high:true,diamond:true},
 {x:util*.80,y:H*.52,rad:bumpR,color:'#ff1744',points:50,impulse:1.35,high:true,diamond:true}
 ];
 ball={x:W-25,y:H-45};vx=vy=0;flippers=[];
}
function start(){if(!active){reset();return}if(!launched){beep(true);vx=0;vy=-Math.sqrt(2*grav*(H-50))-5.5;launched=true;arena=false;}}
function reset(){score=0;active=true;launched=false;arena=false;leftOn=rightOn=false;ball={x:W-25,y:H-45};vx=vy=0;updateStatus();draw();}
function updateStatus(){status.textContent=`PONTOS: ${score} | RECORDE: ${record}`;}
function geometry(){
 const y=H*.99, gapL=util*.33,gapR=util*.67,len=util*.15;
 const aL=leftOn?-22:16,aR=rightOn?202:164;
 const radL=aL*Math.PI/180,radR=aR*Math.PI/180;
 flippers=[
 {x1:gapL,y1:y,x2:gapL+Math.cos(radL)*len,y2:y+Math.sin(radL)*len,active:leftOn,side:'L'},
 {x1:gapR,y1:y,x2:gapR+Math.cos(radR)*len,y2:y+Math.sin(radR)*len,active:rightOn,side:'R'}
 ];
}
function lineHit(f,x,y){let dx=f.x2-f.x1,dy=f.y2-f.y1,u=((x-f.x1)*dx+(y-f.y1)*dy)/(dx*dx+dy*dy||1);u=Math.max(0,Math.min(1,u));return Math.hypot(x-(f.x1+u*dx),y-(f.y1+u*dy))<r+8}
function draw(){
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#05070b';ctx.fillRect(0,0,W,H);
 const startY=H*.60,endY=H*.99,gL=util*.33,gR=util*.67;
 // launcher lane and frame
 ctx.strokeStyle='#858585';ctx.lineWidth=3;ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(util,65);ctx.lineTo(util,H);ctx.stroke();ctx.setLineDash([]);
 ctx.strokeStyle='yellow';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(util,45);ctx.lineTo(W,0);ctx.stroke();
 for(let i=0;i<3;i++){ctx.fillStyle='#00ff00';ctx.font='bold 26px Arial';ctx.textAlign='center';ctx.fillText('▲',W-22,H*.22+i*H*.19)}
 // funnel walls
 ctx.fillStyle='#1e1e1e';ctx.strokeStyle='yellow';ctx.lineWidth=3;
 ctx.beginPath();ctx.moveTo(0,startY);ctx.lineTo(gL,endY);ctx.lineTo(0,endY);ctx.closePath();ctx.fill();ctx.stroke();
 ctx.beginPath();ctx.moveTo(util,startY);ctx.lineTo(gR,endY);ctx.lineTo(util,endY);ctx.closePath();ctx.fill();ctx.stroke();
 for(const o of obstacles){
  ctx.beginPath();ctx.arc(o.x,o.y,o.rad,0,Math.PI*2);ctx.fillStyle=o.star?'#222':o.color;ctx.fill();ctx.lineWidth=o.star?3:2;ctx.strokeStyle=o.star?o.color:'#fff';ctx.stroke();
  ctx.fillStyle='#fff';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`bold ${o.star?20:o.diamond?22:16}px Arial`;ctx.fillText(o.star?'★':o.diamond?'♦':'●',o.x,o.y);
 }
 geometry();
 for(const f of flippers){
  ctx.fillStyle='#ef5350';ctx.strokeStyle='#b71c1c';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(f.x1,f.y1-6);ctx.lineTo(f.x1,f.y1+34);ctx.lineTo(f.x1+(f.side==='L'?12:-12),f.y1+34);ctx.lineTo(f.x2,f.y2);ctx.closePath();ctx.fill();ctx.stroke();
 }
 // ball
 ctx.beginPath();ctx.arc(ball.x,ball.y,r,0,Math.PI*2);ctx.fillStyle='#f5f5f5';ctx.fill();ctx.lineWidth=2;ctx.strokeStyle='#b0b0b0';ctx.stroke();
 if(!active){ctx.fillStyle='rgba(0,0,0,.72)';ctx.fillRect(0,0,W,H);ctx.fillStyle='#fff';ctx.textAlign='center';ctx.font='bold 25px Arial';ctx.fillText('GAME OVER',W/2,H/2-12);ctx.font='bold 15px Arial';ctx.fillText('Toque em REINICIAR ou LANÇAR BOLA',W/2,H/2+18)}
}
function tick(t){
 if(!active){draw();return}
 if(launched){
  vy+=grav;vx=Math.max(-22,Math.min(22,vx));vy=Math.max(-38,Math.min(38,vy));ball.x+=vx;ball.y+=vy;
  if(!arena){if(ball.x>=util&&ball.y<=110){vx=-17.5;vy=3.5;arena=true;ball.x-=20;ball.y+=15}}
  else if(ball.x-r<util&&ball.x+r>=util&&ball.y>35){vx=-Math.abs(vx);ball.x-=4}
  if(ball.x-r<=0){vx=Math.abs(vx)*1.01;ball.x=r+2}else if(ball.x+r>=W){vx=-Math.abs(vx)*1.01;ball.x=W-r-2}
  if(ball.y-r<=0){vy=Math.abs(vy)*.85;ball.y=r+2}
  const startY=H*.60,endY=H*.99,gL=util*.33,gR=util*.67;
  if(arena&&ball.y>=startY&&ball.y<=endY){
   if(ball.x<=gL){let prop=ball.x/gL,lim=startY+(endY-startY)*prop;if(ball.y+r>=lim-4){vx=Math.abs(vx)*.4+4.5;vy=Math.abs(vy)*.5+3;ball.x+=3;ball.y+=2}}
   else if(ball.x>=gR&&ball.x<util){let prop=(util-ball.x)/(util-gR),lim=startY+(endY-startY)*prop;if(ball.y+r>=lim-4){vx=-Math.abs(vx)*.4-4.5;vy=Math.abs(vy)*.5+3;ball.x-=3;ball.y+=2}}
  }
  for(const o of obstacles){if(Math.hypot(ball.x-o.x,ball.y-o.y)<o.rad+r){beep(o.high);vy=-vy*o.impulse;vx+=(ball.x-o.x)*.45;score+=o.points;if(score>record){record=score;localStorage.setItem('pinballRecord',record)}updateStatus();ball.x+=vx*1.05;ball.y+=vy*1.05}}
  geometry();let touched=false;
  if(arena){for(const f of flippers){if(lineHit(f,ball.x,ball.y)){beep(false);if(f.active){vy=-38;vx=f.side==='L'?(ball.x-gL)*.15+6:(ball.x-gR)*.15-6}else{vy=-Math.abs(vy)*1.45;vx=f.side==='L'?Math.abs(vx)*1.1+3:-Math.abs(vx)*1.1-3}ball.x+=f.side==='L'?2:-2;ball.y-=22;touched=true;break}}}
  if(arena&&ball.y>endY+r&&!touched){if(ball.x>gL&&ball.x<gR){active=false;status.textContent=`GAME OVER! PONTOS: ${score} | RECORDE: ${record} — reinicie`;}else{vy=-8;vx=ball.x<W/2?4:-4;ball.y-=20}}
 }
 draw();raf=requestAnimationFrame(tick);
}
function hold(id,down,up){const b=document.getElementById(id);b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture?.(e.pointerId);down();b.classList.add('pressed')});for(const ev of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(ev,e=>{up();b.classList.remove('pressed')})}
hold('left',()=>{leftOn=true;beep();},()=>leftOn=false);
hold('right',()=>{rightOn=true;beep();},()=>rightOn=false);
document.getElementById('launch').addEventListener('click',start);
document.getElementById('restart').addEventListener('click',reset);
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp',' '].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft')leftOn=true;if(e.key==='ArrowRight')rightOn=true;if(e.key===' '||e.key==='ArrowUp')start();if(e.key==='Escape')reset()});
window.addEventListener('keyup',e=>{if(e.key==='ArrowLeft')leftOn=false;if(e.key==='ArrowRight')rightOn=false});
window.addEventListener('resize',resize);
updateStatus();resize();cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);
})();
</script>
</body>
</html>
