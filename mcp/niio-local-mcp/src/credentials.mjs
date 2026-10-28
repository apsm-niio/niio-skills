import {readFile} from 'node:fs/promises';
import {homedir} from 'node:os';
import {join,resolve} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {currentHeaders as legacyHeaders} from './legacy-credentials.mjs';
export async function currentHeaders(){
 const home=resolve(process.env.NIIO_LOCAL_HOME??join(homedir(),'.codex','niio-local-mcp'));
 const file=resolve(process.env.NIIO_LOCAL_CREDENTIAL_FILE??join(home,'auth.json'));
 try{
  const store=JSON.parse(await readFile(file,'utf8'));
  if(process.platform!=='win32'||store.version!==1||store.upstreamUrl!=='https://niiodemo.apsm.com.tw/mcp'||store.protection!=='windows-dpapi-current-user')throw Error('INVALID_CREDENTIAL_STORE');
  const command="$ErrorActionPreference='Stop';Add-Type -AssemblyName System.Security;$s=Get-Content -LiteralPath $env:NIIO_LOCAL_CREDENTIAL_FILE -Raw|ConvertFrom-Json;$b=[Convert]::FromBase64String($s.ciphertext);$p=[Security.Cryptography.ProtectedData]::Unprotect($b,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser);$t=[Text.Encoding]::UTF8.GetString($p);@{Authorization=('Bearer '+$t)}|ConvertTo-Json -Compress";
  const {stdout}=await promisify(execFile)(join(process.env.SystemRoot??'C:\\Windows','System32','WindowsPowerShell','v1.0','powershell.exe'),['-NoProfile','-NonInteractive','-EncodedCommand',Buffer.from(command,'utf16le').toString('base64')],{env:{...process.env,NIIO_LOCAL_CREDENTIAL_FILE:file},windowsHide:true,timeout:10000,maxBuffer:8192});
  const h=JSON.parse(stdout);if(!/^Bearer [^\s]{1,4096}$/.test(h.Authorization??''))throw Error('INVALID_CREDENTIAL');return{Authorization:h.Authorization};
 }catch(e){if(e.code!=='ENOENT')throw Error('CREDENTIAL_STORE_UNAVAILABLE');}
 if(process.env.NIIO_LOCAL_TOKEN){
  if(!/^[^\s]{1,4096}$/.test(process.env.NIIO_LOCAL_TOKEN))throw Error('INVALID_CREDENTIAL');
  return{Authorization:'Bearer '+process.env.NIIO_LOCAL_TOKEN};
 }
 if(process.env.NIIO_LEGACY_CODEX_CONFIG)return legacyHeaders(resolve(process.env.NIIO_LEGACY_CODEX_CONFIG));
 throw Error('AUTHENTICATION_NOT_CONFIGURED');
}
