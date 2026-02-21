/* ─────────────────────────────────────────────────────────────
   THREE-HERO.JS  — AI Neural-Sphere with data pulses & parallax
   ───────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas || typeof THREE === "undefined") return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  /* ── Renderer ─────────────────────────────────── */
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 600);
  camera.position.set(0, 0, 140);

  /* ── Lights ───────────────────────────────────── */
  scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  const light1 = new THREE.PointLight(0x22c3ff, 3.5, 300);
  light1.position.set(60, 80, 60);
  scene.add(light1);
  const light2 = new THREE.PointLight(0x6d7dff, 2.5, 300);
  light2.position.set(-80, -40, 40);
  scene.add(light2);

  /* ── Neural sphere nodes ─────────────────────── */
  const NODE_COUNT = 220;
  const SPHERE_R   = 55;
  const nodePos    = [];   // {x,y,z}

  // Fibonacci sphere distribution — evenly spread nodes on sphere surface
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < NODE_COUNT; i++) {
    const y   = 1 - (i / (NODE_COUNT - 1)) * 2;
    const r   = Math.sqrt(1 - y * y);
    const phi = goldenAngle * i;
    nodePos.push({
      x: Math.cos(phi) * r * SPHERE_R,
      y: y * SPHERE_R,
      z: Math.sin(phi) * r * SPHERE_R,
    });
  }

  /* Flat position array for BufferGeometry */
  const nodePosFlat = new Float32Array(NODE_COUNT * 3);
  nodePos.forEach((p, i) => {
    nodePosFlat[i * 3]     = p.x;
    nodePosFlat[i * 3 + 1] = p.y;
    nodePosFlat[i * 3 + 2] = p.z;
  });

  const nodeGeo = new THREE.BufferGeometry();
  nodeGeo.setAttribute("position", new THREE.BufferAttribute(nodePosFlat, 3));
  const nodeMat = new THREE.PointsMaterial({
    color: 0x22c3ff,
    size: 1.4,
    transparent: true,
    opacity: 0.9,
    sizeAttenuation: true,
  });
  const nodeCloud = new THREE.Points(nodeGeo, nodeMat);
  scene.add(nodeCloud);

  /* ── Edges ────────────────────────────────────── */
  const EDGE_THRESH = 24;
  const edgeSegments = [];  // pairs of node indices close enough to connect
  for (let i = 0; i < NODE_COUNT; i++) {
    for (let j = i + 1; j < NODE_COUNT; j++) {
      const dx = nodePos[i].x - nodePos[j].x;
      const dy = nodePos[i].y - nodePos[j].y;
      const dz = nodePos[i].z - nodePos[j].z;
      if (Math.sqrt(dx*dx + dy*dy + dz*dz) < EDGE_THRESH) {
        edgeSegments.push(i, j);
      }
    }
  }

  const edgePts = new Float32Array(edgeSegments.length * 3);
  for (let k = 0; k < edgeSegments.length; k++) {
    const idx = edgeSegments[k];
    edgePts[k * 3]     = nodePos[idx].x;
    edgePts[k * 3 + 1] = nodePos[idx].y;
    edgePts[k * 3 + 2] = nodePos[idx].z;
  }
  const edgeGeo = new THREE.BufferGeometry();
  edgeGeo.setAttribute("position", new THREE.BufferAttribute(edgePts, 3));
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x6d7dff, transparent: true, opacity: 0.22 });
  scene.add(new THREE.LineSegments(edgeGeo, edgeMat));

  /* ── Data-pulse particles that travel along edges ─ */
  const PULSE_COUNT = 14;
  const pulses = [];
  const pulseGeo = new THREE.BufferGeometry();
  const pulsePts = new Float32Array(PULSE_COUNT * 3);
  pulseGeo.setAttribute("position", new THREE.BufferAttribute(pulsePts, 3));
  const pulseMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 2.8,
    transparent: true,
    opacity: 0.95,
    sizeAttenuation: true,
  });
  scene.add(new THREE.Points(pulseGeo, pulseMat));

  const edgePairCount = edgeSegments.length / 2;
  function spawnPulse() {
    const pairIdx = Math.floor(Math.random() * edgePairCount);
    const a = edgeSegments[pairIdx * 2];
    const b = edgeSegments[pairIdx * 2 + 1];
    return { a, b, t: 0, speed: 0.008 + Math.random() * 0.012 };
  }
  for (let i = 0; i < PULSE_COUNT; i++) pulses.push(spawnPulse());

  /* ── Outer wireframe icosphere accent ─────────── */
  const icoGeo = new THREE.IcosahedronGeometry(SPHERE_R * 1.22, 1);
  const icoMat = new THREE.MeshBasicMaterial({
    color: 0x22c3ff,
    wireframe: true,
    transparent: true,
    opacity: 0.06,
  });
  const ico = new THREE.Mesh(icoGeo, icoMat);
  scene.add(ico);

  /* ── Torus knot accent (off-centre) ───────────── */
  const knot = new THREE.Mesh(
    new THREE.TorusKnotGeometry(7, 1.8, 120, 16),
    new THREE.MeshStandardMaterial({
      color: 0x6d7dff,
      metalness: 0.8,
      roughness: 0.15,
      emissive: 0x2233aa,
      emissiveIntensity: 0.4,
    })
  );
  knot.position.set(90, -25, -10);
  scene.add(knot);

  /* ── Floating ring ────────────────────────────── */
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(28, 0.5, 8, 80),
    new THREE.MeshBasicMaterial({ color: 0x22c3ff, transparent: true, opacity: 0.18 })
  );
  ring.rotation.x = Math.PI / 3;
  ring.position.set(-70, 20, -30);
  scene.add(ring);

  /* ── Mouse parallax ───────────────────────────── */
  let mouseX = 0, mouseY = 0;
  let targetRotX = 0, targetRotY = 0;
  window.addEventListener("mousemove", e => {
    mouseX = (e.clientX / innerWidth  - 0.5) * 2;
    mouseY = (e.clientY / innerHeight - 0.5) * 2;
  });

  /* ── Color cycling ────────────────────────────── */
  const colorA = new THREE.Color(0x22c3ff);
  const colorB = new THREE.Color(0xa78bfa);
  const colorC = new THREE.Color(0x38bdf8);
  let colorT = 0;

  /* ── Animation loop ───────────────────────────── */
  let frame = 0;
  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    frame++;

    /* Smooth sphere rotation + mouse parallax */
    targetRotY += (mouseX * 0.25 - targetRotY) * 0.03;
    targetRotX += (mouseY * 0.15 - targetRotX) * 0.03;

    nodeCloud.rotation.y = t * 0.06 + targetRotY;
    nodeCloud.rotation.x = targetRotX;
    edgeGeo.attributes.position && (function(){
      // rotate the entire edge mesh with the node cloud
    })();

    /* Rotate whole group together */
    const sphereGroup = nodeCloud;
    ico.rotation.y = t * 0.04 + targetRotY;
    ico.rotation.x = targetRotX;

    /* Knot & ring */
    knot.rotation.x += 0.004;
    knot.rotation.y += 0.007;
    ring.rotation.z += 0.003;
    ring.position.y = 20 + Math.sin(t * 0.5) * 8;

    /* Color cycle for node dots */
    colorT = (Math.sin(t * 0.3) + 1) * 0.5;
    const lerpedColor = colorA.clone().lerp(colorB, colorT).lerp(colorC, Math.abs(Math.sin(t * 0.5)));
    nodeMat.color.set(lerpedColor);

    /* Light pulse */
    light1.intensity = 3.5 + Math.sin(t * 1.2) * 1.0;
    light2.intensity = 2.5 + Math.sin(t * 0.9 + 1) * 0.8;

    /* Animate data pulses */
    for (let i = 0; i < pulses.length; i++) {
      const p = pulses[i];
      p.t += p.speed;
      if (p.t >= 1) {
        pulses[i] = spawnPulse();
        continue;
      }
      const nA = nodePos[p.a];
      const nB = nodePos[p.b];
      // Apply same rotation as nodeCloud
      const cosY = Math.cos(nodeCloud.rotation.y);
      const sinY = Math.sin(nodeCloud.rotation.y);
      const lx = nA.x + (nB.x - nA.x) * p.t;
      const ly = nA.y + (nB.y - nA.y) * p.t;
      const lz = nA.z + (nB.z - nA.z) * p.t;
      pulsePts[i * 3]     = lx * cosY - lz * sinY;
      pulsePts[i * 3 + 1] = ly + Math.sin(nodeCloud.rotation.x) * lz;
      pulsePts[i * 3 + 2] = lx * sinY + lz * cosY;
    }
    pulseGeo.attributes.position.needsUpdate = true;

    /* Pulsing opacity for edges */
    edgeMat.opacity = 0.18 + Math.sin(t * 0.8) * 0.07;

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    renderer.setSize(innerWidth, innerHeight);
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
  });
});
