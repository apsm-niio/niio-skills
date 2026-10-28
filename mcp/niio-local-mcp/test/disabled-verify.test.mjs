import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,access,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

test('verification never launches an explicitly disabled service',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'niio-disabled-verifier-'));
 try{
  const marker=join(dir,'launched');
  const config=join(dir,'config.toml');
  const script=join(dir,'synthetic.mjs');
  await writeFile(script,`import {writeFileSync} from 'node:fs';writeFileSync(${JSON.stringify(marker)},'unexpected');`);
  await writeFile(config,`[mcp_servers.niio_local_mcp]\nenabled = false\ncommand = ${JSON.stringify(process.execPath)}\nargs = [${JSON.stringify(script)}]\n`);
  const r=spawnSync(process.execPath,[fileURLToPath(new URL('../scripts/verify.mjs',import.meta.url)),config],{encoding:'utf8',timeout:10000});
  assert.equal(r.status,1);
  assert.match(r.stderr,/NIIO_VERIFY_FAILED/);
  await assert.rejects(access(marker));
 }finally{await rm(dir,{recursive:true,force:true});}
});
