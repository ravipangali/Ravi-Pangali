/**
 * Galaxy Theme
 * Three.js implementation for the galaxy background
 */

// Variables to track animation state
let galaxyScene = null;
let galaxyCamera = null;
let galaxyRenderer = null;
let galaxyAnimationId = null;
let isGalaxyAnimating = false;
let galaxyObjects = {
    galaxy: null,
    blockchainNodes: null,
    dataPackets: null,
    stars: null,
    floatingCode: null
};

/**
 * Initialize the galaxy scene
 */
function initGalaxyScene() {
    // If already initialized and animating, don't initialize again
    if (isGalaxyAnimating) return;
    
    const canvas = document.querySelector('#galaxy-canvas');
    if (!canvas) return;
    
    console.log('Initializing galaxy scene');
    
    // Create scene
    galaxyScene = new THREE.Scene();
    galaxyCamera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    galaxyRenderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    
    galaxyRenderer.setSize(window.innerWidth, window.innerHeight);
    galaxyRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    
    // Add soft ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    galaxyScene.add(ambientLight);
    
    // Add point light with a slight blue tint for blockchain nodes
    const pointLight = new THREE.PointLight(0x4d7cff, 0.8, 100);
    pointLight.position.set(0, 3, 5);
    galaxyScene.add(pointLight);
    
    // Create galaxy elements
    galaxyObjects.galaxy = createGalaxy();
    const nodeSystem = createBlockchainNodes();
    galaxyObjects.blockchainNodes = nodeSystem.nodeGroup;
    
    // Create data packets
    const connections = nodeSystem.connections;
    const nodePositions = nodeSystem.nodePositions;
    galaxyObjects.dataPackets = createDataPackets(nodePositions, connections);
    
    // Create stars
    galaxyObjects.stars = createStars();
    
    // Create floating code
    galaxyObjects.floatingCode = createFloatingCode();
    
    // Setup camera position
    galaxyCamera.position.set(0, 3, 10);
    
    // Handle window resize
    window.addEventListener('resize', () => {
        // Update camera aspect ratio
        galaxyCamera.aspect = window.innerWidth / window.innerHeight;
        galaxyCamera.updateProjectionMatrix();
        
        // Update renderer size
        galaxyRenderer.setSize(window.innerWidth, window.innerHeight);
        galaxyRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    });
    
    // Start animation
    startGalaxyAnimation();
}

/**
 * Start galaxy animation
 */
function startGalaxyAnimation() {
    if (isGalaxyAnimating) return;
    isGalaxyAnimating = true;
    
    const animate = () => {
        galaxyAnimationId = requestAnimationFrame(animate);
        
        // Rotate galaxy slowly
        if (galaxyObjects.galaxy) {
            galaxyObjects.galaxy.rotation.y += 0.0005;
        }
        
        // Rotate blockchain node system
        if (galaxyObjects.blockchainNodes) {
            galaxyObjects.blockchainNodes.rotation.y += 0.001;
        }
        
        // Animate data packets
        if (galaxyObjects.dataPackets) {
            for (const packet of galaxyObjects.dataPackets) {
                packet.moveStep();
                
                // If packet reaches destination, reset it
                if (packet.complete) {
                    packet.reset();
                }
            }
        }
        
        // Render scene
        if (galaxyRenderer && galaxyScene && galaxyCamera) {
            galaxyRenderer.render(galaxyScene, galaxyCamera);
        }
    };
    
    animate();
}

/**
 * Stop galaxy animation
 */
function stopGalaxyAnimation() {
    if (galaxyAnimationId !== null) {
        cancelAnimationFrame(galaxyAnimationId);
        galaxyAnimationId = null;
        isGalaxyAnimating = false;
    }
}

/**
 * Create galaxy particle system
 */
function createGalaxy() {
    // Parameters
    const parameters = {
        count: 20000,  // Reduced for better performance
        size: 0.01,
        radius: 8,
        branches: 5,
        spin: 1,
        randomness: 0.2,
        randomnessPower: 3,
        insideColor: 0x0066ff,
        outsideColor: 0x00ffff
    };

    // Galaxy geometry
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(parameters.count * 3);
    const colors = new Float32Array(parameters.count * 3);

    const colorInside = new THREE.Color(parameters.insideColor);
    const colorOutside = new THREE.Color(parameters.outsideColor);

    // Create galaxy points
    for (let i = 0; i < parameters.count; i++) {
        const i3 = i * 3;

        // Position
        const radius = Math.random() * parameters.radius;
        const spinAngle = radius * parameters.spin;
        const branchAngle = ((i % parameters.branches) / parameters.branches) * Math.PI * 2;

        const randomX = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius;
        const randomY = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius;
        const randomZ = Math.pow(Math.random(), parameters.randomnessPower) * (Math.random() < 0.5 ? 1 : -1) * parameters.randomness * radius;

        positions[i3] = Math.cos(branchAngle + spinAngle) * radius + randomX;
        positions[i3 + 1] = randomY;
        positions[i3 + 2] = Math.sin(branchAngle + spinAngle) * radius + randomZ;

        // Color
        const mixedColor = colorInside.clone();
        mixedColor.lerp(colorOutside, radius / parameters.radius);

        colors[i3] = mixedColor.r;
        colors[i3 + 1] = mixedColor.g;
        colors[i3 + 2] = mixedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Use simple PointsMaterial for better performance
    const material = new THREE.PointsMaterial({
        size: parameters.size,
        sizeAttenuation: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        vertexColors: true,
        transparent: true,
        opacity: 0.8
    });

    // Galaxy mesh
    const galaxy = new THREE.Points(geometry, material);
    galaxyScene.add(galaxy);

    return galaxy;
}

/**
 * Create blockchain nodes system
 */
function createBlockchainNodes() {
    const nodeCount = 50; // Number of blockchain nodes
    const nodeGroup = new THREE.Group();
    const nodes = [];
    const nodePositions = [];
    const connections = [];
    
    // Create nodes
    for (let i = 0; i < nodeCount; i++) {
        // Node geometry and material
        const nodeGeometry = new THREE.IcosahedronGeometry(0.08, 1);
        const nodeMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ffff,
            emissive: 0x00ffff,
            emissiveIntensity: 0.5,
            metalness: 0.8,
            roughness: 0.2
        });
        
        // Create the node mesh
        const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
        
        // Random position within a sphere
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos((Math.random() * 2) - 1);
        const radius = 3 + Math.random() * 3;
        
        const x = radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.sin(phi) * Math.sin(theta);
        const z = radius * Math.cos(phi);
        
        node.position.set(x, y, z);
        nodePositions.push({x, y, z});
        nodes.push(node);
        nodeGroup.add(node);
    }
    
    // Create connections between nodes (blockchain links)
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x0088ff,
        transparent: true,
        opacity: 0.3
    });
    
    // Connect each node to 2-4 nearest nodes
    for (let i = 0; i < nodeCount; i++) {
        const connectionsCount = 2 + Math.floor(Math.random() * 3); // 2-4 connections
        const distances = [];
        
        // Calculate distances to all other nodes
        for (let j = 0; j < nodeCount; j++) {
            if (i !== j) {
                const dist = Math.sqrt(
                    Math.pow(nodePositions[i].x - nodePositions[j].x, 2) +
                    Math.pow(nodePositions[i].y - nodePositions[j].y, 2) +
                    Math.pow(nodePositions[i].z - nodePositions[j].z, 2)
                );
                distances.push({index: j, distance: dist});
            }
        }
        
        // Sort by distance
        distances.sort((a, b) => a.distance - b.distance);
        
        // Connect to closest nodes
        for (let c = 0; c < Math.min(connectionsCount, distances.length); c++) {
            // Check if this connection already exists
            const j = distances[c].index;
            const connectionExists = connections.some(conn => 
                (conn.from === i && conn.to === j) || (conn.from === j && conn.to === i)
            );
            
            if (!connectionExists) {
                connections.push({from: i, to: j});
                
                // Create the line geometry
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(nodePositions[i].x, nodePositions[i].y, nodePositions[i].z),
                    new THREE.Vector3(nodePositions[j].x, nodePositions[j].y, nodePositions[j].z)
                ]);
                
                const line = new THREE.Line(lineGeometry, lineMaterial);
                nodeGroup.add(line);
            }
        }
    }
    
    galaxyScene.add(nodeGroup);
    return { nodeGroup, nodes, connections, nodePositions };
}

/**
 * Create data packets that travel along blockchain connections
 */
function createDataPackets(nodePositions, connections) {
    const packets = [];
    
    // Create data packet class
    class DataPacket {
        constructor(fromPos, toPos) {
            // Packet geometry and material
            const geometry = new THREE.SphereGeometry(0.04, 8, 8);
            const material = new THREE.MeshBasicMaterial({
                color: 0x00ffff,
                transparent: true,
                opacity: 0.8
            });
            
            this.mesh = new THREE.Mesh(geometry, material);
            this.fromPos = fromPos;
            this.toPos = toPos;
            this.progress = 0;
            this.speed = 0.005 + Math.random() * 0.01; // Random speed
            this.complete = false;
            this.active = false;
            this.startDelay = Math.random() * 10; // Random delay before starting
            
            // Hide initially
            this.mesh.visible = false;
            
            // Add to scene
            galaxyScene.add(this.mesh);
        }
        
        moveStep() {
            if (this.startDelay > 0) {
                this.startDelay -= 0.1;
                return;
            }
            
            if (!this.active) {
                this.mesh.visible = true;
                this.active = true;
            }
            
            this.progress += this.speed;
            
            if (this.progress >= 1) {
                this.complete = true;
                this.mesh.visible = false;
                return;
            }
            
            // Linear interpolation between from and to positions
            this.mesh.position.x = this.fromPos.x + (this.toPos.x - this.fromPos.x) * this.progress;
            this.mesh.position.y = this.fromPos.y + (this.toPos.y - this.fromPos.y) * this.progress;
            this.mesh.position.z = this.fromPos.z + (this.toPos.z - this.fromPos.z) * this.progress;
        }
        
        reset() {
            this.progress = 0;
            this.complete = false;
            this.active = false;
            this.mesh.visible = false;
            this.startDelay = Math.random() * 10;
        }
    }
    
    // Create packets for some of the connections
    const packetCount = Math.min(connections.length, 30); // Limit to 30 packets max
    
    for (let i = 0; i < packetCount; i++) {
        const conn = connections[i];
        const fromPos = nodePositions[conn.from];
        const toPos = nodePositions[conn.to];
        
        const packet = new DataPacket(fromPos, toPos);
        packets.push(packet);
    }
    
    return packets;
}

/**
 * Create floating code elements
 */
function createFloatingCode() {
    // Code snippets for the floating code elements
    const codeSnippets = [
        "function createGalaxy() {",
        "const data = blockchain.getData();",
        "if (isValid(hash)) {",
        "class GalaxyNode extends Node {",
        "const stars = new Array(1000);",
        "return Promise.resolve(data);",
        "for (let i = 0; i < nodes.length; i++) {",
        "async function processBlock() {",
        "const position = new Vector3();",
        "import * as THREE from 'three';",
        "const scene = new THREE.Scene();"
    ];
    
    const codeElements = [];
    const container = document.createElement('div');
    container.className = 'absolute inset-0 overflow-hidden pointer-events-none';
    document.getElementById('galaxy-background').appendChild(container);

    // Create 15 floating code elements
    for (let i = 0; i < 15; i++) {
        const codeEl = document.createElement('div');
        codeEl.className = 'code-particle';
        codeEl.textContent = codeSnippets[i % codeSnippets.length];
        
        // Random starting position
        const x = Math.random() * 100; // percentage
        const y = Math.random() * 100; // percentage
        const delay = Math.random() * 15; // seconds
        const duration = 15 + Math.random() * 20; // seconds
        
        codeEl.style.left = `${x}%`;
        codeEl.style.top = `${y}%`;
        codeEl.style.opacity = '0';
        
        // Animation with CSS
        codeEl.style.animation = `
            floatingCode ${duration}s linear ${delay}s infinite
        `;
        
        container.appendChild(codeEl);
        codeElements.push(codeEl);
    }
    
    // Add keyframes for the animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatingCode {
            0% {
                opacity: 0;
                transform: translateY(0) translateX(0);
            }
            10% {
                opacity: 0.7;
            }
            90% {
                opacity: 0.7;
            }
            100% {
                opacity: 0;
                transform: translateY(-70vh) translateX(var(--tx, 0));
            }
        }
    `;
    document.head.appendChild(style);
    
    // Set random horizontal drift for each element
    codeElements.forEach(el => {
        const drift = (Math.random() - 0.5) * 20; // -10vw to 10vw
        el.style.setProperty('--tx', `${drift}vw`);
    });
    
    return { container, elements: codeElements };
}

/**
 * Create star elements with explosion effect
 */
function createStars() {
    // Create stars container if it doesn't already exist
    let starsContainer = document.querySelector('.stars-container');
    if (!starsContainer) {
        starsContainer = document.createElement('div');
        starsContainer.className = 'stars-container';
        document.getElementById('galaxy-background').appendChild(starsContainer);
    }
    
    // Add stars
    const count = 100;
    const stars = [];
    
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        
        // Random position
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        
        star.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background-color: #fff;
            border-radius: 50%;
            left: ${x}%;
            top: ${y}%;
            opacity: ${0.3 + Math.random() * 0.7};
            box-shadow: 0 0 ${3 + Math.random() * 4}px #fff;
        `;
        
        // Add random animation for twinkling
        const duration = 3 + Math.random() * 7;
        star.style.animation = `twinkle ${duration}s infinite ${Math.random() * duration}s`;
        
        starsContainer.appendChild(star);
        stars.push(star);
        
        // Add occasional star explosion effect
        if (Math.random() < 0.2) { // 20% chance each star will explode
            setTimeout(() => {
                createStarExplosion(x, y);
            }, Math.random() * 10000); // Random delay up to 10 seconds
        }
    }
    
    // Add keyframes for twinkling effect
    const twinkleStyle = document.createElement('style');
    twinkleStyle.textContent = `
        @keyframes twinkle {
            0%, 100% {
                opacity: 0.3;
            }
            50% {
                opacity: 1;
            }
        }
        
        @keyframes explode {
            0% {
                width: 2px;
                height: 2px;
                opacity: 1;
            }
            100% {
                width: 30px;
                height: 30px;
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(twinkleStyle);
    
    return { container: starsContainer, stars };
}

/**
 * Create star explosion effect
 */
function createStarExplosion(x, y) {
    const explosion = document.createElement('div');
    explosion.className = 'star-explosion';
    explosion.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(59,130,246,0.5) 50%, transparent 100%);
        border-radius: 50%;
        left: ${x}%;
        top: ${y}%;
        transform: translate(-50%, -50%);
        z-index: 1;
        animation: explode 2s forwards;
    `;
    
    document.querySelector('.stars-container').appendChild(explosion);
    
    // Create particles for the explosion
    const particleCount = 8 + Math.floor(Math.random() * 8); // 8-15 particles
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        const angle = (i / particleCount) * Math.PI * 2;
        const distance = 10 + Math.random() * 20;
        
        particle.className = 'star-particle';
        particle.style.cssText = `
            position: absolute;
            width: 1px;
            height: 1px;
            background-color: #fff;
            left: ${x}%;
            top: ${y}%;
            box-shadow: 0 0 2px #fff;
            opacity: 1;
            z-index: 2;
        `;
        
        // Create unique animation for each particle
        const keyframes = `
            @keyframes particle-${x}-${y}-${i} {
                0% {
                    opacity: 1;
                    transform: translate(-50%, -50%) rotate(${angle}rad) translateX(0);
                }
                100% {
                    opacity: 0;
                    transform: translate(-50%, -50%) rotate(${angle}rad) translateX(${distance}px);
                }
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = keyframes;
        document.head.appendChild(style);
        
        particle.style.animation = `particle-${x}-${y}-${i} 1.5s forwards`;
        
        document.querySelector('.stars-container').appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 1500);
    }
    
    // Remove explosion element after animation
    setTimeout(() => {
        if (explosion.parentNode) {
            explosion.parentNode.removeChild(explosion);
        }
    }, 2000);
}

// Make necessary functions globally available
window.initGalaxyScene = initGalaxyScene;
window.stopGalaxyAnimation = stopGalaxyAnimation; 