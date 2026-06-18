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

// --- 3D Hologram Core (Three.js) ---
const container3D = document.getElementById('three-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 500 / 500, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(500, 500);
container3D.appendChild(renderer.domElement);

// Create Hologram Geometry (Icosahedron)
const geometry = new THREE.IcosahedronGeometry(2.5, 1);
const material = new THREE.MeshBasicMaterial({ 
    color: 0x00e5ff, 
    wireframe: true, 
    transparent: true, 
    opacity: 0.3 
});
const hologram = new THREE.Mesh(geometry, material);
scene.add(hologram);

// Create Particles
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 200;
const posArray = new Float32Array(particlesCount * 3);
for(let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 8;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const particlesMaterial = new THREE.PointsMaterial({
    size: 0.05,
    color: 0x00e5ff,
    transparent: true,
    opacity: 0.8
});
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

camera.position.z = 5;

// GLTF Loader (Commented out for future Sketchfab models)
/*
const loader = new THREE.GLTFLoader();
loader.load('tu_modelo_sketchfab.glb', function(gltf) {
    scene.add(gltf.scene);
    hologram.visible = false; // Hide default hologram
    particlesMesh.visible = false;
}, undefined, function(error) {
    console.error(error);
});
*/

function animate3D() {
    requestAnimationFrame(animate3D);
    
    // Base rotation
    hologram.rotation.x += 0.005;
    hologram.rotation.y += 0.005;
    particlesMesh.rotation.y -= 0.002;
    
    // React to states
    if(orb.classList.contains('listening')) {
        material.color.setHex(0xff0055);
        particlesMaterial.color.setHex(0xff0055);
        hologram.rotation.y += 0.02; // Spin faster
    } else if(orb.classList.contains('processing')) {
        material.color.setHex(0xa200ff);
        particlesMaterial.color.setHex(0xa200ff);
        hologram.rotation.x += 0.05; // Spin erratically
    } else {
        material.color.setHex(0x00e5ff);
        particlesMaterial.color.setHex(0x00e5ff);
    }
    
    renderer.render(scene, camera);
}
animate3D();
// ----------------------------------

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
            } else if (data.type === "media") {
                const mediaContainer = document.getElementById('media-panel-container');
                const mediaTitle = document.getElementById('media-title');
                const mediaArtist = document.getElementById('media-artist');
                
                if (data.title) {
                    mediaTitle.textContent = data.title;
                    mediaArtist.textContent = data.artist || '';
                    mediaContainer.style.display = 'block';
                } else {
                    mediaContainer.style.display = 'none';
                }
            } else if (data.type === "face_detected") {
                const statusText = document.getElementById('status-text');
                statusText.textContent = "USER DETECTED";
                statusText.classList.add('cyan-text');
                setTimeout(() => {
                    statusText.classList.remove('cyan-text');
                    statusText.textContent = "SYSTEM ONLINE";
                }, 4000);
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
