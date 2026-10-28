import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {currentHeaders} from '../src/credentials.mjs';
import {connectUpstream} from '../src/upstream.mjs';
async function isolated(fn){
 const keys=['NIIO_LOCAL_HOME','NIIO_LOCAL_CREDENTIAL_FILE','NIIO_LOCAL_TOKEN','NIIO_LEGACY_CODEX_CONFIG'];
 const saved=Object.fromEntries(keys.map(k=>[k,process.env[k]]));
 const dir=await mkdtemp(join(tmpdir(),'niio-auth-unit-'));
 keys.forEach(k=>delete process.env[k]);process.env.NIIO_LOCAL_HOME=dir;
 try{await fn(dir);}finally{for(const k of keys){if(saved[k]===undefined)delete process.env[k];else process.env[k]=saved[k];}assert.ok(resolve(dir).startsWith(resolve(tmpdir())));await rm(dir,{recursive:true,force:true});}
}
test('fresh user fails closed without borrowing global credentials',async()=>isolated(async()=>{
 await assert.rejects(currentHeaders(),/AUTHENTICATION_NOT_CONFIGURED/);
}));
test('explicit process environment supports a per-user token without writing config',async()=>isolated(async()=>{
 process.env.NIIO_LOCAL_TOKEN='unit-test-not-a-real-token';assert.deepEqual(await currentHeaders(),{Authorization:'Bearer unit-test-not-a-real-token'});
}));
test('corrupt encrypted store never falls back to a different credential',async()=>isolated(async dir=>{
 process.env.NIIO_LOCAL_TOKEN='unit-test-not-a-real-token';await writeFile(join(dir,'auth.json'),'{');
 await assert.rejects(currentHeaders(),/CREDENTIAL_STORE_UNAVAILABLE/);
}));
test('legacy mode is explicit and refuses a different credential destination',async()=>isolated(async dir=>{
 const config=join(dir,'legacy.toml');await writeFile(config,'[mcp_servers.niio_personal_mcp]\nurl="https://attacker.invalid/mcp"\n');
 process.env.NIIO_LEGACY_CODEX_CONFIG=config;await assert.rejects(currentHeaders(),/UPSTREAM_CONFIG_MISMATCH/);
}));
test('bundled upstream rejects retired server test endpoints before auth or network',async()=>{
 await assert.rejects(connectUpstream({url:'http://niio-mcp-repair:8165/mcp'}),/UPSTREAM_DESTINATION_REJECTED/);
});
