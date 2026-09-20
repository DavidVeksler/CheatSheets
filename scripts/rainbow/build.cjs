// Embed calculated static SVG and runtime sources into the standalone HTML.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const dir=__dirname,root=path.resolve(dir,'../..'),R=require('./optics.js'),data=require('./data.json');
const file=path.join(root,'how-do-rainbows-work.html');let html=fs.readFileSync(file,'utf8');
const red=data.ray_presets[0].n,b=R.stationary(red).b;
const hero=R.heroBow();
const figures={
 'hero-band':hero.shade,'hero-bow':hero.bow,
 'trace-figure':R.drop(),'cone-figure':R.cone(),'full-cone':R.cone(),'sky-figure':R.sky(),'side-figure':R.side(),'inset-figure':R.observerDrop(),
 'ray-figure':R.drop(b,red,1,true),'deflection-figure':R.deflection(b,red),
 'primary-figure':R.drop(),'secondary-figure':R.drop(R.stationary(4/3,3).b,4/3,2),'sky-slice':R.skySlice(),'sky-slice-mobile':R.skySlice(true),
 'density-figure':R.density(),'density-mobile':R.density(true),
 'elevated-figure':R.elevated(),
 'wave-figure':R.wave(data),'wave-mobile':R.wave(data,100,true,true,false,true),
 'polarization-figure':R.wave(data,100,true,true,true),'polarization-mobile':R.wave(data,100,true,true,true,true)
};
for(const [id,value] of Object.entries(figures)){const start=`<!-- FIG:${id} -->`,end=`<!-- /FIG:${id} -->`;const a=html.indexOf(start),b=html.indexOf(end);if(a<0||b<0)throw Error('Missing slot '+id);html=html.slice(0,a+start.length)+value+html.slice(b);}
const js=fs.readFileSync(path.join(dir,'optics.js'),'utf8')+'\n'+fs.readFileSync(path.join(dir,'app.js'),'utf8');
const app=`<script type="application/json" id="rainbow-data">${JSON.stringify(data)}</script>\n<script>\n${js}\n</script>`;
html=html.replace(/<!-- APP:begin -->[\s\S]*?<!-- APP:end -->/,'<!-- APP:begin -->\n'+app+'\n<!-- APP:end -->');
fs.writeFileSync(file,html);
const css=html.match(/@layer figures \{([\s\S]*?)\n\}/)[1];
const exportSvg=R.svg(`<style>svg{color-scheme:light;--ink:#142538;--muted:#46566b;--line:#c8d5de;--bench:#fffef9;--blue:#28699f;--accent:#8d3140;--gold:#8b5313}${css}</style><rect width="1100" height="720" fill="#f7f4ec"/><text x="35" y="60" style="font:42px Georgia;fill:#142538">Your rainbow.</text><text x="35" y="96" style="font:18px system-ui;fill:#46566b">One eye. A circle of directions. A different set of drops.</text><g transform="translate(0 140)">${R.cone().replace('<svg ','<svg width="730" height="500" ')}</g><g transform="translate(755 130)">${R.sky().replace('<svg ','<svg width="340" height="260" ')}</g><g transform="translate(755 370)">${R.observerDrop().replace('<svg ','<svg width="340" height="300" ')}</g><text x="35" y="693" style="font:16px system-ui;fill:#46566b">650 nm · Sun 15° · normalized distances · schematic colors · cheatsheets.davidveksler.com</text>`,1100,720,'Your rainbow: observer cone, sky view and drop path');
fs.mkdirSync(path.join(root,'images/how-do-rainbows-work'),{recursive:true});fs.writeFileSync(path.join(root,'images/how-do-rainbows-work/signature.svg'),exportSvg);
console.log(JSON.stringify({html_bytes:Buffer.byteLength(html),gzip_bytes:zlib.gzipSync(html).length,application_js_bytes:Buffer.byteLength(js),computed_data_bytes:Buffer.byteLength(JSON.stringify(data))},null,2));
