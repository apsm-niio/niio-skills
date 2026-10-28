import Ajv from 'ajv';
import { pathToFileURL } from 'node:url';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { connectUpstream } from './upstream.mjs';
import { NiioService, ServiceError, errorResult } from './service.mjs';

export async function createServer(client, identity = {name:'niio-local-mcp',version:'0.2.0'}, {filterMetadataSupport=false}={}) {
  const tools=[]; let cursor;
  do {
    const page=await client.listTools(cursor ? {cursor}:{});
    tools.push(...page.tools); cursor=page.nextCursor;
  } while(cursor);
  if(filterMetadataSupport){
    const tool=tools.find(t=>t.name==='save_worksheet_filter');
    if(tool){tool.inputSchema=structuredClone(tool.inputSchema);Object.assign(tool.inputSchema.properties,{
      name:{type:'string',description:'篩選器名稱。更新省略時保留原名稱。'},
      type:{type:'integer',enum:[1,2],description:'1 個人、2 公共。更新省略時保留原範圍；新建具名稱篩選器請明確指定。'},
      module:{type:'integer',enum:[1,2,3],description:'1 工作表可見篩選器、2 統計條件、3 知識條件。更新保留原模組。'}
    });tool.description+=' 修補測試版：支援名稱與範圍；更新省略時由 API 讀取並保留既有值。';}
  }
  const ajv=new Ajv({strict:false,allErrors:true,validateFormats:false});
  const validators=new Map(tools.map(tool=>[tool.name,ajv.compile(tool.inputSchema)]));
  const service=new NiioService(client);
  const server=new Server(identity,{capabilities:{tools:{}}});
  server.setRequestHandler(ListToolsRequestSchema,async()=>({tools:tools.map(t=>{
    if(t.name==='get_record_list') return {...t, description:t.description+' 本機版：明確 fields 的 JSON 清單會在相同行選取範圍內讀取有權限的詳情，以完整回傳指定欄位；多次讀取非原子快照。'};
    if(t.name==='save_worksheet_filter'&&!filterMetadataSupport) return {...t,description:t.description+' 本部署實測：省略 filterId 會建立 module=2 條件設定，未建立具名稱／個人或公共範圍的可見篩選器；本工具目前沒有 name/scope 參數。已確認上游缺陷：更新 module=1 可見篩選器會清空名稱，額外傳 name 也無效；尚未修復，不得宣稱能保留名稱。'};
    return t;
  })}));
  server.setRequestHandler(CallToolRequestSchema,async(request,extra)=>{
    try {
      const validate=validators.get(request.params.name);
      if(!validate) throw new ServiceError('UNKNOWN_TOOL','找不到工具。');
      if(!validate(request.params.arguments??{})) throw new ServiceError('INVALID_ARGUMENTS','工具參數不符合結構。',{
        paths:validate.errors.map(e=>({path:e.instancePath,keyword:e.keyword}))
      });
      return await service.call(request.params.name,request.params.arguments??{},extra.signal);
    } catch(error) { return errorResult(error); }
  });
  return server;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const {client}=await connectUpstream();
    const server=await createServer(client);
    server.onclose=()=>{void client.close();};
    await server.connect(new StdioServerTransport());
  } catch { process.stderr.write('niio-local-mcp: startup failed; check upstream connection and local configuration.\n'); process.exitCode=1; }
}
