const page = await figma.getNodeByIdAsync(PAGE_ID);
await figma.setCurrentPageAsync(page);
await Promise.all(['Regular','Medium','SemiBold','Bold'].map(style=>figma.loadFontAsync({family:'Manrope',style})));
const vars=await figma.variables.getLocalVariablesAsync();
const vm=Object.fromEntries(vars.map(v=>[v.name,v]));
const rgb=hex=>({r:parseInt(hex.slice(1,3),16)/255,g:parseInt(hex.slice(3,5),16)/255,b:parseInt(hex.slice(5,7),16)/255});
const palette=PALETTE;
const paint=k=>figma.variables.setBoundVariableForPaint({type:'SOLID',color:rgb(palette[k]||palette.ink)},'color',vm['color/'+k]);
const created=[], mutated=[], out={};
const nodeMap={...NODE_MAP};
function metric(n,field,value,kind='space'){n[field]=value;const v=vm[kind+'/'+value];if(v)n.setBoundVariable(field,v);}
function layout(n,s) {
 n.name=s.name||s.type; n.fills=s.fill?[paint(s.fill)]:[];
 if(s.stroke){n.strokes=[paint(s.stroke)];n.strokeWeight=1;}
 n.resize(s.width||300,s.height||1);
 if(s.type!=='rect'&&s.type!=='photo') {
 n.layoutMode=s.dir||'VERTICAL';
 if(n.layoutMode!=='NONE'){
 const vertical=n.layoutMode==='VERTICAL';
 n.primaryAxisSizingMode=vertical&&!s.height?'AUTO':'FIXED';
 n.counterAxisSizingMode=!vertical&&!s.height?'AUTO':'FIXED';
 n.primaryAxisAlignItems=s.justify||'MIN';n.counterAxisAlignItems=s.align||'MIN';
 metric(n,'itemSpacing',s.gap||0);
 for(const field of ['paddingLeft','paddingRight'])metric(n,field,s.padX??s.padding??0);
 for(const field of ['paddingTop','paddingBottom'])metric(n,field,s.padY??s.padding??0);
 }
 }
 metric(n,'cornerRadius',s.radius||0,'radius');
 n.clipsContent=!!s.clip;
}
function setPhoto(n,index) {
 const crops=[[360,411,504,215],[884,411,530,215],[360,735,504,177],[884,735,530,177]];
 const [x,y,w,h]=crops[index||0];
 n.fills=[{type:'IMAGE',imageHash:'57989daa658a27c25603ccd3ebbe8456565e1eda',scaleMode:'CROP',imageTransform:[[w/1478,0,x/1478],[0,h/1064,y/1064]]}];
}
for(const op of OPS) {
 const s=op.spec; let n;
 const parent=nodeMap[op.parent]?await figma.getNodeByIdAsync(nodeMap[op.parent]):page;
 if(s.type==='text'){
 n=figma.createText();n.name=s.name||s.text.slice(0,50);n.fontName={family:'Manrope',style:s.weight||'Regular'};n.fontSize=s.size||16;n.characters=s.text;
 n.lineHeight={unit:'PIXELS',value:Math.ceil((s.size||16)*((s.size||16)>=32?1.2:1.45))};
 n.fills=[paint(s.color||'ink')];
 if(s.width){n.textAutoResize='HEIGHT';n.resize(s.width,1);}
 else n.textAutoResize='WIDTH_AND_HEIGHT';
 if(s.textAlign)n.textAlignHorizontal=s.textAlign;
 } else if(s.type==='instance'){
 const main=await figma.getNodeByIdAsync(COMP_MAP[s.ref]);n=main.createInstance();n.name=s.name||s.ref;
 if(s.width||s.height)n.resize(s.width||n.width,s.height||n.height);
 const ts=n.findAllWithCriteria({types:['TEXT']});
 for(const t of ts){if(s.labels&&Object.hasOwn(s.labels,t.name)){t.characters=s.labels[t.name];mutated.push(t.id);}}
 if(s.fill)n.fills=[paint(s.fill)];
 if(s.photo!==undefined){const photo=n.findOne(z=>z.name==='Photo');if(photo&&'fills'in photo){setPhoto(photo,s.photo);mutated.push(photo.id);}}
 if(s.statusFill){const badge=n.findOne(z=>z.name==='Status');if(badge&&'fills'in badge){badge.fills=[paint(s.statusFill)];mutated.push(badge.id);}}
 if(s.textColor)for(const t of ts){t.fills=[paint(s.textColor)];mutated.push(t.id);}
 }else if(s.type==='photo'||s.type==='rect'){
 n=figma.createRectangle();n.name=s.name||'Photo';n.resize(s.width,s.height);n.fills=s.fill?[paint(s.fill)]:[];metric(n,'cornerRadius',s.radius||0,'radius');if(s.type==='photo')setPhoto(n,s.photo);
 }else if(s.type==='svg'){
 n=figma.createNodeFromSvg(s.svg);n.name=s.name||'Icon';
 }else if(s.type==='component'){
 n=figma.createComponent();layout(n,s);n.description=s.description||'Редактируемый компонент интерфейса Маэстро.';
 }else {
 n=figma.createAutoLayout(s.dir==='NONE'?'VERTICAL':s.dir||'VERTICAL');layout(n,s);
 }
 parent.appendChild(n);
 if(s.abs){n.layoutPositioning='ABSOLUTE';n.x=s.x||0;n.y=s.y||0;}
 if(parent.type==='PAGE'){n.x=s.x??200;n.y=s.y??0;}
 if(s.opacity!==undefined)n.opacity=s.opacity;
 created.push(n.id);
 if('findAll'in n&&s.type==='instance')for(const d of n.findAll(()=>true))created.push(d.id);
 nodeMap[op.key]=n.id;out[op.key]=n.id;
}
return {createdNodeIds:created,mutatedNodeIds:mutated,nodeMap:out,checks:await Promise.all(Object.values(out).map(async id=>{const n=await figma.getNodeByIdAsync(id);return {id,name:n.name,width:n.width,height:n.height};}))};
