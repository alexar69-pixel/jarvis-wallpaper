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

// --- ARC REACTOR 3D MODEL ---
const arcReactorGroup = new THREE.Group();
scene.add(arcReactorGroup);

// Helper to get CSS variable color
function getThemeColor(varName) {
    return parseInt(getComputedStyle(document.body).getPropertyValue(varName).trim().replace('#', '0x'));
}

// Materials
let baseColor = getThemeColor('--primary');
let dangerColor = getThemeColor('--danger');

const coreMaterial = new THREE.MeshBasicMaterial({ color: baseColor, transparent: true, opacity: 0.9 });
const wireMaterial = new THREE.MeshBasicMaterial({ color: baseColor, wireframe: true, transparent: true, opacity: 0.4 });
const darkMetal = new THREE.MeshBasicMaterial({ color: 0x333333, wireframe: true, transparent: true, opacity: 0.8 });

// 1. Core Sphere
const coreGeo = new THREE.SphereGeometry(0.8, 16, 16);
const coreMesh = new THREE.Mesh(coreGeo, coreMaterial);
arcReactorGroup.add(coreMesh);

// 2. Inner Ring
const innerRingGeo = new THREE.TorusGeometry(1.5, 0.2, 16, 32);
const innerRing = new THREE.Mesh(innerRingGeo, wireMaterial);
arcReactorGroup.add(innerRing);

// 3. Outer Ring
const outerRingGeo = new THREE.TorusGeometry(2.2, 0.1, 16, 64);
const outerRing = new THREE.Mesh(outerRingGeo, wireMaterial);
arcReactorGroup.add(outerRing);

// 4. Coils around the inner ring
const coilsGroup = new THREE.Group();
const coilGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.6, 8);
for(let i=0; i<10; i++) {
    const angle = (i / 10) * Math.PI * 2;
    const coil = new THREE.Mesh(coilGeo, darkMetal);
    coil.position.x = Math.cos(angle) * 1.5;
    coil.position.y = Math.sin(angle) * 1.5;
    coil.rotation.z = angle + Math.PI/2;
    coilsGroup.add(coil);
}
arcReactorGroup.add(coilsGroup);

// 5. Particles
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 300;
const posArray = new Float32Array(particlesCount * 3);
for(let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 8;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const particlesMaterial = new THREE.PointsMaterial({ size: 0.05, color: baseColor, transparent: true, opacity: 0.8 });
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

camera.position.z = 5;

// Animation Loop
function animate3D() {
    requestAnimationFrame(animate3D);
    
    // Base rotation
    arcReactorGroup.rotation.x += 0.005;
    arcReactorGroup.rotation.y += 0.005;
    coilsGroup.rotation.z -= 0.01;
    innerRing.rotation.z += 0.02;
    particlesMesh.rotation.y -= 0.002;
    
    // React to states
    if(orb.classList.contains('listening') || document.body.classList.contains('red-alert')) {
        coreMaterial.color.setHex(dangerColor);
        wireMaterial.color.setHex(dangerColor);
        particlesMaterial.color.setHex(dangerColor);
        arcReactorGroup.rotation.y += 0.04; // Spin much faster
        coilsGroup.rotation.z -= 0.06;
    } else if(orb.classList.contains('processing')) {
        coreMaterial.color.setHex(baseColor);
        wireMaterial.color.setHex(baseColor);
        particlesMaterial.color.setHex(baseColor);
        arcReactorGroup.rotation.x += 0.05; // Spin erratically
        coilsGroup.rotation.z -= 0.04;
    } else {
        // IDLE or SLEEP
        if(document.body.classList.contains('sleep-mode')) {
            coreMaterial.color.setHex(0x330000); // Dark red dormant
            wireMaterial.color.setHex(0x111111);
            particlesMaterial.color.setHex(0x000000);
        } else {
            coreMaterial.color.setHex(baseColor);
            wireMaterial.color.setHex(baseColor);
            particlesMaterial.color.setHex(baseColor);
        }
    }
    
    // Core pulsing effect
    const time = Date.now() * 0.005;
    coreMesh.scale.setScalar(1 + Math.sin(time) * 0.1);
    
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
                // Wake up from sleep if sleeping
                document.body.classList.remove('sleep-mode');
                setTimeout(() => {
                    statusText.classList.remove('cyan-text');
                    statusText.textContent = "SYSTEM ONLINE";
                }, 4000);
            } else if (data.type === "action") {
                if (data.value === "red_alert") {
                    document.body.classList.add("red-alert");
                } else if (data.value === "red_alert_off") {
                    document.body.classList.remove("red-alert");
                } else if (data.value === "sleep_mode") {
                    document.body.classList.add("sleep-mode");
                }
            } else if (data.type === "theme") {
                document.body.classList.remove("theme-gold", "theme-matrix", "theme-cyan");
                if (data.value && data.value !== "theme-cyan") {
                    document.body.classList.add(data.value);
                }
                setTimeout(() => {
                    baseColor = getThemeColor('--primary');
                    dangerColor = getThemeColor('--danger');
                }, 100);
            } else if (data.type === "shortcuts") {
                const container = document.getElementById("dynamic-shortcuts");
                if (container && data.shortcuts) {
                    container.innerHTML = "";
                    data.shortcuts.forEach(sc => {
                        const btn = document.createElement("button");
                        btn.className = "btn-launch";
                        btn.textContent = sc.name;
                        btn.onclick = () => launchApp(sc.name);
                        container.appendChild(btn);
                    });
                }
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
