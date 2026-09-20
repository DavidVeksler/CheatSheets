/* Pure geometry and SVG renderer shared by build-time and browser states. */
(function(root){
'use strict';
const PI=Math.PI,rad=d=>d*PI/180,deg=r=>r*180/PI;
const add=(a,b)=>a.map((v,i)=>v+b[i]),mul=(a,k)=>a.map(v=>v*k),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const unit=a=>mul(a,1/Math.hypot(...a)),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function refract(v,n,eta){const c=-dot(v,n),q=1-eta*eta*(1-c*c);if(q<0)return null;return add(mul(v,eta),mul(n,eta*c-Math.sqrt(q)));}
const reflect=(v,n)=>add(v,mul(n,-2*dot(v,n)));
const next=(p,v)=>add(p,mul(v,-2*dot(p,v)));
function trace(b,n=4/3,reflections=1){
 const entry=[-Math.sqrt(1-b*b),b],vin=[1,0],inside=refract(vin,entry,1/n),points=[entry];
 let p=entry,v=inside;for(let j=0;j<reflections;j++){p=next(p,v);points.push(p);v=reflect(v,p);}
 p=next(p,v);points.push(p);const outgoing=refract(v,mul(p,-1),n);
 return {points,vin,inside,outgoing,b,n,beta:180-deg(Math.atan2(Math.abs(outgoing[1]),outgoing[0]))};
}
function stationary(n=4/3,p=2){const i=Math.asin(Math.sqrt((p*p-n*n)/(p*p-1))),r=Math.asin(Math.sin(i)/n),D=(p-1)*PI+2*i-2*p*r;return {b:Math.sin(i),i:deg(i),r:deg(r),D:deg(D),beta:180-deg(Math.acos(Math.cos(D)))};}
const num=n=>Number(n.toFixed(2)),xy=p=>p.map(num).join(','),line=(a,b,cls='guide',extra='')=>`<line x1="${num(a[0])}" y1="${num(a[1])}" x2="${num(b[0])}" y2="${num(b[1])}" class="${cls}" ${extra}/>`;
const path=(points,cls='ray',extra='')=>`<path d="M${points.map(xy).join(' L')}" class="${cls}" ${extra}/>`;
const label=(x,y,t,cls='')=>`<text x="${num(x)}" y="${num(y)}" class="${cls}">${t}</text>`;
const dotmark=(p,r=4,cls='dot')=>`<circle cx="${num(p[0])}" cy="${num(p[1])}" r="${r}" class="${cls}"/>`;
function svg(content,w,h,title,desc=''){return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${title}" xmlns="http://www.w3.org/2000/svg"><title>${title}</title><desc>${desc}</desc>${content}</svg>`;}
function arrow(a,b,cls='ray'){const v=unit(add(b,mul(a,-1))),q=add(a,mul(add(b,mul(a,-1)),.58)),l=add(q,mul(v,-8)),per=[-v[1],v[0]];return line(a,b,cls)+path([add(l,mul(per,4)),q,add(l,mul(per,-4))],cls);}
function clipSegment(a,b,box){let lo=0,hi=1;const d=add(b,mul(a,-1));for(const [p,q] of [[-d[0],a[0]-box[0]],[d[0],box[2]-a[0]],[-d[1],a[1]-box[1]],[d[1],box[3]-a[1]]]){if(p===0){if(q<0)return null;}else{const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);}}return lo<=hi?[add(a,mul(d,lo)),add(a,mul(d,hi))]:null;}
function angleArc(p,v1,v2,r,text){let a=Math.atan2(v1[1],v1[0]),b=Math.atan2(v2[1],v2[0]);while(b-a>PI)b-=2*PI;while(b-a<-PI)b+=2*PI;const pts=Array.from({length:17},(_,j)=>add(p,[r*Math.cos(a+(b-a)*j/16),r*Math.sin(a+(b-a)*j/16)]));const mid=(a+b)/2;return path(pts,'angle')+label(p[0]+(r+15)*Math.cos(mid),p[1]+(r+15)*Math.sin(mid),text);}
function drop(b=.860663,n=4/3,refs=1,neighbors=false,small=false){
 const w=small?340:560,h=small?300:400,scale=small?79:126,c=[w*.52,h*.53],P=p=>[c[0]+p[0]*scale,c[1]-p[1]*scale];
 let s=`<circle cx="${c[0]}" cy="${c[1]}" r="${scale}" class="water"/>`;
 function ray(t,cl){const ps=[add(t.points[0],[-1.5,0]),...t.points,add(t.points.at(-1),mul(t.outgoing,1.5))].map(P);return ps.slice(1).map((p,i)=>{const segment=clipSegment(ps[i],p,[8,45,w-8,small?h-10:h-45]);return segment?arrow(...segment,cl):'';}).join('');}
 if(neighbors)for(const offset of [-.055,-.028,.028,.055])s+=ray(trace(Math.max(.01,Math.min(.985,b+offset)),n,refs),'neighbor');
 const t=trace(b,n,refs);s+=ray(t,'ray');
 t.points.forEach((p,j)=>{if(t.points.slice(0,j).some(q=>Math.hypot(...add(q,mul(p,-1)))<1e-7))return;const indices=t.points.flatMap((q,k)=>Math.hypot(...add(q,mul(p,-1)))<1e-7?[k+1]:[]);s+=line(P(mul(p,.78)),P(mul(p,1.14)),'normal');s+=dotmark(P(p),4);const lp=P(mul(p,1.12));s+=label(lp[0]+7,lp[1]+5,indices.join('/'),'event-number');});
 if(!small){const p=P(t.points[0]);s+=angleArc(p,[-1,0],[t.points[0][0],-t.points[0][1]],35,'i');s+=angleArc(p,[-t.points[0][0],t.points[0][1]],[t.inside[0],-t.inside[1]],39,'r');s+=label(18,28,refs===1?'DROP SECTION · 1 reflection':'DROP SECTION · 2 reflections');s+=label(18,h-18,`b/a = ${b.toFixed(3)} · n = ${n.toFixed(5)}`);}
 else s+=label(16,25,'DROP D · same three events');
 return svg(s,w,h,refs===1?'Calculated primary light path through a spherical drop':'Calculated secondary light path through a spherical drop','Solid arrows show light propagation; gray lines are surface normals. Entry, partial internal reflection, exit.');
}
const camera={eye:[12,-5,9],target:[0,3,1]};
const forward=unit(add(camera.target,mul(camera.eye,-1))),right=unit(cross(forward,[0,0,1])),up=cross(right,forward);
function project(p){const q=add(p,mul(camera.target,-1));return [310+dot(q,right)*36,252-dot(q,up)*36];}
function direction(e,beta,phi){const k=[0,Math.cos(rad(e)),-Math.sin(rad(e))],v=[0,Math.sin(rad(e)),Math.cos(rad(e))];return add(mul(k,Math.cos(rad(beta))),mul(add(mul([1,0,0],Math.cos(phi)),mul(v,Math.sin(phi))),Math.sin(rad(beta))));}
const field=[];
for(let j=0;j<150;j++){let x=((j*73)%151)/151*7-3.5,y=1.2+((j*37)%149)/149*6,z=.15+((j*53)%157)/157*5;field.push([x,y,z]);}
// Fixed sample points remain fixed when the observer or Sun moves.
for(const ob of [0,1.2])for(const e of [0,15,30])for(const d of [3,5,7])for(const phi of [.55,1,1.57,2.14,2.6]){const p=add([ob,0,.1],mul(direction(e,42.27,phi),d));if(p[2]>0&&p[2]<=5&&Math.abs(p[0])<=3.5&&p[1]>=1.2&&p[1]<=7.2)field.push(p);}
function observerState(observer=0,elevation=15){const o=[observer?1.2:0,0,.1],beta=stationary(1.3316655570438782).beta,k=[0,Math.cos(rad(elevation)),-Math.sin(rad(elevation))];const drops=field.map((p,j)=>{const v=unit(add(p,mul(o,-1))),betaDrop=deg(Math.acos(Math.max(-1,Math.min(1,dot(v,k)))));return {p,j,selected:betaDrop<=beta&&betaDrop>beta-1,angle:betaDrop};});return {o,beta,k,drops,elevation,observer};}
function impactForBeta(beta,n){let lo=0,hi=stationary(n).b;for(let j=0;j<48;j++){const mid=(lo+hi)/2;if(trace(mid,n).beta<beta)lo=mid;else hi=mid;}return (lo+hi)/2;}
function observerDrop(observer=0,elevation=15){const n=1.3316655570438782,s=observerState(observer,elevation),d=s.drops.find(d=>d.selected);return d?drop(impactForBeta(d.angle,n),n,1,false,true):svg(label(18,38,'No selected above-ground drop.')+label(18,75,'Raise the bow: lower the Sun.')+label(18,120,'The ray path still exists;')+label(18,149,'this rain field does not supply it.'),340,300,'No selected droplet for the current geometry');}
function cone(observer=0,elevation=15){const st=observerState(observer,elevation),{o,beta,k,drops}=st,P=project;let s=label(20,28,'SPACE VIEW · directions, not a glowing shell');
 const floor=[[-4,-1,0],[4,-1,0],[4,8,0],[-4,8,0]];
 s+=`<polygon points="${floor.map(P).map(xy).join(' ')}" class="ground"/>`;
 const corners=[[-3.5,1.2,0],[3.5,1.2,0],[3.5,7.2,0],[-3.5,7.2,0],[-3.5,1.2,5],[3.5,1.2,5],[3.5,7.2,5],[-3.5,7.2,5]];
 for(const [a,b] of [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]])s+=line(P(corners[a]),P(corners[b]),'volume');
 const ring=Array.from({length:65},(_,j)=>add(o,mul(direction(elevation,beta,j*2*PI/64),5)));
 // Back-to-front transparent faces and sample drops use the same fixed camera.
 const faces=[];for(let j=0;j<64;j++)faces.push({pts:[o,ring[j],ring[j+1]],depth:dot(ring[j],forward)});
 faces.sort((a,b)=>b.depth-a.depth).forEach(f=>{s+=`<polygon points="${f.pts.map(P).map(xy).join(' ')}" class="cone-fill"/>`;});
 for(let j=0;j<64;j++)s+=line(P(ring[j]),P(ring[j+1]),ring[j][2]>=0?'cone-edge':'sight');for(let j=0;j<64;j+=8)s+=line(P(o),P(ring[j]),'sight');
 s+=arrow(P(o),P(add(o,mul(k,7))),'axis');
 const chosen=drops.filter(d=>d.selected).slice(0,8);
 drops.sort((a,b)=>dot(b.p,forward)-dot(a.p,forward)).forEach(d=>{s+=dotmark(P(d.p),d.selected?4:1.6,d.selected?'contributor':'rain-dot');});
 chosen.forEach(d=>s+=arrow(P(d.p),P(o),'return-ray'));
 for(const base of [[-3,2,4],[-1,2,4],[1,2,4]])s+=arrow(P(add(base,mul(k,-1))),P(base),'sunray');
 s+=label(24,63,'Parallel sunlight ↘');s+=label(425,83,'Rain at many distances');
 s+=label(450,345,'Antisolar axis');s+=label(22,461,'Normalized distances · samples in 1° inside the cone edge');
 for(const [tag,pos] of [['A',[0,0,.1]],['B',[1.2,0,.1]]]){const p=P(pos);s+=dotmark(p,tag===(observer?'B':'A')?13:6,tag===(observer?'B':'A')?'eye':'station');s+=label(p[0]-6,p[1]+34,tag,'observer-letter');}
 const ep=P(o);s+=label(ep[0]-100,ep[1]+60,'01 · YOU','observer-label');
 if(chosen.length){const p=P(chosen[0].p);s+=label(p[0]+9,p[1]-10,'D');}
 return svg(s,700,480,'Your rainbow: a viewing cone with your eye at its apex','Move from A to B to change the fixed sampled drops selected by the viewing angle. Sunlight is parallel. The wireframe is a direction construction, not a material object.');
}
function side(observer=0,elevation=15){const {beta}=observerState(observer,elevation),o=[54+observer*16,210],R=210;let s=label(16,26,'SIDE SECTION · observer 01');
 const pt=a=>[o[0]+R*Math.cos(rad(a)),o[1]-R*Math.sin(rad(a))];
 s+=line([16,218],[326,218],'horizon')+label(215,242,'ground');
 s+=line(o,pt(-elevation),'axis')+line(o,pt(beta-elevation),'sight');const lower=clipSegment(o,pt(-beta-elevation),[0,40,340,273]);if(lower)s+=line(...lower,'sight');
 s+=angleArc(o,[Math.cos(rad(-elevation)),-Math.sin(rad(-elevation))],[Math.cos(rad(beta-elevation)),-Math.sin(rad(beta-elevation))],72,'β ≈ 42°');
 s+=dotmark(o,10,'eye')+label(o[0]-10,193,observer?'B':'A');s+=label(20,300,`Top: ${(beta-elevation).toFixed(1)}° above horizon`);
 s+=label(150,64,'rain ahead');s+=label(140,104,'cone edge');
 return svg(s,340,325,'Side section of the viewing cone','The antisolar axis lies below the horizontal by the Sun elevation. The top of the primary is beta minus that elevation.');
}
function sky(observer=0,elevation=15){const st=observerState(observer,elevation),{beta,drops}=st,projectSky=v=>[170+v[0]*170,180-v[2]*170],c=projectSky(st.k);let s=label(16,25,'SKY VIEW · observer '+(observer?'B':'A'));
 const colors=['#D94B54','#E58A37','#E8BE49','#4AAB82','#478ED1','#8A6BD1'];
 s+='<defs><clipPath id="sky-clip"><rect x="8" y="34" width="324" height="145"/></clipPath></defs><g clip-path="url(#sky-clip)">';
 colors.forEach((color,j)=>{const points=Array.from({length:121},(_,k)=>projectSky(direction(elevation,beta-j*.32,k*2*PI/120)));s+=`<path d="M${points.map(xy).join(' L')}" fill="none" stroke="${color}" stroke-width="2"/>`;});
 drops.filter(d=>d.selected).forEach((d,j)=>{const v=unit(add(d.p,mul(st.o,-1)));if(v[1]>0){const p=projectSky(v);s+=dotmark(p,2.5,'sky-sample');if(j===0)s+=label(p[0]+5,p[1]-10,'D');}});s+='</g>';
 s+=line([8,180],[332,180],'horizon')+label(18,202,'horizon');s+=line([170,178],[c[0],Math.min(c[1],224)],'axis');if(c[1]<=224)s+=dotmark(c,3);s+=label(18,251,`Sun ${elevation}° · apex ${(beta-elevation).toFixed(1)}°`);
 return svg(s,340,260,'Sky inset: the primary arc is clipped by the horizon','Orthographic projection toward the horizontal forward direction; dots mark selected sample directions, not simulated brightness.');
}
function deflection(b=.860663,n=4/3){const w=560,h=400,P=(u,D)=>[64+u*464,320-(D-135)*5.4];let s=label(18,27,'ANGULAR PLOT · primary ray family');
 for(const d of [140,160,180]){s+=line(P(0,d),P(1,d),'gridline')+label(18,P(0,d)[1]+5,d+'°');}
 for(const u of [0,.5,1])s+=label(P(u,135)[0]-8,345,String(u));
 const pts=Array.from({length:201},(_,j)=>{const u=j/200;return P(u,180+2*deg(Math.asin(u))-4*deg(Math.asin(u/n)));});s+=path(pts,'graph');
 const g=stationary(n);s+=line(P(g.b,135),P(g.b,g.D),'sight');s+=dotmark(P(g.b,g.D),5,'contributor');
 const D=180+2*deg(Math.asin(b))-4*deg(Math.asin(b/n));s+=dotmark(P(b,D),7,'selected-point');
 s+=label(100,100,`Minimum θ = ${g.D.toFixed(2)}°`)+label(100,125,`Radius β = ${g.beta.toFixed(2)}°`)+label(155,380,'Normalized impact parameter b/a');
 return svg(s,w,h,'Deflection versus normalized impact parameter','The minimum deflection sets the maximum primary radius. The highlighted point follows the selected ray; it is not always the caustic.');
}
function wave(data,radius=100,showAiry=true,showMie=true,polar=false,compact=false){const c=data.cases[String(radius)],w=compact?350:700,h=370;
 const point=(beta,v)=>[(compact?42:64)+(beta-35)*(compact?36:75),294-v*220];
 let s=label(18,26,compact?(polar?'POLARIZATION':'MONOCHROMATIC · 650 nm'):(polar?'POLARIZATION · shared intensity scale':'ANGULAR PLOT · independently normalized shapes'));
 const perMax=Math.max(...c.perpendicular),aiMax=Math.max(...c.airy);
 for(const v of [0,.5,1])s+=line(point(35,v),point(43,v),'gridline')+label(8,point(35,v)[1]+5,String(v));
 for(const beta of [35,37,39,41,43])s+=label(point(beta,0)[0]-12,320,beta+'°');
 function curve(arr,max,cls){return path(arr.map((v,j)=>point(35+j*.01,v/max)),cls);}
 if(polar){s+=curve(c.perpendicular,perMax,'mie')+curve(c.parallel,perMax,'parallel');}
 else{if(showMie)s+=curve(c.perpendicular,perMax,'mie');if(showAiry)s+=curve(c.airy,aiMax,'airy');}
 s+=line(point(data.geometry.beta,0),point(data.geometry.beta,1.05),'sight');s+=label(compact?110:460,54,'ray edge '+data.geometry.beta.toFixed(2)+'°');
 s+=label(compact?35:135,355,compact?'β: radius from antisolar axis':'β: angular radius from the antisolar axis');
 return svg(s,w,h,polar?'Perpendicular and parallel Mie intensities':'Airy approximation and full sphere scattering','Monochromatic 650 nm. Sphere radius '+radius+' micrometers, index 1.332, exterior index one. The dashed Airy curve is a qualitative single-family approximation.');
}
function skySlice(compact=false){let s=label(18,28,compact?'RADIAL SKY SLICE':'RADIAL SKY SLICE · outward from antisolar point');const P=b=>(compact?22:48)+(b-35)*(compact?14:25);
 s+=`<rect x="${P(42.3)}" y="64" width="${P(50.6)-P(42.3)}" height="100" class="dark-band"/>`;
 const colors=['#8A6BD1','#478ED1','#4AAB82','#E8BE49','#E58A37','#D94B54'];colors.forEach((c,j)=>{s+=`<rect x="${P(40+j*.4)}" y="64" width="${compact?5.6:10}" height="100" fill="${c}"/><rect x="${P(50.6+j*.6)}" y="64" width="${compact?8.4:15}" height="100" fill="${colors[5-j]}"/>`;});
 [35,40,45,50,55].forEach(b=>s+=label(P(b)-8,193,b+'°'));s+=label(compact?55:146,224,'primary')+label(compact?134:314,112,'less light')+label(compact?134:314,138,'≠ no light')+label(compact?225:450,224,'secondary');return svg(s,compact?350:600,254,'Primary and secondary color order with Alexander’s band between','Schematic colors and brightness. Violet is inside the primary; red is inside the secondary.');
}
function density(compact=false){const w=compact?350:700,P=(beta,rho)=>[(compact?42:64)+(beta-40)*(compact?96:190),215-rho*30],edge=42.2237504138;let s=label(18,26,'RAY DENSITY · the geometric limit');
 for(const y of [0,1,3,5])s+=line(P(40,y),P(43,y),'gridline')+label(10,P(40,y)[1]+5,String(y));
 for(const beta of [40,41,42,43])s+=label(P(beta,0)[0]-10,240,beta+'°');
 const pts=Array.from({length:180},(_,j)=>{const beta=40+(edge-.04-40)*j/179;return P(beta,1/Math.sqrt(edge-beta));});s+=path(pts,'graph');s+=line(P(edge,0),P(edge,5.5),'sight');s+=label(compact?190:450,48,'→ ∞');s+=label(compact?35:180,274,'β: radius from antisolar axis');
 return svg(s,w,295,'Ray-density divergence near the primary edge','Local fold Jacobian proportional to one over the square root of beta R minus beta. Scale chosen as one at one degree inside; not absolute brightness. The trace is clipped above five, and diverges at the edge.');}
function elevated(){const P=v=>[175+v[0]*135,116-v[2]*135],beta=stationary(1.3316655570438782).beta;let s=label(16,26,'ELEVATED OBSERVER · Sun 15°');
 const colors=['#D94B54','#E58A37','#E8BE49','#4AAB82','#478ED1','#8A6BD1'];colors.forEach((c,j)=>{const pts=Array.from({length:121},(_,i)=>P(direction(15,beta-j*.32,i*2*PI/120)));s+=`<path d="M${pts.map(xy).join(' L')}" fill="none" stroke="${c}" stroke-width="2"/>`;});
 s+=line([10,116],[340,116],'horizon')+label(12,104,'eye-level horizon');s+=dotmark(P([0,Math.cos(rad(15)),-Math.sin(rad(15))]),4);s+=label(35,259,'Drops below you can complete it.');
 return svg(s,350,290,'Elevated observer: the full circle can extend below eye level','Orthographic sky projection. The full bow is possible only where rain or spray supplies every sight direction. No ground clipping is applied to this elevated-observer example.');}
// Hero bow: a physically shaped radial gradient. Angular radii come from stationary(n(λ)) for the
// primary (p=2) and secondary (p=3); n(λ) interpolates the three IAPWS presets on a 1/λ² basis.
const presetN=[[450,1.3396055544134375],[550,1.3346802542039415],[650,1.3316655570438782]];
function indexAt(nm){const x=1/(nm*nm),xs=presetN.map(([l])=>1/(l*l));let n=0;for(let i=0;i<3;i++){let L=presetN[i][1];for(let j=0;j<3;j++)if(j!==i)L*=(x-xs[j])/(xs[i]-xs[j]);n+=L;}return n;}
function spectrum(nm){let r=0,g=0,b=0;if(nm<440){r=(440-nm)/60;b=1;}else if(nm<490){g=(nm-440)/50;b=1;}else if(nm<510){g=1;b=(510-nm)/20;}else if(nm<580){r=(nm-510)/70;g=1;}else if(nm<645){r=1;g=(645-nm)/65;}else r=1;
 const f=nm<420?.45+.55*(nm-400)/20:nm>680?.55+.45*(700-nm)/20:1;return [r,g,b].map(c=>Math.round(255*(.08+.92*Math.pow(c*f,.8))));}
function heroBow(){const W=1000,H=700,cx=500,cy=780,k=11,rMax=56,stop=(beta,rgb,a)=>({beta,rgb,a});
 const primary=[],secondary=[];for(let nm=400;nm<=700;nm+=5){const n=indexAt(nm),rgb=spectrum(nm),w=Math.exp(-Math.pow((nm-560)/110,2)),a=.32+.58*Math.sqrt(w);primary.push(stop(stationary(n,2).beta,rgb,a));secondary.push(stop(stationary(n,3).beta,rgb,a*.42));}
 const pv=primary[0].beta,pr=primary[primary.length-1].beta,sr=Math.min(...secondary.map(s=>s.beta)),sv=Math.max(...secondary.map(s=>s.beta));
 const white=[255,250,240];
 const bright=[stop(0,white,.05),stop(pv-6,white,.07),stop(pv-2.2,white,.11),
  stop(pv-1.35,[190,255,215],.2),stop(pv-1.05,white,.12),stop(pv-.75,[255,190,225],.3),stop(pv-.42,white,.16),stop(pv-.14,[200,180,255],.36),
  ...primary,stop(pr+.18,primary[primary.length-1].rgb,.4),stop(pr+.45,[255,120,90],0),
  stop(sr-.45,[255,120,90],0),stop(sr-.15,secondary.find(s=>s.beta===sr).rgb,.15),...secondary,stop(sv+.2,[150,120,255],.1),stop(sv+.55,[150,120,255],0),stop(rMax,white,0)].sort((a,b)=>a.beta-b.beta);
 const dark=[10,22,40],band=[stop(0,dark,0),stop(pr+.35,dark,0),stop(pr+1.1,dark,.34),stop(sr-.9,dark,.3),stop(sr-.25,dark,0),stop(sv+.3,dark,0),stop(sv+1.2,dark,.14),stop(rMax,dark,.14)];
 const stops=list=>list.map(s=>`<stop offset="${(s.beta/rMax).toFixed(4)}" stop-color="rgb(${s.rgb.join(' ')})" stop-opacity="${s.a.toFixed(2)}"/>`).join('');
 const grad=(id,list)=>`<radialGradient id="${id}" gradientUnits="userSpaceOnUse" cx="${cx}" cy="${cy}" r="${rMax*k}">${stops(list)}</radialGradient>`;
 const open=(cls,extra='')=>`<svg class="${cls}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMax meet" aria-hidden="true" ${extra}>`;
 // The sheet overshoots the viewBox so the hero (overflow hidden) clips it, not the SVG box.
 const sheet=(fill,extra='')=>`<rect x="-1500" y="-1500" width="4000" height="3000" fill="${fill}" ${extra}/>`;
 const bow=open('hero-bow')+`<defs>${grad('hero-bow-grad',bright)}<linearGradient id="hero-bow-fade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="${H}"><stop offset="0" stop-color="#fff"/><stop offset=".6" stop-color="#fff"/><stop offset=".82" stop-color="#8a8a8a"/><stop offset="1" stop-color="#222"/></linearGradient><mask id="hero-bow-mask" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="5000" height="5000">${sheet('url(#hero-bow-fade)')}</mask></defs>${sheet('url(#hero-bow-grad)','mask="url(#hero-bow-mask)"')}</svg>`;
 const shade=open('hero-band')+`<defs>${grad('hero-band-grad',band)}</defs>${sheet('url(#hero-band-grad)')}</svg>`;
 return {bow,shade,primary:[pv,pr],secondary:[sr,sv]};}
const api={rad,deg,add,mul,dot,unit,refract,reflect,next,trace,stationary,project,direction,observerState,observerDrop,impactForBeta,svg,drop,cone,side,sky,deflection,wave,skySlice,density,elevated,indexAt,spectrum,heroBow};
if(typeof module!=='undefined')module.exports=api;else root.Rainbow=api;
})(typeof window!=='undefined'?window:globalThis);
