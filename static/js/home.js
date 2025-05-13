// Hero Section Animation
document.addEventListener('DOMContentLoaded', () => {
    // Hero Particle Effect
    const heroParticles = document.getElementById('hero-particles');
    if (heroParticles) {
        createHeroParticles(heroParticles);
    }
    
    // Initialize Three.js scene
    const canvas = document.querySelector('#galaxy-canvas');
    if (!canvas) return;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    
    // Add soft ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambientLight);
    
    // Add point light with a slight blue tint for blockchain nodes
    const pointLight = new THREE.PointLight(0x4d7cff, 0.8, 100);
    pointLight.position.set(0, 3, 5);
    scene.add(pointLight);

    // Create galaxy particle system
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
        scene.add(galaxy);

        return galaxy;
    }

    // Create blockchain nodes system
    function createBlockchainNodes() {
        const nodeCount = 50; // Number of blockchain nodes
        const nodeGroup = new THREE.Group();
        const nodes = [];
        const nodePositions = [];
        
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
        const connections = [];
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
        
        scene.add(nodeGroup);
        return { nodeGroup, nodes };
    }
    
    // Create data packets that travel along blockchain connections
    function createDataPackets(nodePositions, connections) {
        const packetGroup = new THREE.Group();
        const packetMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.8
        });
        
        const packets = [];
        
        // Create several data packets
        for (let i = 0; i < 15; i++) {
            // Select a random connection
            const connectionIndex = Math.floor(Math.random() * connections.length);
            const connection = connections[connectionIndex];
            
            // Create the packet mesh (small cube)
            const packetGeometry = new THREE.BoxGeometry(0.05, 0.05, 0.05);
            const packet = new THREE.Mesh(packetGeometry, packetMaterial);
            
            // Position at the start node
            const fromPos = nodePositions[connection.from];
            const toPos = nodePositions[connection.to];
            
            packet.position.set(fromPos.x, fromPos.y, fromPos.z);
            
            // Store packet data for animation
            packets.push({
                mesh: packet,
                from: {x: fromPos.x, y: fromPos.y, z: fromPos.z},
                to: {x: toPos.x, y: toPos.y, z: toPos.z},
                progress: 0,
                speed: 0.005 + Math.random() * 0.01
            });
            
            packetGroup.add(packet);
        }
        
        scene.add(packetGroup);
        return { packetGroup, packets };
    }
    
    // Create floating code elements
    function createFloatingCode() {
        const codeGroup = new THREE.Group();
        const codeTexts = [
            "const galaxy = createGalaxy();", 
            "function render() {", 
            "requestAnimationFrame(animate);", 
            "forEach((particle) => {", 
            "return new Promise((resolve) => {", 
            "<div className='container'>",
            "npm install three gsap",
            "import * as THREE from 'three';",
            "@keyframes float {",
            "git commit -m 'Add 3D effects'"
        ];
        
        const codeElements = [];
        
        // Create text sprites for each code snippet
        for (let i = 0; i < 10; i++) {
            // Create canvas for the text
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 1024;
            canvas.height = 256;
            
            // Draw gradient background
            const gradient = context.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, 'rgba(10, 20, 40, 0.9)');
            gradient.addColorStop(1, 'rgba(30, 50, 80, 0.9)');
            context.fillStyle = gradient;
            context.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw border
            context.strokeStyle = '#0088ff';
            context.lineWidth = 4;
            context.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
            
            // Draw text
            context.font = 'bold 64px monospace';
            context.textBaseline = 'middle';
            context.textAlign = 'center';
            
            // Text shadow
            context.fillStyle = 'rgba(0, 136, 255, 0.7)';
            context.fillText(codeTexts[i], canvas.width / 2 + 3, canvas.height / 2 + 3);
            
            // Actual text
            context.fillStyle = '#ffffff';
            context.fillText(codeTexts[i], canvas.width / 2, canvas.height / 2);
            
            // Create texture
            const texture = new THREE.CanvasTexture(canvas);
            
            // Create material
            const material = new THREE.SpriteMaterial({
                map: texture,
                transparent: true,
                opacity: 0.8
            });
            
            // Create sprite
            const sprite = new THREE.Sprite(material);
            
            // Set random position within a larger sphere
            const radius = 12 + Math.random() * 6;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);
            
            sprite.position.set(x, y, z);
            
            // Set size
            sprite.scale.set(5, 1.25, 1);
            
            // Add to group
            codeGroup.add(sprite);
            
            // Store for animation
            codeElements.push({
                sprite,
                initialPosition: { x, y, z },
                floatSpeed: 0.2 + Math.random() * 0.3,
                rotationSpeed: 0.1 + Math.random() * 0.2,
                floatOffset: Math.random() * Math.PI * 2
            });
        }
        
        scene.add(codeGroup);
        return { codeGroup, codeElements };
    }
    
    // Create all elements
    const galaxy = createGalaxy();
    const blockchain = createBlockchainNodes();
    const dataPackets = createDataPackets(blockchain.nodes.map(node => node.position), [
        {from: 0, to: 1}, {from: 1, to: 2}, {from: 2, to: 3}, {from: 3, to: 4},
        {from: 4, to: 5}, {from: 5, to: 6}, {from: 6, to: 7}, {from: 7, to: 8},
        {from: 8, to: 9}, {from: 9, to: 0}, {from: 0, to: 5}, {from: 1, to: 6},
        {from: 2, to: 7}, {from: 3, to: 8}, {from: 4, to: 9}
    ]);
    const floatingCode = createFloatingCode();
    
    // Position camera
    camera.position.z = 8;
    camera.position.y = 2;
    camera.lookAt(0, 0, 0);
    
    // Mouse move effect
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX);
        mouseY = (event.clientY - windowHalfY);
    });
    
    const clock = new THREE.Clock();

    // Scroll effect variables
    let scrollY = window.scrollY;
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', () => {
        scrollY = window.scrollY;
        
        // Determine scroll direction
        const scrollDirection = scrollY > lastScrollTop ? 'down' : 'up';
        lastScrollTop = scrollY;
        
        // Adjust galaxy rotation based on scroll position
        if (scrollDirection === 'down') {
            galaxy.rotation.x += 0.01;
            blockchain.nodeGroup.rotation.x += 0.005;
        } else {
            galaxy.rotation.x -= 0.01;
            blockchain.nodeGroup.rotation.x -= 0.005;
        }
        
        // Parallax effect - move elements based on scroll
        const scrollFactor = scrollY * 0.0005;
        galaxy.position.y = -scrollFactor * 2;
        blockchain.nodeGroup.position.y = -scrollFactor;
    });

    // Animation
    const animate = () => {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();
        
        targetX = mouseX * 0.0005;
        targetY = mouseY * 0.0005;

        // Update galaxy shader uniform
        if (galaxy.material.uniforms) {
            galaxy.material.uniforms.uTime.value = elapsedTime;
        }

        // Rotate galaxy and blockchain based on mouse movement
        galaxy.rotation.y += 0.03 * (targetX - galaxy.rotation.y);
        galaxy.rotation.x += 0.03 * (targetY - galaxy.rotation.x);
        
        blockchain.nodeGroup.rotation.y += 0.01 * (targetX - blockchain.nodeGroup.rotation.y);
        blockchain.nodeGroup.rotation.x += 0.01 * (targetY - blockchain.nodeGroup.rotation.x);
        
        // Slow constant rotation for galaxy
        galaxy.rotation.y += 0.001;
        
        // Animate blockchain nodes pulsing
        blockchain.nodes.forEach((node, i) => {
            node.scale.setScalar(1 + Math.sin(elapsedTime * 2 + i) * 0.1);
            node.material.emissiveIntensity = 0.5 + Math.sin(elapsedTime * 2 + i) * 0.2;
        });
        
        // Animate data packets
        dataPackets.packets.forEach(packet => {
            // Move along the line from -> to
            packet.progress += packet.speed;
            
            if (packet.progress >= 1) {
                // Reset packet position
                packet.progress = 0;
                
                // Swap from and to for reverse journey
                const temp = packet.from;
                packet.from = packet.to;
                packet.to = temp;
            }
            
            // Update position
            packet.mesh.position.x = packet.from.x + (packet.to.x - packet.from.x) * packet.progress;
            packet.mesh.position.y = packet.from.y + (packet.to.y - packet.from.y) * packet.progress;
            packet.mesh.position.z = packet.from.z + (packet.to.z - packet.from.z) * packet.progress;
            
            // Scale based on travel (grow slightly in the middle of the journey)
            const scale = 1 + Math.sin(packet.progress * Math.PI) * 0.5;
            packet.mesh.scale.setScalar(scale);
        });
        
        // Animate floating code elements
        floatingCode.codeElements.forEach((element, index) => {
            // Floating movement
            element.sprite.position.y = element.initialPosition.y + 
                Math.sin(elapsedTime * element.floatSpeed + element.floatOffset) * 1.5;
                
            // Slow rotation
            element.sprite.rotation.z = Math.sin(elapsedTime * element.rotationSpeed) * 0.1;
            
            // Subtle pulsing
            const pulse = 1 + Math.sin(elapsedTime * 0.5 + index) * 0.05;
            element.sprite.scale.set(5 * pulse, 1.25 * pulse, 1);
        });
        
        renderer.render(scene, camera);
    };
    
    animate();
    
    // Resize handler
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    });
    
    // GSAP Text animations
    gsap.registerPlugin(ScrollTrigger);
    gsap.to('.hero-title', { opacity: 1, y: 0, duration: 1.2, delay: 0.5 });
    gsap.to('.hero-subtitle', { opacity: 1, y: 0, duration: 1.2, delay: 0.8 });
    gsap.to('.hero-buttons', { opacity: 1, y: 0, duration: 1.2, delay: 1.1 });
    gsap.to('.social-links', { opacity: 1, y: 0, duration: 1.2, delay: 1.4 });
    
    // Create starfield background
    function createStars() {
        const starsContainer = document.querySelector('.stars-container');
        if (!starsContainer) return;
        
        const count = 100;
        
        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            const size = Math.random() * 2 + 1;
            
            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            star.style.left = `${Math.random() * 100}%`;
            star.style.top = `${Math.random() * 100}%`;
            star.style.animationDelay = `${Math.random() * 5}s`;
            star.style.animationDuration = `${Math.random() * 3 + 2}s`;
            
            star.classList.add('absolute', 'rounded-full', 'bg-white', 'animate-twinkle');
            
            starsContainer.appendChild(star);
        }
    }
    
    createStars();
    
    // Animated gradient lines
    function animateGradientLines() {
        const lines = document.querySelectorAll('.gradient-line');
        
        lines.forEach((line, index) => {
            gsap.fromTo(line, 
                { x: '-100%' }, 
                { 
                    x: '100%', 
                    duration: 15, 
                    delay: index * 2, 
                    repeat: -1,
                    ease: 'linear'
                }
            );
        });
    }
    
    animateGradientLines();
    
    // Typewriter effect for subtitle
    function typeWriterEffect() {
        const typewriterText = document.querySelector('.typewriter-text');
        if (!typewriterText) return;
        
        const words = ['Full Stack Developer', 'UI/UX Designer', 'Problem Solver', 'Tech Enthusiast'];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let typeSpeed = 100;
        
        function type() {
            const currentWord = words[wordIndex];
            
            if (isDeleting) {
                typewriterText.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
                typeSpeed = 50;
            } else {
                typewriterText.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
                typeSpeed = 100;
            }
            
            // Add blinking cursor effect
            if (!isDeleting && charIndex === currentWord.length + 1) {
                typewriterText.innerHTML = `${currentWord}<span class="inline-block w-1 h-6 ml-1 bg-blue-400 animate-blink"></span>`;
                isDeleting = true;
                typeSpeed = 1500; // Pause at the end of a word
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % words.length;
                typeSpeed = 500; // Pause before starting a new word
            }
            
            setTimeout(type, typeSpeed);
        }
        
        // Add cursor at the beginning
        typewriterText.innerHTML = '<span class="inline-block w-1 h-6 bg-blue-400 animate-blink"></span>';
        
        // Start typing after a delay
        setTimeout(type, 1000);
    }
    
    typeWriterEffect();
    
    // Scroll indicator click handler
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            const aboutSection = document.getElementById('about');
            if (aboutSection) {
                aboutSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Create digital particles
    function createDigitalParticles() {
        const container = document.getElementById('digital-particles-container');
        if (!container) return;
        
        const particleCount = 30;
        
        for (let i = 0; i < particleCount; i++) {
            createDigitalParticle(container);
        }
    }
    
    function createDigitalParticle(container) {
        const particle = document.createElement('div');
        particle.classList.add('digital-particle');
        
        // Random position, size and timing
        const size = Math.random() * 3 + 2;
        const left = Math.random() * 100;
        const delay = Math.random() * 10;
        const duration = Math.random() * 10 + 10;
        const opacity = Math.random() * 0.5 + 0.3;
        
        // Random color (blues and cyans)
        const colors = ['#3b82f6', '#0ea5e9', '#06b6d4', '#22d3ee'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${left}%`;
        particle.style.bottom = '0';
        particle.style.backgroundColor = color;
        particle.style.opacity = opacity.toString();
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;
        
        container.appendChild(particle);
        
        // Remove and recreate particle after animation completes
        setTimeout(() => {
            particle.remove();
            createDigitalParticle(container);
        }, (duration + delay) * 1000);
    }
    
    createDigitalParticles();
    
    // About Section Parallax for Image (keep)
    gsap.to('.about-image', {
        yPercent: -15,
        ease: "none",
        scrollTrigger: {
            trigger: '#about',
            start: 'top bottom',
            end: 'bottom top',
            scrub: true
        }
    });
    
    gsap.to('.about-content', {
        scrollTrigger: {
            trigger: '#about',
            start: 'top 80%',
            toggleActions: 'play none none none'
        },
        opacity: 1,
        x: 0,
        duration: 1,
        delay: 0.3
    });
    
    // Animate the About section underline
    ScrollTrigger.create({
        trigger: '#about',
        start: 'top 80%',
        onEnter: () => {
            gsap.to('.about-underline', {
                scaleX: 1,
                duration: 1.5,
                ease: 'power3.out'
            });
        }
    });
    
    // Animate skill bars when they come into view
    function animateSkillBars() {
        const skillBars = document.querySelectorAll('.skill-progress');
        
        skillBars.forEach(bar => {
            const width = bar.getAttribute('data-width');
            if (!width) {
                console.warn('Skill bar missing data-width attribute:', bar);
                return;
            }
            
            // Set initial state
            bar.style.transform = 'scaleX(0)';
            bar.style.transformOrigin = 'left';
            
            ScrollTrigger.create({
                trigger: bar,
                start: 'top 90%',
                onEnter: () => {
                    const widthValue = parseFloat(width.replace('%', ''));
                    if (isNaN(widthValue)) {
                        console.warn('Invalid width value:', width);
                        return;
                    }
                    
                    gsap.to(bar, {
                        scaleX: widthValue / 100,
                        duration: 1.5,
                        ease: 'power3.out'
                    });
                }
            });
        });
    }
    
    animateSkillBars();
    
    // Orbit animation for about image
    function animateOrbits() {
        const orbit1 = document.querySelector('.orbit-1');
        const orbit2 = document.querySelector('.orbit-2');
        const dot1 = document.querySelector('.orbit-dot-1');
        const dot2 = document.querySelector('.orbit-dot-2');
        
        if (!orbit1 || !orbit2 || !dot1 || !dot2) return;
        
        // Rotate orbits
        gsap.to(orbit1, {
            rotation: 360,
            duration: 20,
            repeat: -1,
            ease: 'none',
            transformOrigin: 'center'
        });
        
        gsap.to(orbit2, {
            rotation: -360,
            duration: 15,
            repeat: -1,
            ease: 'none',
            transformOrigin: 'center'
        });
        
        // Animate dots along the orbit paths
        animateOrbitDot(dot1, 20);
        animateOrbitDot(dot2, 15, true);
    }
    
    function animateOrbitDot(dot, duration, reverse = false) {
        const radius = 140; // Half of the orbit diameter
        const centerX = 140;
        const centerY = 140;
        
        gsap.to(dot, {
            keyframes: {
                "0%": { 
                    left: centerX + radius, 
                    top: centerY 
                },
                "25%": { 
                    left: centerX, 
                    top: centerY - radius 
                },
                "50%": { 
                    left: centerX - radius, 
                    top: centerY 
                },
                "75%": { 
                    left: centerX, 
                    top: centerY + radius 
                },
                "100%": { 
                    left: centerX + radius, 
                    top: centerY 
                }
            },
            duration: duration,
            ease: "none",
            repeat: -1,
            reversed: reverse
        });
    }
    
    animateOrbits();
    
    // Initialize Project Card Tilt Effect
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.style.transformStyle = 'preserve-3d'; // Apply preserve-3d to the card

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const width = rect.width;
            const height = rect.height;
            
            const rotateX = (y / height - 0.5) * -15; // Max rotation 15 degrees
            const rotateY = (x / width - 0.5) * 15;  // Max rotation 15 degrees

            gsap.to(card, {
                rotationX: rotateX,
                rotationY: rotateY,
                scale: 1.02, // Slightly scale up
                duration: 0.5,
                ease: 'power1.out'
            });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                rotationX: 0,
                rotationY: 0,
                scale: 1,
                duration: 0.5,
                ease: 'power1.out'
            });
        });
    });
    
    // ... rest of the code

});

// Timeline animations (using existing Intersection Observer)
const timelineItems = document.querySelectorAll('.timeline-item');
// ... existing code ... 

// Function to create interactive particles for hero section
function createHeroParticles(container) {
    const particleCount = 60; // Reduced for better performance
    const particles = [];
    const maxDistance = 150; // Max distance for connecting lines
    const colors = {
        particle: '#4b8bf4',
        connection: 'rgba(75, 139, 244, 0.15)'
    };
    
    // Set up the canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    container.appendChild(canvas);
    
    function resizeCanvas() {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 1,
            vx: Math.random() * 0.3 - 0.15, // Reduced velocity for smoother motion
            vy: Math.random() * 0.3 - 0.15, // Reduced velocity for smoother motion
            opacity: Math.random() * 0.5 + 0.5
        });
    }
    
    // Mouse tracking
    let mouseX = 0;
    let mouseY = 0;
    let mouseRadius = 150;
    let mouseActive = false;
    
    container.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        mouseActive = true;
    });
    
    container.addEventListener('mouseleave', () => {
        mouseActive = false;
    });
    
    // Animation
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw particles
        for (let i = 0; i < particleCount; i++) {
            const p = particles[i];
            
            // Update position
            p.x += p.vx;
            p.y += p.vy;
            
            // Boundary check
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            
            // Mouse interaction
            if (mouseActive) {
                const dx = p.x - mouseX;
                const dy = p.y - mouseY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < mouseRadius) {
                    const force = (mouseRadius - distance) / mouseRadius;
                    p.vx += dx * force * 0.02;
                    p.vy += dy * force * 0.02;
                }
            }
            
            // Apply speed limits
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (speed > 1) {
                p.vx = (p.vx / speed) * 1;
                p.vy = (p.vy / speed) * 1;
            }
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = colors.particle;
            ctx.globalAlpha = p.opacity;
            ctx.fill();
            ctx.globalAlpha = 1;
        }
        
        // Draw connections
        ctx.globalAlpha = 0.5;
        for (let i = 0; i < particleCount; i++) {
            for (let j = i + 1; j < particleCount; j++) {
                const p1 = particles[i];
                const p2 = particles[j];
                
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < maxDistance) {
                    ctx.strokeStyle = colors.connection;
                    ctx.globalAlpha = (1 - distance / maxDistance) * 0.5;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// Enhanced text animations for hero section
gsap.registerPlugin(ScrollTrigger);

// Hero section animations with staggered entrance
const heroTimeline = gsap.timeline({delay: 0.5});
heroTimeline.to('.hero-title', { opacity: 1, y: 0, duration: 1.2 });
heroTimeline.to('.hero-subtitle', { opacity: 1, y: 0, duration: 1, delay: 0.1 }, "-=0.8");
heroTimeline.to('.hero-buttons', { opacity: 1, y: 0, duration: 1 }, "-=0.6");
heroTimeline.to('.social-links', { opacity: 1, y: 0, duration: 1 }, "-=0.4");

// Improved typewriter effect for the hero subtitle
function typeWriterEffect() {
    const typewriterText = document.querySelector('.typewriter-text');
    if (!typewriterText) return;
    
    const words = ['Full Stack Developer', 'UI/UX Designer', 'Problem Solver', 'Tech Enthusiast'];
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typeSpeed = 100;
    
    function type() {
        const currentWord = words[wordIndex];
        
        if (isDeleting) {
            typewriterText.textContent = currentWord.substring(0, charIndex - 1);
            charIndex--;
            typeSpeed = 50;
        } else {
            typewriterText.textContent = currentWord.substring(0, charIndex + 1);
            charIndex++;
            typeSpeed = 100;
        }
        
        if (!isDeleting && charIndex === currentWord.length) {
            isDeleting = true;
            typeSpeed = 1500; // Pause at the end of a word
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            typeSpeed = 500; // Pause before starting a new word
        }
        
        setTimeout(type, typeSpeed);
    }
    
    // Start typing
    setTimeout(type, 1200);
}

typeWriterEffect();

// ... rest of the existing code
// ... 