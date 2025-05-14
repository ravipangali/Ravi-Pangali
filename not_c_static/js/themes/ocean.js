// Ocean Theme Animation - Simple Version
// Creates a basic ocean effect with a clearly visible submarine

(function() {
    // Prevent multiple initializations
    if (window.oceanSceneInitialized) {
        console.log("Ocean theme already initialized, stopping first");
        if (window.stopOceanScene) window.stopOceanScene();
    }
    window.oceanSceneInitialized = true;
    
    // Debug mode
    const DEBUG = true;
    
    // Main Three.js variables
    let scene, camera, renderer;
    let submarine, water;
    let animationId;
    
    // Create and initialize the ocean scene
    function initOcean() {
        console.log("Initializing ocean theme");
        
        // Create container
        const container = document.createElement('div');
        container.id = 'ocean-container';
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.zIndex = '-1';
        container.style.overflow = 'hidden';
        document.body.appendChild(container);
        
        // Create scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0066aa); // Blue background
        
        // Create camera
        camera = new THREE.PerspectiveCamera(
            75, 
            window.innerWidth / window.innerHeight, 
            0.1, 
            1000
        );
        camera.position.set(0, 0, 100);
        camera.lookAt(0, 0, 0);
        
        // Create renderer
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);
        
        // Add lights
        const ambientLight = new THREE.AmbientLight(0xccccff, 0.4);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(0, 10, 10);
        scene.add(directionalLight);
        
        // Create simple water plane
        createWater();
        
        // Create submarine
        createSubmarine();
        
        // Add bubbles
        createBubbles();
        
        // Create some fish
        createFish();
        
        // Handle window resize
        window.addEventListener('resize', onWindowResize);
        
        // Add mouse tracking for submarine
        document.addEventListener('mousemove', onMouseMove);
        
        // Start animation loop
        animate();
        
        console.log("Ocean theme initialized");
    }
    
    // Create water surface
    function createWater() {
        const waterGeometry = new THREE.PlaneGeometry(2000, 2000, 50, 50);
        const waterMaterial = new THREE.MeshStandardMaterial({
            color: 0x0077ee,
            transparent: true,
            opacity: 0.8,
            side: THREE.DoubleSide,
            flatShading: true
        });
        
        water = new THREE.Mesh(waterGeometry, waterMaterial);
        water.rotation.x = -Math.PI / 2;
        water.position.y = 30;
        scene.add(water);
        
        // Add underwater fog
        scene.fog = new THREE.FogExp2(0x004488, 0.01);
    }
    
    // Create submarine
    function createSubmarine() {
        // Create a group for the submarine
        submarine = new THREE.Group();
        
        // Main body - blue cylinder
        const bodyGeometry = new THREE.CylinderGeometry(7, 7, 35, 16);
        bodyGeometry.rotateZ(Math.PI / 2);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x0055aa,
            metalness: 0.3,
            roughness: 0.7
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        submarine.add(body);
        
        // Nose cone
        const noseGeometry = new THREE.ConeGeometry(7, 15, 16);
        noseGeometry.rotateZ(-Math.PI / 2);
        const nose = new THREE.Mesh(noseGeometry, bodyMaterial);
        nose.position.set(25, 0, 0);
        submarine.add(nose);
        
        // Tail cone
        const tailGeometry = new THREE.ConeGeometry(7, 15, 16);
        tailGeometry.rotateZ(Math.PI / 2);
        const tail = new THREE.Mesh(tailGeometry, bodyMaterial);
        tail.position.set(-25, 0, 0);
        submarine.add(tail);
        
        // Conning tower
        const towerGeometry = new THREE.BoxGeometry(12, 10, 8);
        const towerMaterial = new THREE.MeshStandardMaterial({
            color: 0x003366,
            metalness: 0.3,
            roughness: 0.7
        });
        const tower = new THREE.Mesh(towerGeometry, towerMaterial);
        tower.position.set(0, 12, 0);
        submarine.add(tower);
        
        // Windows - add bright emissive windows
        const windowMaterial = new THREE.MeshStandardMaterial({
            color: 0xffcc00,
            emissive: 0xffcc00,
            emissiveIntensity: 0.5,
            metalness: 0.2,
            roughness: 0.3
        });
        
        // Add several circular windows along the side
        for (let i = -15; i <= 15; i += 7) {
            const windowGeometry = new THREE.CircleGeometry(2, 16);
            windowGeometry.rotateY(Math.PI / 2);
            
            // Left side window
            const windowLeft = new THREE.Mesh(windowGeometry, windowMaterial);
            windowLeft.position.set(i, 0, 7.1);
            submarine.add(windowLeft);
            
            // Right side window
            const windowRight = new THREE.Mesh(windowGeometry.clone(), windowMaterial);
            windowRight.position.set(i, 0, -7.1);
            windowRight.rotation.y = Math.PI;
            submarine.add(windowRight);
        }
        
        // Propeller
        const propellerGroup = new THREE.Group();
        const propellerMaterial = new THREE.MeshStandardMaterial({
            color: 0x777777,
            metalness: 0.7,
            roughness: 0.3
        });
        
        const blade1 = new THREE.Mesh(
            new THREE.BoxGeometry(1, 12, 1),
            propellerMaterial
        );
        propellerGroup.add(blade1);
        
        const blade2 = new THREE.Mesh(
            new THREE.BoxGeometry(1, 12, 1),
            propellerMaterial
        );
        blade2.rotation.x = Math.PI / 2;
        propellerGroup.add(blade2);
        
        propellerGroup.position.set(-33, 0, 0);
        submarine.add(propellerGroup);
        
        // Animate propeller
        function animatePropeller() {
            propellerGroup.rotation.x += 0.1;
            requestAnimationFrame(animatePropeller);
        }
        animatePropeller();
        
        // Position submarine in the scene
        submarine.position.set(0, 0, 30);
        submarine.rotation.y = Math.PI / 4; // Angle for better view
        scene.add(submarine);
        
        // Add spotlight to highlight submarine
        const spotlight = new THREE.SpotLight(0xffffff, 1);
        spotlight.position.set(30, 30, 50);
        spotlight.angle = Math.PI / 6;
        spotlight.penumbra = 0.3;
        spotlight.target = submarine;
        scene.add(spotlight);
        
        console.log("Submarine created at", submarine.position);
    }
    
    // Create bubbles around submarine
    function createBubbles() {
        const bubblesGroup = new THREE.Group();
        const bubbleMaterial = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.7,
            metalness: 0.1,
            roughness: 0.3
        });
        
        // Create 30 bubbles
        for (let i = 0; i < 30; i++) {
            const size = 0.5 + Math.random() * 1.5;
            const bubbleGeometry = new THREE.SphereGeometry(size, 12, 12);
            const bubble = new THREE.Mesh(bubbleGeometry, bubbleMaterial);
            
            // Position randomly near the submarine
            bubble.position.set(
                -30 - Math.random() * 10,
                Math.random() * 10 - 5,
                Math.random() * 10 - 5
            );
            
            // Add custom properties for animation
            bubble.userData = {
                speed: 0.1 + Math.random() * 0.2,
                offset: Math.random() * 100
            };
            
            bubblesGroup.add(bubble);
        }
        
        scene.add(bubblesGroup);
        
        // Animate bubbles
        function animateBubbles() {
            bubblesGroup.children.forEach(bubble => {
                // Move upward and slightly to the left
                bubble.position.y += bubble.userData.speed;
                bubble.position.x -= bubble.userData.speed * 0.3;
                
                // Apply some random motion
                const time = Date.now() * 0.001;
                bubble.position.x += Math.sin(time + bubble.userData.offset) * 0.05;
                bubble.position.z += Math.cos(time + bubble.userData.offset) * 0.05;
                
                // Reset bubbles that have risen too high
                if (bubble.position.y > 50) {
                    bubble.position.y = -10;
                    bubble.position.x = -30 - Math.random() * 10;
                    bubble.position.z = Math.random() * 10 - 5;
                }
            });
            
            requestAnimationFrame(animateBubbles);
        }
        
        animateBubbles();
    }
    
    // Create some fish
    function createFish() {
        const fishColors = [
            0xff9900, // Orange
            0x66ccff, // Light blue
            0xff6699, // Pink
            0x99ff66  // Light green
        ];
        
        for (let i = 0; i < 10; i++) {
            const fishGroup = new THREE.Group();
            
            // Fish body - simple cone
            const bodyGeometry = new THREE.ConeGeometry(3, 8, 8);
            bodyGeometry.rotateZ(Math.PI / 2);
            const bodyMaterial = new THREE.MeshStandardMaterial({
                color: fishColors[i % fishColors.length],
                metalness: 0.2,
                roughness: 0.8
            });
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            fishGroup.add(body);
            
            // Fish tail - flattened cone
            const tailGeometry = new THREE.ConeGeometry(4, 4, 8);
            tailGeometry.rotateZ(-Math.PI / 2);
            const tail = new THREE.Mesh(tailGeometry, bodyMaterial);
            tail.position.set(-6, 0, 0);
            fishGroup.add(tail);
            
            // Position fish randomly in the water
            fishGroup.position.set(
                Math.random() * 150 - 75,
                Math.random() * 40 - 20,
                Math.random() * 80 - 40
            );
            
            // Add data for animation
            fishGroup.userData = {
                speed: 0.2 + Math.random() * 0.3,
                rotationSpeed: 0.01 + Math.random() * 0.02,
                direction: new THREE.Vector3(1, 0, 0), // Start direction
                targetPosition: new THREE.Vector3(
                    Math.random() * 150 - 75,
                    Math.random() * 40 - 20,
                    Math.random() * 80 - 40
                )
            };
            
            scene.add(fishGroup);
            
            // Animate tail
            function animateTail(fish) {
                const time = Date.now() * 0.001;
                tail.rotation.y = Math.sin(time * 5) * 0.3;
                requestAnimationFrame(() => animateTail(fish));
            }
            
            animateTail(fishGroup);
        }
    }
    
    // Handle mouse movement to control submarine
    function onMouseMove(event) {
        if (!submarine) return;
        
        // Get the 3D point in space that corresponds to the mouse position
        const mouseVector = new THREE.Vector3();
        
        // Calculate normalized device coordinates (-1 to +1)
        mouseVector.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouseVector.y = -(event.clientY / window.innerHeight) * 2 + 1; // Y is inverted
        mouseVector.z = 0.5; // Set to value in middle of screen
        
        // Convert to 3D world coordinates
        mouseVector.unproject(camera);
        
        // Calculate direction from camera
        const direction = mouseVector.sub(camera.position).normalize();
        
        // Calculate a point in space that's in the direction of the cursor
        const distance = 100; // Some distance in front of the camera
        const targetPoint = new THREE.Vector3().copy(camera.position).add(direction.multiplyScalar(distance));
        
        // Make submarine look at this point
        // Store current position so we don't change it
        const currentPosition = submarine.position.clone();
        
        // Look at the target point (this calculates the rotation needed)
        submarine.lookAt(targetPoint);
        
        // Apply a small offset to make submarine face slightly upward for better visibility
        submarine.rotation.x += 0.1;
        
        // Ensure position didn't change
        submarine.position.copy(currentPosition);
        
        // Log occasionally for debugging
        if (Math.random() < 0.005) {
            console.log("Submarine rotation:", {
                x: submarine.rotation.x.toFixed(2),
                y: submarine.rotation.y.toFixed(2),
                z: submarine.rotation.z.toFixed(2)
            });
        }
    }
    
    // Handle window resize
    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    // Animate water 
    function animateWater() {
        if (!water) return;
        
        const time = Date.now() * 0.001;
        const positions = water.geometry.attributes.position;
        
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i);
            const z = positions.getZ(i);
            
            // Only animate vertices that aren't at the edge
            if (Math.abs(x) < 900 && Math.abs(z) < 900) {
                const waveHeight = Math.sin(x * 0.05 + time) * 
                                  Math.cos(z * 0.05 + time) * 3;
                positions.setY(i, waveHeight);
            }
        }
        
        positions.needsUpdate = true;
        water.geometry.computeVertexNormals();
    }
    
    // Animate fish
    function animateFish() {
        scene.children.forEach(child => {
            if (child.userData && child.userData.speed) {
                // This is a fish group
                
                // Move toward target position
                const direction = new THREE.Vector3().subVectors(
                    child.userData.targetPosition,
                    child.position
                ).normalize();
                
                // Update position
                child.position.x += direction.x * child.userData.speed;
                child.position.y += direction.y * child.userData.speed;
                child.position.z += direction.z * child.userData.speed;
                
                // Look in the direction of movement
                child.lookAt(
                    child.position.x + direction.x,
                    child.position.y + direction.y,
                    child.position.z + direction.z
                );
                
                // If near target, set new target
                if (child.position.distanceTo(child.userData.targetPosition) < 10) {
                    child.userData.targetPosition.set(
                        Math.random() * 150 - 75,
                        Math.random() * 40 - 20,
                        Math.random() * 80 - 40
                    );
                }
            }
        });
    }
    
    // Main animation loop
    function animate() {
        animationId = requestAnimationFrame(animate);
        
        // Remove bobbing motion to keep submarine position fixed
        // Keep submarine position completely stable
        if (submarine) {
            // Ensure position stays fixed at original coordinates
            submarine.position.set(0, 0, 30);
        }
        
        // Animate water
        animateWater();
        
        // Animate fish
        animateFish();
        
        // Render scene
        renderer.render(scene, camera);
    }
    
    // Clean up resources
    function cleanUp() {
        console.log("Cleaning up ocean theme");
        
        // Stop animation loop
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        
        // Remove event listeners
        window.removeEventListener('resize', onWindowResize);
        document.removeEventListener('mousemove', onMouseMove);
        
        // Remove renderer and container
        if (renderer) {
            renderer.dispose();
            const canvas = renderer.domElement;
            if (canvas && canvas.parentNode) {
                canvas.parentNode.removeChild(canvas);
            }
        }
        
        // Remove container
        const container = document.getElementById('ocean-container');
        if (container) {
            container.remove();
        }
        
        // Reset scene
        scene = null;
        camera = null;
        renderer = null;
        submarine = null;
        water = null;
        
        // Reset initialization flag
        window.oceanSceneInitialized = false;
        
        console.log("Ocean theme cleaned up");
    }
    
    // Initialize theme if Three.js is available or load it
    function startOceanTheme() {
        console.log("Starting ocean theme");
        
        if (typeof THREE === 'undefined') {
            console.log("Loading Three.js library");
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            script.onload = () => {
                console.log("Three.js loaded, initializing ocean");
                initOcean();
            };
            document.head.appendChild(script);
        } else {
            console.log("Three.js already loaded, initializing ocean");
            initOcean();
        }
    }
    
    // Export start and stop functions
    window.initOceanScene = startOceanTheme;
    window.stopOceanScene = cleanUp;
    
    // Start the theme
    startOceanTheme();
})(); 