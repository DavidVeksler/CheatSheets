const assert=require('node:assert/strict'),R=require('./optics.js');
const near=(a,b,t=1e-11)=>assert(Math.abs(a-b)<t,`${a} != ${b}`);
let count=0;
for(const n of [4/3,1.3396055544134375,1.3346802542039415,1.3316655570438782])for(const b of [0,.001,.5,.86,.95,.99])for(const reflections of [1,2]){
 const t=R.trace(b,n,reflections);t.points.forEach(p=>near(R.dot(p,p),1));near(R.dot(t.outgoing,t.outgoing),1);
 const i=Math.asin(b),r=Math.asin(b/n);near(Math.sin(i),n*Math.sin(r));
 near(-R.dot(t.inside,t.points[0]),Math.cos(r));
 for(let j=1;j<t.points.length;j++){
   const incoming=R.unit(R.add(t.points[j],R.mul(t.points[j-1],-1)));
   if(j<t.points.length-1){const outgoing=R.unit(R.add(t.points[j+1],R.mul(t.points[j],-1)));near(R.dot(incoming,t.points[j]),-R.dot(outgoing,t.points[j]));}
   else near(R.dot(t.outgoing,t.points[j]),Math.cos(i));
 }
 const D=reflections*Math.PI+2*i-2*(reflections+1)*r;near(t.beta,180-R.deg(Math.atan2(Math.abs(Math.sin(D)),Math.cos(D))),1e-9);count++;
}
const primary=R.stationary();near(primary.b,Math.sqrt(20/27));near(primary.beta,42.0296588656977,1e-10);near(R.stationary(4/3,3).beta,50.9780935256757,1e-10);
for(const e of [0,15,30,45,60])for(const observer of [0,1]){const s=R.observerState(observer,e);for(let j=0;j<12;j++)near(R.dot(R.direction(e,s.beta,j*Math.PI/6),s.k),Math.cos(R.rad(s.beta)));for(const d of s.drops.filter(d=>d.selected))near(R.trace(R.impactForBeta(d.angle,1.3316655570438782),1.3316655570438782).beta,d.angle,1e-9);assert(!/NaN|Infinity/.test(R.cone(observer,e)+R.sky(observer,e)+R.side(observer,e)+R.observerDrop(observer,e)));}
const A=R.observerState(0,15).drops.filter(d=>d.selected).map(d=>d.j),B=R.observerState(1,15).drops.filter(d=>d.selected).map(d=>d.j);assert.notDeepEqual(A,B);
assert(R.stationary(1.331665557).beta>R.stationary(1.339605554).beta);assert(R.stationary(1.331665557,3).beta<R.stationary(1.339605554,3).beta);
console.log(JSON.stringify({ray_cases:count,primary,secondary:R.stationary(4/3,3),observerA:A.length,observerB:B.length,result:'All geometry invariants passed'},null,2));
