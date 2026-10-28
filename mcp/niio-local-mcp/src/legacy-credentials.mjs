import {readFile} from 'node:fs/promises';
import {homedir} from 'node:os';
import {join} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {parse} from 'smol-toml';
export const POWERSHELL=join(process.env.SystemRoot??'C:\\Windows','System32','WindowsPowerShell','v1.0','powershell.exe');
export const HEADER_SCRIPT=join(homedir(),'.codex','niio-secrets','get-niio-headers.ps1');
export const HEADER_COMMAND='"'+POWERSHELL+'" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+HEADER_SCRIPT+'"';
export async function currentHeaders(configPath) {
  const path=configPath??process.env.NIIO_CODEX_CONFIG??join(homedir(),'.codex','config.toml');
  const source=parse(await readFile(path,'utf8')).mcp_servers?.niio_personal_mcp;
  if(source?.url!=='https://niiodemo.apsm.com.tw/mcp')throw Error('UPSTREAM_CONFIG_MISMATCH');
  const headers={...source.http_headers};
  if(source.http_headers_helper){
    if(source.http_headers_helper!==HEADER_COMMAND)throw Error('UNRECOGNIZED_CREDENTIAL_HELPER');
    let result;
    try {result=await promisify(execFile)(POWERSHELL,['-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',HEADER_SCRIPT],{windowsHide:true,timeout:10000,maxBuffer:8192});}
    catch {throw Error('CREDENTIAL_HELPER_FAILED');}
    try {Object.assign(headers,JSON.parse(result.stdout));}catch {throw Error('CREDENTIAL_HELPER_FORMAT');}
  }
  for(const [key,envName]of Object.entries(source.env_http_headers??{})){
    if(!process.env[envName])throw Error('MISSING_UPSTREAM_HEADER_ENV');
    headers[key]=process.env[envName];
  }
  if(source.bearer_token_env_var){
    const token=process.env[source.bearer_token_env_var];if(!token)throw Error('MISSING_UPSTREAM_TOKEN_ENV');
    headers.Authorization='Bearer '+token;
  }
  if(!headers.Authorization)throw Error('MISSING_UPSTREAM_AUTHORIZATION');
  return headers;
}
