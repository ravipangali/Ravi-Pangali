(function(){if(window.oceanSceneInitialized){console.log("Ocean theme already initialized,stopping first");if(window.stopOceanScene)window.stopOceanScene();}window.oceanSceneInitialized=true;const DEBUG=true;let scene,camera,renderer;let submarine,water;let animationId;function initOcean(){console.log("Initializing ocean theme");const container=document.createElement('div');container.id='ocean-container';container.style.position='fixed';container.style.top='0';container.style.left='0';container.style.width='100%';container.style.height='100%';container.style.zIndex='-1';container.style.overflow='hidden';document.body.appendChild(container);scene=new THREE.Scene();scene.background=new THREE.Color(0x0066aa);camera=new THREE.PerspectiveCamera(75,window.innerWidth / window.innerHeight,0.1,1000);camera.position.set(0,0,100);camera.lookAt(0,0,0);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(window.devicePixelRatio);renderer.setSize(window.innerWidth,window.innerHeight);container.appendChild(renderer.domElement);const ambientLight=new THREE.AmbientLight(0xccccff,0.4);scene.add(ambientLight);const directionalLight=new THREE.DirectionalLight(0xffffff,1);directionalLight.position.set(0,10,10);scene.add(directionalLight);createWater();createSubmarine();createBubbles();createFish();window.addEventListener('resize',onWindowResize);document.addEventListener('mousemove',onMouseMove);animate();console.log("Ocean theme initialized");}function createWater(){const waterGeometry=new THREE.PlaneGeometry(2000,2000,50,50);const waterMaterial=new THREE.MeshStandardMaterial({color:0x0077ee,transparent:true,opacity:0.8,side:THREE.DoubleSide,flatShading:true});water=new THREE.Mesh(waterGeometry,waterMaterial);water.rotation.x=-Math.PI / 2;water.position.y=30;scene.add(water);scene.fog=new THREE.FogExp2(0x004488,0.01);}function createSubmarine(){submarine=new THREE.Group();const bodyGeometry=new THREE.CylinderGeometry(7,7,35,16);bodyGeometry.rotateZ(Math.PI / 2);const bodyMaterial=new THREE.MeshStandardMaterial({color:0x0055aa,metalness:0.3,roughness:0.7});const body=new THREE.Mesh(bodyGeometry,bodyMaterial);submarine.add(body);const noseGeometry=new THREE.ConeGeometry(7,15,16);noseGeometry.rotateZ(-Math.PI / 2);const nose=new THREE.Mesh(noseGeometry,bodyMaterial);nose.position.set(25,0,0);submarine.add(nose);const tailGeometry=new THREE.ConeGeometry(7,15,16);tailGeometry.rotateZ(Math.PI / 2);const tail=new THREE.Mesh(tailGeometry,bodyMaterial);tail.position.set(-25,0,0);submarine.add(tail);const towerGeometry=new THREE.BoxGeometry(12,10,8);const towerMaterial=new THREE.MeshStandardMaterial({color:0x003366,metalness:0.3,roughness:0.7});const tower=new THREE.Mesh(towerGeometry,towerMaterial);tower.position.set(0,12,0);submarine.add(tower);const windowMaterial=new THREE.MeshStandardMaterial({color:0xffcc00,emissive:0xffcc00,emissiveIntensity:0.5,metalness:0.2,roughness:0.3});for(let i=-15;i <=15;i +=7){const windowGeometry=new THREE.CircleGeometry(2,16);windowGeometry.rotateY(Math.PI / 2);const windowLeft=new THREE.Mesh(windowGeometry,windowMaterial);windowLeft.position.set(i,0,7.1);submarine.add(windowLeft);const windowRight=new THREE.Mesh(windowGeometry.clone(),windowMaterial);windowRight.position.set(i,0,-7.1);windowRight.rotation.y=Math.PI;submarine.add(windowRight);}const propellerGroup=new THREE.Group();const propellerMaterial=new THREE.MeshStandardMaterial({color:0x777777,metalness:0.7,roughness:0.3});const blade1=new THREE.Mesh(new THREE.BoxGeometry(1,12,1),propellerMaterial);propellerGroup.add(blade1);const blade2=new THREE.Mesh(new THREE.BoxGeometry(1,12,1),propellerMaterial);blade2.rotation.x=Math.PI / 2;propellerGroup.add(blade2);propellerGroup.position.set(-33,0,0);submarine.add(propellerGroup);function animatePropeller(){propellerGroup.rotation.x +=0.1;requestAnimationFrame(animatePropeller);}animatePropeller();submarine.position.set(0,0,30);submarine.rotation.y=Math.PI / 4;scene.add(submarine);const spotlight=new THREE.SpotLight(0xffffff,1);spotlight.position.set(30,30,50);spotlight.angle=Math.PI / 6;spotlight.penumbra=0.3;spotlight.target=submarine;scene.add(spotlight);console.log("Submarine created at",submarine.position);}function createBubbles(){const bubblesGroup=new THREE.Group();const bubbleMaterial=new THREE.MeshStandardMaterial({color:0xffffff,transparent:true,opacity:0.7,metalness:0.1,roughness:0.3});for(let i=0;i < 30;i++){const size=0.5 + Math.random()* 1.5;const bubbleGeometry=new THREE.SphereGeometry(size,12,12);const bubble=new THREE.Mesh(bubbleGeometry,bubbleMaterial);bubble.position.set(-30 - Math.random()* 10,Math.random()* 10 - 5,Math.random()* 10 - 5);bubble.userData={speed:0.1 + Math.random()* 0.2,offset:Math.random()* 100};bubblesGroup.add(bubble);}scene.add(bubblesGroup);function animateBubbles(){bubblesGroup.children.forEach(bubble=>{bubble.position.y +=bubble.userData.speed;bubble.position.x -=bubble.userData.speed * 0.3;const time=Date.now()* 0.001;bubble.position.x +=Math.sin(time + bubble.userData.offset)* 0.05;bubble.position.z +=Math.cos(time + bubble.userData.offset)* 0.05;if(bubble.position.y > 50){bubble.position.y=-10;bubble.position.x=-30 - Math.random()* 10;bubble.position.z=Math.random()* 10 - 5;}});requestAnimationFrame(animateBubbles);}animateBubbles();}function createFish(){const fishColors=[ 0xff9900,0x66ccff,0xff6699,0x99ff66 ];for(let i=0;i < 10;i++){const fishGroup=new THREE.Group();const bodyGeometry=new THREE.ConeGeometry(3,8,8);bodyGeometry.rotateZ(Math.PI / 2);const bodyMaterial=new THREE.MeshStandardMaterial({color:fishColors[i % fishColors.length],metalness:0.2,roughness:0.8});const body=new THREE.Mesh(bodyGeometry,bodyMaterial);fishGroup.add(body);const tailGeometry=new THREE.ConeGeometry(4,4,8);tailGeometry.rotateZ(-Math.PI / 2);const tail=new THREE.Mesh(tailGeometry,bodyMaterial);tail.position.set(-6,0,0);fishGroup.add(tail);fishGroup.position.set(Math.random()* 150 - 75,Math.random()* 40 - 20,Math.random()* 80 - 40);fishGroup.userData={speed:0.2 + Math.random()* 0.3,rotationSpeed:0.01 + Math.random()* 0.02,direction:new THREE.Vector3(1,0,0),targetPosition:new THREE.Vector3(Math.random()* 150 - 75,Math.random()* 40 - 20,Math.random()* 80 - 40)};scene.add(fishGroup);function animateTail(fish){const time=Date.now()* 0.001;tail.rotation.y=Math.sin(time * 5)* 0.3;requestAnimationFrame(()=> animateTail(fish));}animateTail(fishGroup);}}function onMouseMove(event){if(!submarine)return;const mouseVector=new THREE.Vector3();mouseVector.x=(event.clientX / window.innerWidth)* 2 - 1;mouseVector.y=-(event.clientY / window.innerHeight)* 2 + 1;mouseVector.z=0.5;mouseVector.unproject(camera);const direction=mouseVector.sub(camera.position).normalize();const distance=100;const targetPoint=new THREE.Vector3().copy(camera.position).add(direction.multiplyScalar(distance));const currentPosition=submarine.position.clone();submarine.lookAt(targetPoint);submarine.rotation.x +=0.1;submarine.position.copy(currentPosition);if(Math.random()< 0.005){console.log("Submarine rotation:",{x:submarine.rotation.x.toFixed(2),y:submarine.rotation.y.toFixed(2),z:submarine.rotation.z.toFixed(2)});}}function onWindowResize(){camera.aspect=window.innerWidth / window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight);}function animateWater(){if(!water)return;const time=Date.now()* 0.001;const positions=water.geometry.attributes.position;for(let i=0;i < positions.count;i++){const x=positions.getX(i);const z=positions.getZ(i);if(Math.abs(x)< 900 && Math.abs(z)< 900){const waveHeight=Math.sin(x * 0.05 + time)* Math.cos(z * 0.05 + time)* 3;positions.setY(i,waveHeight);}}positions.needsUpdate=true;water.geometry.computeVertexNormals();}function animateFish(){scene.children.forEach(child=>{if(child.userData && child.userData.speed){const direction=new THREE.Vector3().subVectors(child.userData.targetPosition,child.position).normalize();child.position.x +=direction.x * child.userData.speed;child.position.y +=direction.y * child.userData.speed;child.position.z +=direction.z * child.userData.speed;child.lookAt(child.position.x + direction.x,child.position.y + direction.y,child.position.z + direction.z);if(child.position.distanceTo(child.userData.targetPosition)< 10){child.userData.targetPosition.set(Math.random()* 150 - 75,Math.random()* 40 - 20,Math.random()* 80 - 40);}}});}function animate(){animationId=requestAnimationFrame(animate);if(submarine){submarine.position.set(0,0,30);}animateWater();animateFish();renderer.render(scene,camera);}function cleanUp(){console.log("Cleaning up ocean theme");if(animationId){cancelAnimationFrame(animationId);}window.removeEventListener('resize',onWindowResize);document.removeEventListener('mousemove',onMouseMove);if(renderer){renderer.dispose();const canvas=renderer.domElement;if(canvas && canvas.parentNode){canvas.parentNode.removeChild(canvas);}}const container=document.getElementById('ocean-container');if(container){container.remove();}scene=null;camera=null;renderer=null;submarine=null;water=null;window.oceanSceneInitialized=false;console.log("Ocean theme cleaned up");}function startOceanTheme(){console.log("Starting ocean theme");if(typeof THREE==='undefined'){console.log("Loading Three.js library");const script=document.createElement('script');script.src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';script.onload=()=>{console.log("Three.js loaded,initializing ocean");initOcean();};document.head.appendChild(script);}else{console.log("Three.js already loaded,initializing ocean");initOcean();}}window.initOceanScene=startOceanTheme;window.stopOceanScene=cleanUp;startOceanTheme();})();