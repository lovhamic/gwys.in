const canvas = document.getElementById('plotCanvas');
const ctx = canvas.getContext('2d');

let view = { offsetX: 0, offsetY: 0, scaleX: 50, scaleY: 50 };
let t = 0;
let animationId = null;
const COLORS = ['#58a6ff', '#7ee787', '#d2a8ff', '#ff7b72', '#f2cc60']; 

window.onload = () => {
    // Default setup: A*sin(x - t)
    addEquation("A * sin(x - t)"); 
    addVariable("A", 1, 0, 5); // Now editable!
    resize();
    setTimeout(() => {
        const loader = document.getElementById('loader');
        if(loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 800);
        }
    }, 1000);
};

// --- UPDATED: EDITABLE VARIABLES ---
function addVariable(name="k", val=1, min=0, max=10) {
    const div = document.createElement('div');
    div.className = 'item-row var-row';
    div.innerHTML = `
        <input type="text" class="var-name" value="${name}" 
               style="width:30px; color:#58a6ff; background:transparent; border:none; font-family:'JetBrains Mono'; font-weight:bold;" 
               oninput="manualPlot()" placeholder="name">
        <input type="range" min="${min}" max="${max}" step="0.1" value="${val}" oninput="syncVal(this)">
        <input type="text" class="var-val" value="${val}" style="width:40px; text-align:right;" onchange="syncSlider(this)">
        <button class="btn-del" onclick="removeItem(this)">x</button>
    `;
    document.getElementById('var-list').appendChild(div);
    manualPlot();
}

function getParams() {
    let params = `t=${t}`;
    document.querySelectorAll('.eq-input').forEach((input, index) => {
        params += `&eq${index}=${encodeURIComponent(input.value)}`;
    });
    
    // UPDATED: Get the name from the input field instead of a span
    document.querySelectorAll('.var-row').forEach(row => {
        const name = row.querySelector('.var-name').value.trim();
        const val = row.querySelector('.var-val').value;
        if(name) params += `&${encodeURIComponent(name)}=${val}`;
    });
    
    const cx = canvas.width/2 + view.offsetX;
    params += `&minX=${-cx / view.scaleX}&maxX=${(canvas.width - cx) / view.scaleX}`;
    return params;
}

// ... (Keep the rest of your drawGrid, updateAndDraw, and Event functions) ...

async function updateAndDraw() {
    const url = `/calculate_wave?${getParams()}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data.error) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if(document.getElementById('grid-mode').checked) drawGrid();
        const cx = canvas.width/2 + view.offsetX;
        const cy = canvas.height/2 + view.offsetY;
        const showSuper = document.getElementById('superposition-mode').checked;
        data.lines.forEach((lineY, index) => {
            ctx.beginPath();
            ctx.strokeStyle = COLORS[index % COLORS.length];
            ctx.lineWidth = showSuper ? 1 : 2;
            ctx.globalAlpha = showSuper ? 0.3 : 1.0;
            for (let i = 0; i < data.x.length; i++) {
                let px = cx + (data.x[i] * view.scaleX);
                let py = cy - (lineY[i] * view.scaleY);
                if (i===0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
            }
            ctx.stroke();
        });
        if (showSuper) {
            ctx.beginPath(); ctx.strokeStyle = "#fff"; ctx.lineWidth = 3;
            ctx.globalAlpha = 1.0; ctx.shadowBlur = 10; ctx.shadowColor = "#fff";
            for (let i = 0; i < data.x.length; i++) {
                let px = cx + (data.x[i] * view.scaleX);
                let py = cy - (data.superposition[i] * view.scaleY);
                if (i===0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
            }
            ctx.stroke(); ctx.shadowBlur = 0;
        }
    } catch (err) { console.error(err); }
}

function drawGrid() {
    const cx = canvas.width / 2 + view.offsetX;
    const cy = canvas.height / 2 + view.offsetY;
    ctx.lineWidth = 1; ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.font = "10px 'JetBrains Mono'"; ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    const minVisX = Math.floor(-cx / view.scaleX);
    const maxVisX = Math.ceil((canvas.width - cx) / view.scaleX);
    const minVisY = Math.floor(-(canvas.height - cy) / view.scaleY);
    const maxVisY = Math.ceil(cy / view.scaleY);
    ctx.beginPath();
    for (let x = minVisX; x <= maxVisX; x++) {
        const screenX = cx + (x * view.scaleX);
        ctx.moveTo(screenX, 0); ctx.lineTo(screenX, canvas.height);
        if (x !== 0) ctx.fillText(x, screenX, cy + 8);
    }
    for (let y = minVisY; y <= maxVisY; y++) {
        const screenY = cy - (y * view.scaleY);
        ctx.moveTo(0, screenY); ctx.lineTo(canvas.width, screenY);
        if (y !== 0) ctx.fillText(y, cx - 15, screenY + 4);
    }
    ctx.stroke();
    ctx.beginPath(); ctx.strokeStyle = "rgba(255, 255, 255, 0.4)"; ctx.lineWidth = 1.5;
    ctx.moveTo(0, cy); ctx.lineTo(canvas.width, cy);
    ctx.moveTo(cx, 0); ctx.lineTo(cx, canvas.height);
    ctx.stroke();
}

function addEquation(defaultValue = "") {
    const div = document.createElement('div');
    div.className = 'item-row eq-row-container';
    const color = COLORS[document.querySelectorAll('.eq-row-container').length % COLORS.length];
    div.innerHTML = `<div style="width:4px; height:20px; background:${color}; margin-right:5px;"></div>
        <input type="text" class="eq-input" value="${defaultValue}" placeholder="Equation" oninput="manualPlot()">
        <button class="btn-del" onclick="removeItem(this)">x</button>`;
    document.getElementById('eq-list').appendChild(div);
    manualPlot();
}

function removeItem(btn) { btn.parentElement.remove(); manualPlot(); }
function syncVal(slider) { slider.nextElementSibling.value = slider.value; manualPlot(); }
function syncSlider(box) { box.previousElementSibling.value = box.value; manualPlot(); }
function manualPlot() { updateAndDraw(); }
function toggleAnimation() { document.getElementById('animate-mode').checked ? loop() : cancelAnimationFrame(animationId); }
function loop() { t += 0.1; updateAndDraw().then(() => { if(document.getElementById('animate-mode').checked) animationId = requestAnimationFrame(loop); }); }
function resize() { canvas.width = window.innerWidth - 380; canvas.height = window.innerHeight; manualPlot(); }
canvas.onmousedown = e => { canvas.isDown = true; canvas.lastX = e.clientX; canvas.lastY = e.clientY; };
canvas.onmouseup = () => canvas.isDown = false;
canvas.onmousemove = e => {
    const rect = canvas.getBoundingClientRect();
    const cx = canvas.width/2 + view.offsetX; const cy = canvas.height/2 + view.offsetY;
    const mx = (e.clientX - rect.left - cx) / view.scaleX; const my = (cy - (e.clientY - rect.top)) / view.scaleY;
    document.getElementById('mouse-coord').innerText = `${mx.toFixed(2)}, ${my.toFixed(2)}`;
    if(!canvas.isDown) return;
    view.offsetX += e.clientX - canvas.lastX; view.offsetY += e.clientY - canvas.lastY;
    canvas.lastX = e.clientX; canvas.lastY = e.clientY; manualPlot();
};
canvas.onwheel = e => { e.preventDefault(); let f = e.deltaY > 0 ? 0.9 : 1.1; view.scaleX *= f; view.scaleY *= f; manualPlot(); };
window.onresize = resize;