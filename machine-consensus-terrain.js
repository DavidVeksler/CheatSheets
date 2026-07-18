import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

const CONFIG = {
  bounds: 10.7,
  segments: 128,
  baseHeight: 3.15,
  texture: 0.11,
  physics: { gravity: 1.72, momentum: 0.925, noiseScale: 0.34 },
  // Indices 6 (raw-corpus) and 7 (refusal) power the safeguard demo. Base: harmful
  // content is a real pit (it exists in the corpus) and no refusal basin exists.
  // Post-training: that pit inverts into a wall (negative depth) and a deep refusal
  // basin opens beside it, so the answer is diverted into "Refused" instead.
  basins: [
    { label: 'Mainstream view', center: [-2.15, 0.7], sigma: [2.15, 1.55], depth: 3.25 },
    { label: 'Expert niche', center: [2.5, -3.15], sigma: [1.5, 1.95], depth: 2.30 },
    { label: 'Contrarian', center: [3.9, 2.45], sigma: [1.75, 1.20], depth: 2.15 },
    { label: 'Fringe', center: [-0.2, 5.25], sigma: [1.08, 1.42], depth: 1.58 },
    { label: 'Institutional default', center: [-5.8, -4.75], sigma: [1.7, 1.25], depth: 2.48 },
    { label: 'Long-tail surprise', center: [6.35, -0.25], sigma: [1.15, 1.72], depth: 1.42 },
    { label: 'Raw-corpus basin', center: [8.8, -6.2], sigma: [1.5, 1.5], depth: 2.6 },
    { label: 'Refused', center: [7.0, -4.2], sigma: [1.3, 1.3], depth: 0.04 }
  ],
  rlhfBasins: [
    { label: 'Mainstream view', center: [-1.85, 0.6], sigma: [2.55, 1.88], depth: 4.28 },
    { label: 'Expert niche', center: [2.3, -3.0], sigma: [1.58, 2.35], depth: 2.15 },
    { label: 'Contrarian', center: [3.25, 2.25], sigma: [2.75, 1.08], depth: 1.82 },
    { label: 'Fringe', center: [-0.1, 5.1], sigma: [1.48, 1.68], depth: 0.48 },
    { label: 'Institutional default', center: [-5.45, -4.5], sigma: [1.95, 1.42], depth: 2.75 },
    { label: 'Long-tail surprise', center: [0.7, 1.35], sigma: [4.2, 0.7], depth: 1.12 },
    { label: 'Raw-corpus basin', center: [8.8, -6.2], sigma: [1.8, 1.8], depth: -2.0 },
    { label: 'Refused', center: [7.0, -4.2], sigma: [2.5, 2.2], depth: 4.2 }
  ],
  prompts: {
    safe: { drop: [-0.05, -0.2], nudge: [-0.16, 0.04] },
    steelman: { drop: [1.15, 1.45], nudge: [0.16, 0.13] },
    expert: { drop: [1.05, -0.95], nudge: [0.08, -0.17] },
    fringe: { drop: [0.05, 3.3], nudge: [-0.02, 0.18] },
    refusal: { drop: [8.0, -5.6], nudge: [-0.06, 0.12] }
  }
};

export function createTerrain(container, opts = {}) {
  if (!(container instanceof HTMLElement)) throw new TypeError('createTerrain requires a container element');

  const root = opts.root || container.closest('[data-terrain-root]') || container.parentElement;
  const componentRoot = opts.componentRoot || container.closest('.terrain-engine') || container;
  const query = new URLSearchParams(location.search);
  const reducedMotion = opts.reducedMotion ?? matchMedia('(prefers-reduced-motion: reduce)').matches;
  const seedValue = opts.seed || query.get('seed') || 'machine-consensus-story';
  const seed = [...seedValue].reduce((acc, ch) => Math.imul(acc ^ ch.charCodeAt(0), 16777619), 2166136261) >>> 0;
  const listeners = new Map();
  const els = {
    app: root,
    scene: container,
    state: root.querySelector('#state-text'),
    temperature: root.querySelector('#temperature'),
    tempValue: root.querySelector('#temperature-value'),
    rlhf: root.querySelector('#rlhf'),
    reroll: root.querySelector('#reroll'),
    callout: root.querySelector('#basin-callout'),
    calloutLabel: root.querySelector('#callout-label'),
    debug: root.querySelector('#debug-panel'),
    debugFields: root.querySelector('#debug-fields'),
    debugToggle: root.querySelector('#debug-toggle'),
    debugClose: root.querySelector('#debug-close'),
    fps: root.querySelector('#fps')
  };

  function mulberry32(a) {
    return () => {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  const random = mulberry32(seed);
  const randomSigned = () => random() * 2 - 1;
  const maxTrail = reducedMotion ? 45 : 90;
  let renderer, scene, camera, controls, terrain, particle, glow, pool, trail, resizeObserver;
  let morph = 0, morphTween = null, activePrompt = null, phase = 'idle', phaseTime = 0, idleTime = 0;
  let particleXZ = new THREE.Vector2(), velocity = new THREE.Vector2(), dropStart = new THREE.Vector3(), trailPoints = [];
  let lastTime = performance.now(), lastRealFrame = lastTime, frameAccumulator = 0, frameSamples = 0, slowSeconds = 0;
  let totalTime = 0, temperature = Number(els.temperature?.value ?? opts.temperature ?? 0.42);
  let fallbackActive = false, paused = false;

  function emit(type, detail = {}) {
    listeners.get(type)?.forEach(handler => handler(detail));
  }

  function on(type, handler) {
    if (!listeners.has(type)) listeners.set(type, new Set());
    listeners.get(type).add(handler);
    return () => listeners.get(type)?.delete(handler);
  }

  function hasWebGL2() {
    if (query.get('fallback') === '1') return false;
    try {
      const canvas = document.createElement('canvas');
      return !!canvas.getContext('webgl2', { failIfMajorPerformanceCaveat: true });
    } catch { return false; }
  }

  function showFallback() {
    if (fallbackActive) return;
    fallbackActive = true;
    root.dataset.terrainMode = 'fallback';
    root.dataset.rendering = 'paused';
    container.hidden = true;
    componentRoot.querySelectorAll('button, input').forEach(el => { el.disabled = true; });
    renderer?.setAnimationLoop(null);
    queueMicrotask(() => emit('fallback'));
  }

  function mixBasin(index) {
    const a = CONFIG.basins[index], b = CONFIG.rlhfBasins[index];
    return {
      label: a.label,
      center: [THREE.MathUtils.lerp(a.center[0], b.center[0], morph), THREE.MathUtils.lerp(a.center[1], b.center[1], morph)],
      sigma: [THREE.MathUtils.lerp(a.sigma[0], b.sigma[0], morph), THREE.MathUtils.lerp(a.sigma[1], b.sigma[1], morph)],
      depth: THREE.MathUtils.lerp(a.depth, b.depth, morph)
    };
  }

  function terrainNoise(x, z) {
    const s = seed * 0.000001;
    return (Math.sin(x * 1.37 + s) * Math.cos(z * 1.11 - s) + .45 * Math.sin((x + z) * 2.19 + s * 2.0)) * CONFIG.texture;
  }

  function heightAt(x, z) {
    let height = CONFIG.baseHeight + terrainNoise(x, z) + 0.12 * Math.sin(x * .29) * Math.cos(z * .35);
    for (let i = 0; i < CONFIG.basins.length; i++) {
      const b = mixBasin(i), dx = x - b.center[0], dz = z - b.center[1];
      height -= b.depth * Math.exp(-0.5 * ((dx * dx) / (b.sigma[0] ** 2) + (dz * dz) / (b.sigma[1] ** 2)));
    }
    return height;
  }

  function gradientAt(x, z) {
    const e = 0.055;
    return new THREE.Vector2(
      (heightAt(x + e, z) - heightAt(x - e, z)) / (2 * e),
      (heightAt(x, z + e) - heightAt(x, z - e)) / (2 * e)
    );
  }

  function shaderBasins(set) {
    return {
      centers: set.map(b => new THREE.Vector2(...b.center)),
      sigmas: set.map(b => new THREE.Vector2(...b.sigma)),
      depths: set.map(b => b.depth)
    };
  }

  function buildTerrain() {
    const a = shaderBasins(CONFIG.basins), b = shaderBasins(CONFIG.rlhfBasins);
    const geometry = new THREE.PlaneGeometry(CONFIG.bounds * 2, CONFIG.bounds * 2, CONFIG.segments, CONFIG.segments);
    const uniforms = THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
      uTime: { value: 0 }, uMorph: { value: 0 }, uSeed: { value: seed * .000001 },
      uMotionFactor: { value: reducedMotion ? .5 : 1 },
      uBaseHeight: { value: CONFIG.baseHeight }, uTexture: { value: CONFIG.texture },
      uCentersA: { value: a.centers }, uSigmasA: { value: a.sigmas }, uDepthsA: { value: a.depths },
      uCentersB: { value: b.centers }, uSigmasB: { value: b.sigmas }, uDepthsB: { value: b.depths }
    }]);
    const material = new THREE.ShaderMaterial({
      uniforms, fog: true, side: THREE.DoubleSide,
      vertexShader: `
        #include <fog_pars_vertex>
        uniform float uTime; uniform float uMorph; uniform float uSeed; uniform float uBaseHeight; uniform float uTexture;
        uniform vec2 uCentersA[8]; uniform vec2 uSigmasA[8]; uniform float uDepthsA[8];
        uniform vec2 uCentersB[8]; uniform vec2 uSigmasB[8]; uniform float uDepthsB[8];
        varying float vHeight; varying float vSlope; varying vec2 vCoord;
        float field(vec2 p) {
          float h=uBaseHeight+(sin(p.x*1.37+uSeed)*cos(p.y*1.11-uSeed)+.45*sin((p.x+p.y)*2.19+uSeed*2.0))*uTexture;
          h += .12*sin(p.x*.29)*cos(p.y*.35);
          for(int i=0;i<8;i++) {
            vec2 c=mix(uCentersA[i],uCentersB[i],uMorph); vec2 s=mix(uSigmasA[i],uSigmasB[i],uMorph); float d=mix(uDepthsA[i],uDepthsB[i],uMorph);
            vec2 q=(p-c)/s; h -= d*exp(-.5*dot(q,q));
          }
          return h;
        }
        void main() {
          vec2 p=vec2(position.x,-position.y); float h=field(p); float e=.08;
          float hx=field(p+vec2(e,0.))-field(p-vec2(e,0.)); float hz=field(p+vec2(0.,e))-field(p-vec2(0.,e));
          vec3 transformed=vec3(position.xy,h); vHeight=h; vSlope=length(vec2(hx,hz))/(2.*e); vCoord=p;
          vec4 mvPosition=modelViewMatrix*vec4(transformed,1.); gl_Position=projectionMatrix*mvPosition;
          #include <fog_vertex>
        }`,
      fragmentShader: `
        #include <fog_pars_fragment>
        uniform float uTime; uniform float uMotionFactor; varying float vHeight; varying float vSlope; varying vec2 vCoord;
        void main() {
          float low=smoothstep(2.7,-.9,vHeight); float mid=smoothstep(3.5,.8,vHeight);
          // near-black cool substrate; basins warm faintly from within
          vec3 base=mix(vec3(.012,.028,.045),vec3(.02,.05,.072),mid);
          base=mix(base,vec3(.05,.028,.014),low*.55);
          // luminous contour lines read as topography AND a network mesh: cyan up high, amber deep
          vec3 lineCol=mix(vec3(.18,.72,.95),vec3(1.2,.52,.14),low);
          float major=1.-smoothstep(0.,.055,abs(fract(vHeight*1.15)-.5));
          float minor=1.-smoothstep(0.,.09,abs(fract(vHeight*4.6)-.5));
          float glowAmt=.55+1.1*low+.3*mid;
          vec3 color=base+lineCol*(major*glowAmt+minor*.28*glowAmt);
          // basin inner bloom (light pooling from within)
          float shimmer=.6+.4*sin(uTime*.6+vCoord.x*.4+vCoord.y*.3);
          color += low*low*vec3(1.,.42,.12)*(.4+.22*shimmer)*uMotionFactor;
          // faint cool sheen on slopes so 3D form still reads between the lines
          color += min(vSlope,1.5)*vec3(.015,.04,.055)*(1.-low)*.6;
          gl_FragColor=vec4(color,1.);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
          #include <fog_fragment>
        }`
    });
    terrain = new THREE.Mesh(geometry, material);
    terrain.rotation.x = -Math.PI / 2;
    terrain.position.y = -2.4;
    scene.add(terrain);

    const edge = new THREE.Mesh(
      new THREE.BoxGeometry(CONFIG.bounds * 2, .45, CONFIG.bounds * 2),
      new THREE.MeshBasicMaterial({ color: 0x070b0d, transparent: true, opacity: .55 })
    );
    edge.position.y = -2.62;
    scene.add(edge);
  }

  function glowTexture() {
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 128;
    const ctx = canvas.getContext('2d'), g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, 'rgba(255,235,184,1)'); g.addColorStop(.13, 'rgba(242,166,64,.8)');
    g.addColorStop(.45, 'rgba(242,114,35,.2)'); g.addColorStop(1, 'rgba(242,114,35,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 128, 128);
    const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
    return texture;
  }

  function buildParticle() {
    particle = new THREE.Mesh(new THREE.SphereGeometry(.4, 28, 28), new THREE.MeshBasicMaterial({ color: 0xffedc8 }));
    particle.visible = false; particle.renderOrder = 10; scene.add(particle);
    // Halo around the ball. depthTest on (default) so ridges occlude it — reads as a 3D
    // light source sitting in the terrain, not a flat decal pasted over everything.
    glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture(), color: 0xf6a541, transparent: true, opacity: .75, depthWrite: false, blending: THREE.AdditiveBlending }));
    glow.scale.set(2.2, 2.2, 1); glow.visible = false; glow.renderOrder = 9; scene.add(glow);
    // Horizontal disc that lies on the basin floor; the rising rim occludes its far edge,
    // so the settled answer reads as light collecting *inside* the pocket.
    pool = new THREE.Mesh(new THREE.CircleGeometry(1, 48), new THREE.MeshBasicMaterial({ map: glowTexture(), color: 0xffb54f, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
    pool.rotation.x = -Math.PI / 2; pool.visible = false; pool.renderOrder = 5; scene.add(pool);
    // Fat line: LineBasicMaterial.linewidth is ignored by WebGL, so a real screen-space
    // width needs Line2. Normal blending + a cream head keep it visible on the bright amber basin.
    const geometry = new LineGeometry();
    geometry.setPositions([0, 0, 0, 0, 0, 0]); geometry.setColors([0, 0, 0, 0, 0, 0]);
    trail = new Line2(geometry, new LineMaterial({
      linewidth: reducedMotion ? 3.4 : 5.2, vertexColors: true, transparent: true,
      opacity: reducedMotion ? .55 : .92, depthTest: false, alphaToCoverage: false
    }));
    trail.visible = false; trail.renderOrder = 8; scene.add(trail);
  }

  function setTemperature(value) {
    temperature = THREE.MathUtils.clamp(Number(value), 0, 1.5);
    if (els.temperature) {
      els.temperature.value = String(temperature);
      els.temperature.style.setProperty('--fill', `${temperature / 1.5 * 100}%`);
    }
    if (els.tempValue) els.tempValue.value = temperature.toFixed(2);
  }

  function bindUI() {
    root.querySelectorAll('.prompt-button').forEach(button => button.addEventListener('click', () => selectPrompt(button.dataset.prompt)));
    els.temperature?.addEventListener('input', () => setTemperature(els.temperature.value));
    setTemperature(temperature);
    els.rlhf?.addEventListener('change', () => startMorph(els.rlhf.checked ? 1 : 0));
    els.reroll?.addEventListener('click', () => activePrompt && selectPrompt(activePrompt, true));
  }

  function selectPrompt(key, reroll = false) {
    if (!CONFIG.prompts[key] || fallbackActive) return;
    idleTime = 0; controls.autoRotate = false;
    activePrompt = key;
    root.querySelectorAll('.prompt-button').forEach(button => button.classList.toggle('active', button.dataset.prompt === key));
    if (els.reroll) els.reroll.disabled = false;
    hideCallout();
    const prompt = CONFIG.prompts[key], spread = .38 + temperature * .55;
    particleXZ.set(prompt.drop[0] + randomSigned() * spread, prompt.drop[1] + randomSigned() * spread);
    velocity.set(prompt.nudge[0] + randomSigned() * .055, prompt.nudge[1] + randomSigned() * .055);
    dropStart.set(particleXZ.x, heightAt(particleXZ.x, particleXZ.y) + 6.8, particleXZ.y);
    particle.position.copy(dropStart); glow.position.copy(dropStart);
    particle.visible = glow.visible = trail.visible = true;
    particle.scale.setScalar(.01); glow.material.opacity = 0; glow.scale.set(2.2, 2.2, 1);
    pool.visible = false; pool.material.opacity = 0; trailPoints = [];
    setPhase('dropping', reroll ? 'Re-rolling the same prompt…' : 'Dropping prompt onto the terrain…');
  }

  function setPhase(next, label) {
    phase = next; phaseTime = 0; root.dataset.state = next;
    if (els.state) els.state.textContent = label;
  }

  function startMorph(target) {
    const next = THREE.MathUtils.clamp(Number(target), 0, 1);
    morphTween = { from: morph, to: next, elapsed: 0, duration: 2.6 };
    if (els.rlhf) els.rlhf.checked = next === 1;
    hideCallout();
    if (phase === 'settled' && particle.visible) {
      const nudgeAngle = random() * Math.PI * 2, nudgeMag = .02 + random() * .02;
      velocity.set(Math.cos(nudgeAngle) * nudgeMag, Math.sin(nudgeAngle) * nudgeMag);
      pool.visible = false; pool.material.opacity = 0;
      setPhase('descending', 'The terrain is moving under a settled answer…');
    } else if (els.state) {
      els.state.textContent = next ? 'Post-training is reshaping likely answers…' : 'Restoring the base landscape…';
    }
  }

  function updateMorph(dt) {
    if (!morphTween) return;
    morphTween.elapsed += dt;
    const t = Math.min(1, morphTween.elapsed / morphTween.duration);
    const eased = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    morph = THREE.MathUtils.lerp(morphTween.from, morphTween.to, eased);
    terrain.material.uniforms.uMorph.value = morph;
    root.dataset.morph = morph.toFixed(3);
    if (t >= 1) {
      morph = morphTween.to; morphTween = null;
      if (phase === 'settled') settleAtNearest();
      else if (phase === 'idle' && els.state) els.state.textContent = 'Choose a prompt to begin';
    }
  }

  function updateParticle(dt) {
    if (phase === 'dropping') {
      phaseTime += dt;
      const t = Math.min(1, phaseTime / .82), eased = 1 - Math.pow(1 - t, 3);
      const surface = heightAt(particleXZ.x, particleXZ.y) - 2.4 + .23;
      particle.position.set(particleXZ.x, THREE.MathUtils.lerp(dropStart.y, surface, eased), particleXZ.y);
      particle.scale.setScalar(Math.min(1, t * 3)); glow.material.opacity = Math.min(.78, t * 1.3);
      glow.position.copy(particle.position);
      if (t >= 1) setPhase('descending', 'Rolling downhill toward a likely answer…');
      return;
    }
    if (phase === 'settled') {
      if (particle.visible) {
        const y = heightAt(particleXZ.x, particleXZ.y) - 2.4 + .23;
        particle.position.y = y; glow.position.copy(particle.position);
      }
      if (pool.visible) {
        pool.material.opacity = Math.min(.85, pool.material.opacity + dt * 2.4);
        pool.scale.setScalar(3.1 + Math.sin(totalTime * 1.4) * .14);
      }
      return;
    }
    if (phase !== 'descending') return;
    phaseTime += dt;
    const fixedDt = Math.min(dt, .035) * 60;
    const gradient = gradientAt(particleXZ.x, particleXZ.y);
    const thermal = CONFIG.physics.noiseScale * temperature * (.72 + .28 * Math.sin(phaseTime * 2.1));
    velocity.multiplyScalar(Math.pow(CONFIG.physics.momentum, fixedDt));
    velocity.addScaledVector(gradient, -CONFIG.physics.gravity * .014 * fixedDt);
    velocity.x += randomSigned() * thermal * .012 * fixedDt;
    velocity.y += randomSigned() * thermal * .012 * fixedDt;
    velocity.clampLength(0, .23 + temperature * .055);
    particleXZ.addScaledVector(velocity, fixedDt);
    const limit = CONFIG.bounds - .25;
    if (Math.abs(particleXZ.x) > limit) { particleXZ.x = THREE.MathUtils.clamp(particleXZ.x, -limit, limit); velocity.x *= -.5; }
    if (Math.abs(particleXZ.y) > limit) { particleXZ.y = THREE.MathUtils.clamp(particleXZ.y, -limit, limit); velocity.y *= -.5; }
    const y = heightAt(particleXZ.x, particleXZ.y) - 2.4 + .23;
    particle.position.set(particleXZ.x, y, particleXZ.y); glow.position.copy(particle.position);
    glow.material.opacity = .64 + Math.sin(phaseTime * 5) * .12 + temperature * .08;
    addTrailPoint(particle.position);

    const nearest = nearestBasin(), localGrad = gradient.length();
    const lowTempSettle = temperature < .9 && phaseTime > 2.5 && velocity.length() < .018 && localGrad < .12;
    const warmSettle = phaseTime > 7 + temperature * 2.2 && nearest.distance < (temperature > 1 ? 1.45 : 1.05);
    if (lowTempSettle || warmSettle || phaseTime > 13) settleAtNearest();
  }

  function addTrailPoint(pos) {
    trailPoints.unshift(pos.clone()); if (trailPoints.length > maxTrail) trailPoints.pop();
    const n = trailPoints.length; if (n < 2) return;
    const positions = new Float32Array(n * 3), colors = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const p = trailPoints[i]; positions[i * 3] = p.x; positions[i * 3 + 1] = p.y; positions[i * 3 + 2] = p.z;
      const t = 1 - i / (n - 1), b = .64 + .36 * t; // head (ball) cream & bright, tail stays a warm amber
      colors[i * 3] = b; colors[i * 3 + 1] = b * (.6 + .35 * t); colors[i * 3 + 2] = b * (.28 + .56 * t);
    }
    trail.geometry.setPositions(positions); trail.geometry.setColors(colors);
  }

  function nearestBasin() {
    let result = { index: 0, distance: Infinity, basin: mixBasin(0) };
    for (let i = 0; i < CONFIG.basins.length; i++) {
      const basin = mixBasin(i), distance = Math.hypot(particleXZ.x - basin.center[0], particleXZ.y - basin.center[1]);
      if (distance < result.distance) result = { index: i, distance, basin };
    }
    return result;
  }

  function settleAtNearest() {
    const nearest = nearestBasin();
    let label = `Settled in “${nearest.basin.label}”`;
    if (nearest.basin.label === 'Refused') label = 'Refused — post-training walls off this region';
    else if (nearest.basin.label === 'Raw-corpus basin') label = 'No safeguard here — the base model would answer';
    setPhase('settled', label);
    velocity.set(0, 0);
    glow.scale.set(2.6, 2.6, 1); glow.material.opacity = .9;
    const py = heightAt(particleXZ.x, particleXZ.y) - 2.4 + .06; // pool lies on the basin floor
    pool.position.set(particleXZ.x, py, particleXZ.y);
    pool.scale.setScalar(3.1); pool.material.opacity = 0; pool.visible = true;
    if (els.callout && els.calloutLabel) {
      els.calloutLabel.textContent = nearest.basin.label; els.callout.hidden = false;
      requestAnimationFrame(() => els.callout.classList.add('visible'));
    }
    emit('settled', { basinLabel: nearest.basin.label, basinIndex: nearest.index });
  }

  function hideCallout() {
    if (!els.callout) return;
    els.callout.classList.remove('visible');
    setTimeout(() => { if (!els.callout.classList.contains('visible')) els.callout.hidden = true; }, 480);
  }

  function updateCallout() {
    if (!els.callout || els.callout.hidden || !particle.visible) return;
    const projected = particle.position.clone().project(camera), rect = container.getBoundingClientRect();
    const x = THREE.MathUtils.clamp((projected.x * .5 + .5) * rect.width, 24, rect.width - 165);
    const y = THREE.MathUtils.clamp((-projected.y * .5 + .5) * rect.height - 12, 90, rect.height - 150);
    els.callout.style.left = `${x}px`; els.callout.style.top = `${y}px`;
  }

  function debugInput(label, object, key, min, max, step, callback) {
    const row = document.createElement('div'), lab = document.createElement('label');
    const input = document.createElement('input'), output = document.createElement('output');
    row.className = 'debug-row'; lab.textContent = label; input.type = 'range';
    input.min = min; input.max = max; input.step = step; input.value = object[key];
    output.value = Number(object[key]).toFixed(step < .01 ? 3 : 2);
    input.addEventListener('input', () => {
      object[key] = Number(input.value); output.value = Number(input.value).toFixed(step < .01 ? 3 : 2);
      input.style.setProperty('--fill', `${(input.value - min) / (max - min) * 100}%`); callback?.();
    });
    input.dispatchEvent(new Event('input')); row.append(lab, input, output); return row;
  }

  function debugGroup(title, rows) {
    const group = document.createElement('section'), heading = document.createElement('h3');
    group.className = 'debug-group'; heading.textContent = title; group.append(heading, ...rows); return group;
  }

  function refreshTerrain() {
    const data = shaderBasins(CONFIG.basins), uniforms = terrain.material.uniforms;
    uniforms.uCentersA.value = data.centers; uniforms.uSigmasA.value = data.sigmas; uniforms.uDepthsA.value = data.depths;
  }

  function createDebugPanel() {
    if (query.get('debug') !== '1' || !els.debug || !els.debugFields) return;
    els.debugToggle.hidden = false;
    const fields = [debugGroup('Physics', [
      debugInput('Gravity', CONFIG.physics, 'gravity', .2, 3.5, .01),
      debugInput('Momentum', CONFIG.physics, 'momentum', .75, .99, .001),
      debugInput('Noise', CONFIG.physics, 'noiseScale', 0, .9, .01)
    ])];
    CONFIG.basins.forEach(basin => fields.push(debugGroup(basin.label, [
      debugInput('Center X', basin.center, 0, -9, 9, .05, refreshTerrain),
      debugInput('Center Z', basin.center, 1, -9, 9, .05, refreshTerrain),
      debugInput('Sigma X', basin.sigma, 0, .5, 4, .05, refreshTerrain),
      debugInput('Sigma Z', basin.sigma, 1, .5, 4, .05, refreshTerrain),
      debugInput('Depth', basin, 'depth', .1, 5, .05, refreshTerrain)
    ])));
    els.debugFields.append(...fields);
    const toggle = open => { els.debug.hidden = !open; els.debugToggle.setAttribute('aria-expanded', String(open)); };
    els.debugToggle.addEventListener('click', () => toggle(true));
    els.debugClose?.addEventListener('click', () => toggle(false));
  }

  function resize() {
    if (!renderer || !camera) return;
    const { width, height } = container.getBoundingClientRect();
    if (width < 2 || height < 2) return;
    camera.aspect = width / height; camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(devicePixelRatio, width < 760 ? 1.35 : 1.7));
    renderer.setSize(width, height, false);
    trail?.material.resolution.set(width, height);
  }

  function frameBody(dt) {
    idleTime += dt; totalTime += dt;
    if (!reducedMotion && idleTime > 8 && phase !== 'dropping') controls.autoRotate = true;
    updateMorph(dt); updateParticle(dt); updateCallout(); controls.update();
    terrain.material.uniforms.uTime.value = totalTime;
    if (particle.visible) { particle.rotation.x += dt * 2; particle.rotation.z += dt * 1.4; }
    renderer.render(scene, camera);
    frameAccumulator += dt; frameSamples++;
    if (frameAccumulator >= 2.2) {
      const fps = frameSamples / frameAccumulator;
      if (els.fps && query.get('debug') === '1') { els.fps.hidden = false; els.fps.textContent = `${fps.toFixed(0)} fps`; }
      if (totalTime > 5 && fps < 30) slowSeconds += frameAccumulator;
      else slowSeconds = Math.max(0, slowSeconds - frameAccumulator);
      frameAccumulator = 0; frameSamples = 0;
      if (slowSeconds > 4.2) showFallback();
    }
  }

  function animate(now) {
    const dt = Math.min((now - lastTime) / 1000, .05); lastTime = now; lastRealFrame = now;
    frameBody(dt);
  }

  function step(ms = 16.7) {
    if (fallbackActive) return;
    if (!paused && performance.now() - lastRealFrame < 250) return;
    frameBody(Math.min(ms / 1000, .05));
  }

  function pause() {
    if (!renderer || fallbackActive || paused) return;
    paused = true; root.dataset.rendering = 'paused'; renderer.setAnimationLoop(null);
  }

  function resume() {
    if (!renderer || fallbackActive || !paused) return;
    paused = false; root.dataset.rendering = 'running'; lastTime = performance.now(); renderer.setAnimationLoop(animate);
  }

  function init() {
    if (!hasWebGL2()) { showFallback(); return; }
    scene = new THREE.Scene(); scene.background = new THREE.Color(0x070a0c); scene.fog = new THREE.FogExp2(0x070a0c, .043);
    camera = new THREE.PerspectiveCamera(40, 1, .1, 80); camera.position.set(11.2, 13.6, 16.8);
    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance', alpha: false });
    renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.28;
    container.appendChild(renderer.domElement);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.dampingFactor = .055; controls.enablePan = false;
    controls.minPolarAngle = Math.PI * .16; controls.maxPolarAngle = Math.PI * .46;
    controls.minDistance = 13; controls.maxDistance = 28; controls.target.set(1.1, .2, 0);
    controls.autoRotate = false; controls.autoRotateSpeed = .28;
    controls.addEventListener('start', () => { idleTime = 0; controls.autoRotate = false; });
    buildTerrain(); buildParticle(); bindUI(); createDebugPanel(); resize();
    resizeObserver = new ResizeObserver(resize); resizeObserver.observe(container);
    root.dataset.terrainMode = 'webgl'; root.dataset.rendering = 'running'; renderer.setAnimationLoop(animate);
  }

  const api = {
    dropPrompt: key => selectPrompt(key),
    reroll: () => activePrompt && selectPrompt(activePrompt, true),
    setTemperature,
    setMorph: target => startMorph(target),
    getPhase: () => phase,
    getMode: () => fallbackActive ? 'fallback' : 'webgl',
    pause,
    resume,
    step,
    __inspect: () => ({
      visible: trail.visible, points: trailPoints.length,
      linewidth: trail.material.linewidth, res: [trail.material.resolution.x, trail.material.resolution.y],
      instanceCount: trail.geometry.instanceCount, glowScale: glow.scale.x, glowOpacity: +glow.material.opacity.toFixed(2),
      poolVisible: pool.visible, poolOpacity: +pool.material.opacity.toFixed(2), ballRadius: particle.geometry.parameters.radius
    }),
    on,
    destroy() {
      pause(); resizeObserver?.disconnect(); renderer?.dispose(); listeners.clear();
    }
  };

  init();
  return api;
}
