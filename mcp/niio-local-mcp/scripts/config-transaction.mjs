import {readFile,writeFile,rename,unlink,mkdir,stat} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {parse,stringify} from 'smol-toml';
const BEGIN='# >>> niio-skills local MCP managed',END='# <<< niio-skills local MCP managed';
const hash=s=>createHash('sha256').update(s).digest('hex');
const lf=s=>s.replace(/\r\n/g,'\n');
const text=async p=>readFile(p,'utf8').catch(e=>{if(e.code==='ENOENT')return '';throw e;});
const normalize=o=>{const n=structuredClone(o);if(n.mcp_servers){delete n.mcp_servers.niio_local_mcp;if(!Object.keys(n.mcp_servers).length)delete n.mcp_servers;}return n;};
const canonical=x=>JSON.stringify(x,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
function managed(s){
 const a=s.indexOf(BEGIN),z=s.indexOf(END);if(a<0&&z<0)return null;
 if(a<0||z<a||s.indexOf(BEGIN,a+1)>=0||s.indexOf(END,z+1)>=0)throw Error('MANAGED_BLOCK_INVALID');
 return{start:a,end:z+END.length,body:s.slice(a,z+END.length)};
}
function removeLegacy(s){
 const headers=[...s.matchAll(/^\s*\[([^\]\r\n]+)\][ \t]*(?:#[^\r\n]*)?\r?$/gm)];
 let result='',previous=0,removed='';
 for(let i=0;i<headers.length;i++){
  const h=headers[i],name=h[1].replace(/["']/g,'').replace(/\s/g,'');
  if(name==='mcp_servers.niio_local_mcp'||name.startsWith('mcp_servers.niio_local_mcp.')){
   const end=headers[i+1]?.index??s.length;result+=s.slice(previous,h.index);removed+=s.slice(h.index,end);previous=end;
  }
 }
 result+=s.slice(previous);if(!removed)throw Error('EXISTING_LOCAL_ENTRY_NOT_IDENTIFIABLE');return{result,removed};
}
async function atomic(path,value,expected){
 await mkdir(dirname(path),{recursive:true});const tmp=path+'.niio-'+randomUUID()+'.tmp';
 const mode=await stat(path).then(s=>s.mode&0o777).catch(()=>0o600);
 try{await writeFile(tmp,value,{flag:'wx',mode});if(await text(path)!==expected)throw Error('CONFIG_CHANGED_CONCURRENTLY');await rename(tmp,path);}
 finally{await unlink(tmp).catch(()=>{});}
}
export async function run(a){
 if(a.op==='prepare'){
  const original=await text(a.path),before=parse(original);let basis=original,oldBlock='',oldKind='absent';const m=managed(original);
  if(m){oldBlock=m.body;oldKind='managed';basis=original.slice(0,m.start)+original.slice(m.end);}
  else if(before.mcp_servers?.niio_local_mcp){if(!a.adopt)throw Error('EXISTING_LOCAL_ENTRY_REQUIRES_EXPLICIT_ADOPTION');const x=removeLegacy(original);basis=x.result;oldBlock=x.removed;oldKind='legacy';}
  const entry=structuredClone(a.entry);
  const policy=before.mcp_servers?.niio_local_mcp??before.mcp_servers?.niio_personal_mcp;
  for(const k of ['default_tools_approval_mode','tools','enabled_tools','disabled_tools'])if(policy?.[k]!==undefined)entry[k]=structuredClone(policy[k]);
  // Adopting or updating an explicitly disabled local service must not enable it.
  if(before.mcp_servers?.niio_local_mcp?.enabled!==undefined)entry.enabled=before.mcp_servers.niio_local_mcp.enabled;
  const block=BEGIN+'\n'+stringify({mcp_servers:{niio_local_mcp:entry}}).trimEnd()+'\n'+END;
  const updated=m?original.slice(0,m.start)+block+original.slice(m.end):basis+(basis.endsWith('\n')?'':'\n')+'\n'+block+'\n';
  if(canonical(normalize(parse(updated)))!==canonical(normalize(before)))throw Error('UNRELATED_CONFIG_WOULD_CHANGE');
  await writeFile(join(a.dir,'config.before.toml'),original,{mode:0o600});
  await writeFile(join(a.dir,'config.after.toml'),updated,{mode:0o600});
  await writeFile(join(a.dir,'block.before.txt'),oldBlock,{mode:0o600});
  await writeFile(join(a.dir,'block.after.txt'),block,{mode:0o600});
  return{originalHash:hash(original),updatedHash:hash(updated),blockHash:hash(block),oldBlockHash:hash(oldBlock),oldKind,existed:await stat(a.path).then(()=>true).catch(()=>false)};
 }
 if(a.op==='apply'){
  const original=await text(join(a.dir,'config.before.toml')),updated=await text(join(a.dir,'config.after.toml'));
  if(hash(original)!==a.meta.originalHash||hash(updated)!==a.meta.updatedHash)throw Error('CONFIG_BACKUP_CHANGED');
  await atomic(a.path,updated,original);return{applied:true};
 }
 if(a.op==='check'||a.op==='restore'){
  const current=await text(a.path),m=managed(current),next=await text(join(a.dir,'block.after.txt')),previous=await text(join(a.dir,'block.before.txt'));
  const old=await text(join(a.dir,'config.before.toml'));
  const planned=await text(join(a.dir,'config.after.toml'));
  if(hash(old)!==a.meta.originalHash||hash(planned)!==a.meta.updatedHash||hash(lf(next))!==a.meta.blockHash||hash(previous)!==a.meta.oldBlockHash)throw Error('CONFIG_BACKUP_CHANGED');
  const isNext=!!m&&lf(m.body)===lf(next);
  const isOld=a.meta.oldKind==='managed'?!!m&&lf(m.body)===lf(previous):canonical(parse(current).mcp_servers?.niio_local_mcp??null)===canonical(parse(old).mcp_servers?.niio_local_mcp??null);
  if(!isNext&&!isOld)throw Error('CUSTOMIZED_MCP_CONFIG_BLOCKS_RESTORE');
  if(a.op==='check'||isOld&&!isNext)return{valid:true,alreadyRestored:isOld&&!isNext};
  const replacement=previous;
  const restored=current===planned?old:current.slice(0,m.start)+replacement+current.slice(m.end);
  if(canonical(normalize(parse(restored)))!==canonical(normalize(parse(current))))throw Error('UNRELATED_CONFIG_WOULD_CHANGE');
  if(!a.meta.existed&&!restored.trim()){if(await text(a.path)!==current)throw Error('CONFIG_CHANGED_CONCURRENTLY');await unlink(a.path);}
  else await atomic(a.path,restored,current);
  return{restored:true};
 }
 if(a.op==='verify'){
  const current=await text(a.path),m=managed(current);return{managed:!!m,blockHash:m?hash(lf(m.body)):null,entry:parse(current).mcp_servers?.niio_local_mcp??null};
 }
 throw Error('UNKNOWN_CONFIG_OPERATION');
}
if(process.argv[1]?.endsWith('config-transaction.mjs')){
 let input='';for await(const chunk of process.stdin)input+=chunk;
 try{console.log(JSON.stringify(await run(JSON.parse(input))));}catch(e){console.error(e.message.match(/^[A-Z_]+$/)?.[0]??'CONFIG_OPERATION_FAILED');process.exitCode=1;}
}
