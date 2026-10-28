import {readFile} from 'node:fs/promises';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {parse} from 'smol-toml';
const config=process.argv[2];let c;
try{
 const entry=parse(await readFile(config,'utf8')).mcp_servers?.niio_local_mcp;if(!entry||entry.enabled===false)throw Error();
 c=new Client({name:'niio-user-readonly-acceptance',version:'1'});
 const t=new StdioClientTransport({command:entry.command,args:entry.args,cwd:entry.cwd,env:{...process.env,...entry.env},stderr:'pipe'});
 // Never print child stderr: errors must not disclose credential material.
 t.stderr?.on('data',()=>{});
 await c.connect(t);const tools=(await c.listTools()).tools;
 if(!tools.some(x=>x.name==='get_current_user'))throw Error();
 const response=await c.callTool({name:'get_current_user',arguments:{}});
 if(response.isError)throw Error();let data=JSON.parse(response.content.find(x=>x.type==='text').text);
 while(data?.data){if(data.success===false)throw Error();data=data.data;}
 if(!data.accountId)throw Error();
 console.log(JSON.stringify({passed:true,readOnly:true,toolCount:tools.length,server:c.getServerVersion(),currentCallerAccepted:true}));
}catch{console.error('NIIO_VERIFY_FAILED_CHECK_AUTH_AND_UPSTREAM');process.exitCode=1;}
finally{await c?.close();}
