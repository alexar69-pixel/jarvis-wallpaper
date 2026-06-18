const orb = document.getElementById('jarvis-orb');
const statusText = document.getElementById('status-text');
const responseText = document.getElementById('current-response');

// Telemetry elements
const cpuBar = document.getElementById('cpu-bar');
const cpuVal = document.getElementById('cpu-val');
const ramBar = document.getElementById('ram-bar');
const ramVal = document.getElementById('ram-val');
const diskBar = document.getElementById('disk-bar');
const diskVal = document.getElementById('disk-val');

const timeDisplay = document.getElementById('time-display');
const dateDisplay = document.getElementById('date-display');
const weatherTemp = document.getElementById('weather-temp');
const weatherDesc = document.getElementById('weather-desc');
const weatherLoc = document.getElementById('weather-loc');

// Clock logic
setInterval(() => {
    const now = new Date();
    timeDisplay.innerText = now.toLocaleTimeString('en-US', { hour12: false });
    dateDisplay.innerText = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).toUpperCase();
}, 1000);

// Neural Network Canvas Animation
const canvas = document.getElementById('neural-canvas');
const ctx = canvas.getContext('2d');
canvas.width = 500;
canvas.height = 500;

const particles = [];
const numParticles = 60;

for(let i = 0; i < numParticles; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5
    });
}

function drawNeuralNet() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Determine color based on state
    let strokeColor = 'rgba(0, 229, 255, 0.15)'; // Cyan (IDLE)
    if(orb.classList.contains('listening')) strokeColor = 'rgba(255, 0, 85, 0.15)'; // Red
    else if(orb.classList.contains('processing')) strokeColor = 'rgba(162, 0, 255, 0.15)'; // Purple
    
    for(let i = 0; i < numParticles; i++) {
        let p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        
        if(p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if(p.y < 0 || p.y > canvas.height) p.vy *= -1;
        
        for(let j = i + 1; j < numParticles; j++) {
            let p2 = particles[j];
            let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
            if(dist < 80) {
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(drawNeuralNet);
}
drawNeuralNet();

// State definitions
const STATES = {
    IDLE: { class: '', status: 'SYSTEM ONLINE' },
    LISTENING: { class: 'listening', status: 'LISTENING...' },
    PROCESSING: { class: 'processing', status: 'PROCESSING...' },
    SPEAKING: { class: 'speaking', status: 'SPEAKING...' } // Add 'speaking' class
};

// Audio Wave Animation inside the core
const waveCanvas = document.getElementById('wave-canvas');
const waveCtx = waveCanvas.getContext('2d');
waveCanvas.width = 150;
waveCanvas.height = 150;

let waveOffset = 0;
function drawWave() {
    waveCtx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);
    
    if(orb.classList.contains('speaking')) {
        waveCtx.beginPath();
        waveCtx.moveTo(0, waveCanvas.height / 2);
        
        for(let i = 0; i < waveCanvas.width; i++) {
            // Complex sine wave
            let amplitude = 20 + Math.random() * 15; // Random fluctuation
            let y = waveCanvas.height / 2 + Math.sin(i * 0.05 + waveOffset) * amplitude * Math.sin(i * 0.02);
            waveCtx.lineTo(i, y);
        }
        
        waveCtx.strokeStyle = 'rgba(0, 229, 255, 0.8)';
        waveCtx.lineWidth = 3;
        waveCtx.stroke();
        
        // Add a secondary wave
        waveCtx.beginPath();
        waveCtx.moveTo(0, waveCanvas.height / 2);
        for(let i = 0; i < waveCanvas.width; i++) {
            let amplitude = 10 + Math.random() * 10;
            let y = waveCanvas.height / 2 + Math.cos(i * 0.08 - waveOffset) * amplitude;
            waveCtx.lineTo(i, y);
        }
        waveCtx.strokeStyle = 'rgba(0, 229, 255, 0.4)';
        waveCtx.lineWidth = 2;
        waveCtx.stroke();
        
        waveOffset += 0.2;
    }
    
    requestAnimationFrame(drawWave);
}
drawWave();

let socket;

function connectWebSocket() {
    socket = new WebSocket('ws://127.0.0.1:8765');

    socket.onopen = () => {
        setState('IDLE');
        updateMessage("Conexión con el núcleo establecida.");
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'state') {
                setState(data.state);
            } else if (data.type === 'message') {
                updateMessage(data.text);
            } else if (data.type === 'telemetry') {
                updateTelemetry(data);
            }
        } catch (e) {
            console.error("Error parsing message", e);
        }
    };

    socket.onclose = () => {
        setState('IDLE');
        updateMessage("Conexión perdida. Reintentando...");
        setTimeout(connectWebSocket, 5000);
    };
}

function setState(stateName) {
    const state = STATES[stateName] || STATES.IDLE;
    orb.className = 'reactor ' + state.class;
    statusText.innerText = state.status;
    
    if(stateName === 'LISTENING') statusText.style.color = '#ff0055';
    else if (stateName === 'PROCESSING') statusText.style.color = '#a200ff';
    else statusText.style.color = 'var(--cyan)';
}

function updateMessage(text) {
    responseText.innerText = text;
}

function updateTelemetry(data) {
    // System stats
    if (data.cpu !== undefined) {
        cpuBar.style.width = data.cpu + '%';
        cpuVal.innerText = Math.round(data.cpu) + '%';
    }
    if (data.ram !== undefined) {
        ramBar.style.width = data.ram + '%';
        ramVal.innerText = Math.round(data.ram) + '%';
    }
    if (data.disk !== undefined) {
        diskBar.style.width = data.disk + '%';
        diskVal.innerText = Math.round(data.disk) + '%';
    }
    
    // Weather stats
    if (data.weather) {
        weatherTemp.innerText = data.weather.temp + '°C';
        weatherDesc.innerText = data.weather.desc;
        weatherLoc.innerText = data.weather.location.toUpperCase();
    }
}

// App Launch Actions
window.launchApp = function(appName) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'action',
            action: 'launch_app',
            app: appName
        }));
        updateMessage(`Iniciando protocolo: ${appName.toUpperCase()}...`);
    } else {
        updateMessage("Error: Sin conexión al núcleo.");
    }
};

connectWebSocket();
