import test from 'node:test';
import assert from 'node:assert/strict';
import {NiioService,validateFields,normalizeSingleValue,resolveInternalStartReferences,corrupted,unpack,jsonResult,errorResult} from '../src/service.mjs';
const structure={worksheetId:'ws',fields:[
  {id:'title',alias:'name',type:'Text',required:true},
  {id:'num',alias:'amount',type:'Number'},
  {id:'one',alias:'choice',type:'SingleSelect',options:[{key:'a'},{key:'b'}]},
  {id:'many',type:'MultipleSelect'}
]};
const response=data=>jsonResult({success:true,data});
function fake(handler) {
  const calls=[];
  return {calls, async callTool(req){calls.push(structuredClone(req));return handler(req);}};
}
test('invalid Number leaves upstream mutation untouched, including batch update',async()=>{
  for(const name of ['create_record','update_record','batch_update_records','batch_create_records']){
    const u=fake(()=>response(structure));const s=new NiioService(u);
    const fields=[{id:'title',value:'test'},{id:'num',value:'31abc'}];
    const args={appId:'app',worksheet_id:'ws',fields,rows:[{fields:[{id:'title',value:'ok'},{id:'num',value:30}]},{fields}]};
    await assert.rejects(()=>s.call(name,args),e=>e.code==='INVALID_NUMBER');
    assert.deepEqual(u.calls.map(c=>c.name),['get_worksheet_structure']);
  }
});
test('finite numbers, decimal strings and explicit optional clear preserve input',()=>{
  for(const value of [30,0,-1.5,'31.25','']){
    const fields=[{id:'num',value}];const before=structuredClone(fields);
    validateFields(fields,structure);assert.deepEqual(fields,before);
  }
  for(const value of [true,null,[],NaN,Infinity,'NOT_A_NUMBER','31abc',' ','9'.repeat(1000)])
    assert.throws(()=>validateFields([{id:'num',value}],structure));
});
test('required values, unknown, duplicate and read-only fields rejected',()=>{
  for(const fields of [[{id:'title',value:''}],[{id:'unknown',value:1}],[{id:'num',value:1},{id:'amount',value:2}]]){
    assert.throws(()=>validateFields(fields,structure));
  }
  assert.throws(()=>validateFields([{id:'num',value:1}],{fields:[{id:'num',type:'Number',isReadOnly:true}]}));
});
test('SingleSelect singleton normalizes while MultipleSelect stays an array',()=>{
  const one={kind:'literal',value:['b']},many={kind:'literal',value:['a','b']};
  normalizeSingleValue(one,structure.fields[2]);normalizeSingleValue(many,structure.fields[3]);
  assert.equal(one.value,'b');assert.deepEqual(many.value,['a','b']);
  for(const value of [[],['a','b'],['unknown']])
    assert.throws(()=>normalizeSingleValue({kind:'literal',value},structure.fields[2]));
});
test('list hydrates exact selected rows and retains original view/filter/pagination',async()=>{
  const args={appId:'app',worksheet_id:'ws',viewId:'restrictive',pageIndex:2,pageSize:1,
    fields:['num'],useFieldIdAsKey:true,filter:{type:'group',logic:'AND',children:[]},sorts:[{field:'title',isAsc:true}]};
  const u=fake(req=>{
    if(req.name==='get_worksheet_structure')return response(structure);
    if(req.name==='get_record_list'){assert.deepEqual(req.arguments,args);return response({rows:[{rowid:'allowed',num:''}],total:7});}
    assert.equal(req.arguments.row_id,'allowed');return response({rowId:'allowed',amount:'30.00',name:'private-unrequested'});
  });
  const result=await new NiioService(u).call('get_record_list',args);
  assert.deepEqual(unpack(result).data,{rows:[{rowid:'allowed',num:'30.00'}],total:7});
  assert.equal(result._meta.niioLocal.atomicSnapshot,false);
});
test('empty selected page does not request any details',async()=>{
  const u=fake(req=>response(req.name==='get_worksheet_structure'?structure:{rows:[],total:0}));
  await new NiioService(u).call('get_record_list',{appId:'app',worksheet_id:'ws',fields:['num']});
  assert.equal(u.calls.length,2);
});
test('denied detail never becomes blank success and never switches view',async()=>{
  const u=fake(req=>req.name==='get_worksheet_structure'?response(structure):
    req.name==='get_record_list'?response({rows:[{rowid:'r',num:''}]}):jsonResult({success:false,error_code:403}));
  await assert.rejects(()=>new NiioService(u).call('get_record_list',{appId:'app',worksheet_id:'ws',fields:['num'],viewId:'v'}),
    e=>e.code==='UPSTREAM_BUSINESS_ERROR');
  assert.equal(u.calls.filter(c=>c.name==='get_record_list').length,1);
});
test('missing field and wrong row are errors, not fabricated empty values',async()=>{
  for(const detail of [{rowId:'r'},{rowId:'other',amount:'30'}]){
    const u=fake(req=>response(req.name==='get_worksheet_structure'?structure:
      req.name==='get_record_list'?{rows:[{rowid:'r'}]}:detail));
    await assert.rejects(()=>new NiioService(u).call('get_record_list',{appId:'app',worksheet_id:'ws',fields:['num']}));
  }
});
test('batch node normalizes SingleSelect and leaves caller input immutable',async()=>{
  let stored;
  const u=fake(req=>{
    if(req.name==='get_worksheet_structure')return response(structure);
    if(req.name==='get_workflow_structure')return response({trigger:{nodeAlias:'start',config:{worksheetId:'ws'}},nodes:stored??[]});
    stored=req.arguments.nodes;return response({processId:'flow'});
  });
  const args={appId:'app',workflow_id:'flow',nodes:[{nodeType:'update_record',config:{target:{node:{nodeAlias:'start'}},
    fields:[{fieldId:'one',op:'set',value:{kind:'literal',value:['b']}},{fieldId:'many',op:'set',value:{kind:'literal',value:['a','b']}}]}}]};
  const before=structuredClone(args);
  await new NiioService(u).call('batch_create_process_nodes',args);
  assert.equal(stored[0].config.fields[0].value.value,'b');
  assert.deepEqual(stored[0].config.fields[1].value.value,['a','b']);
  assert.deepEqual(args,before);
});
test('SingleSelect eq trigger condition normalizes by the actual field type',async()=>{
  let sent;
  const u=fake(req=>{
    if(req.name==='get_worksheet_structure')return response(structure);
    if(req.name==='create_process'){sent=req.arguments;return response({processId:'flow'});}
    return response({trigger:sent.trigger,nodes:[]});
  });
  const args={appId:'app',trigger:{config:{worksheetId:'ws',filter:{items:[{op:'eq',left:{kind:'field',fieldId:'one'},
    right:{kind:'literal',value:['a']}}]}}}};
  await new NiioService(u).call('create_process',args);
  assert.equal(sent.trigger.config.filter.items[0].right.value,'a');
});
test('corrupt historical draft cannot validate or publish',async()=>{
  const poison=JSON.stringify({_children:[{_value:'b'}],_nodeFactory:{}});
  const u=fake(()=>response({nodes:[{value:poison}]}));const s=new NiioService(u);
  assert.equal(unpack(await s.call('validate_process',{appId:'a',workflow_id:'f'})).data.canPublish,false);
  await assert.rejects(()=>s.call('publish_process',{appId:'a',workflow_id:'f'}),e=>e.code==='CORRUPT_LITERAL');
  assert.ok(u.calls.every(c=>c.name==='get_workflow_structure'));
});
test('post-write corruption returns explicit uncertain mutation status',async()=>{
  let writes=0;
  const u=fake(req=>{
    if(req.name==='create_process'){writes++;return response({processId:'flow'});}
    return response({value:JSON.stringify({_children:[],_nodeFactory:{}})});
  });
  await assert.rejects(()=>new NiioService(u).call('create_process',{appId:'a',publish:false,trigger:{}}),
    e=>e.code==='WRITE_READBACK_FAILED'&&e.details.mutationMayHaveSucceeded);
  assert.equal(writes,1);
});
test('no auto publish and no error output of private payloads',async()=>{
  const u=fake(()=>{throw Error('secret-password')});
  await assert.rejects(()=>new NiioService(u).call('create_process',{publish:true}),e=>e.code==='SEPARATE_PUBLISH_REQUIRED');
  assert.equal(u.calls.length,0);
  assert.ok(!JSON.stringify(errorResult(Error('secret-password'))).includes('secret-password'));
  assert.equal(corrupted({value:['a','b']}),false);
});

test('internal start aliases resolve only to the current flow trigger and preserve literal data',()=>{
 for(const [type,alias]of [['approval','approval_start'],['sub_process','sub_trigger']]){
  const nodes=[{prevNode:{nodeAlias:alias},config:{target:{kind:'record',node:{nodeAlias:alias}},fields:[{value:{kind:'literal',value:{nodeAlias:alias}}}]}}];
  resolveInternalStartReferences(nodes,{trigger:{triggerType:type,nodeId:'real-start',nodeAlias:null},nodes:[]});
  assert.deepEqual(nodes[0].prevNode,{nodeId:'real-start'});
  assert.deepEqual(nodes[0].config.target.node,{nodeId:'real-start'});
  assert.deepEqual(nodes[0].config.fields[0].value.value,{nodeAlias:alias});
 }
 const nodes=[{prevNode:{nodeAlias:'approval_start'}}];
 resolveInternalStartReferences(nodes,{trigger:{triggerType:'worksheet_event',nodeId:'outer'},nodes:[]});
 assert.deepEqual(nodes[0].prevNode,{nodeAlias:'approval_start'});
});

test('upstream diagnostic retains actionable message and masks credential strings',()=>{
 let err;try{unpack(jsonResult({success:false,errorCode:430001,errorMsg:'invalid node pat_example_secret Bearer hidden_token'}));}catch(e){err=e;}
 assert.equal(err.details.upstreamCode,430001);
 assert.match(err.details.upstreamMessage,/invalid node/);
 assert.ok(!JSON.stringify(errorResult(err)).includes('example_secret'));
 assert.ok(!JSON.stringify(errorResult(err)).includes('hidden_token'));
});

test('gateway HTML is a tool failure and a mutation is never retried',async()=>{
 let writes=0;
 const upstream=fake(()=>{writes++;return {content:[{type:'text',text:'<html><head><title>502 Bad Gateway</title></head><body>nginx</body></html>'}],isError:false};});
 await assert.rejects(()=>new NiioService(upstream).call('create_app',{name:'synthetic'}),e=>e.code==='UPSTREAM_GATEWAY_UNAVAILABLE'&&e.details.upstreamStatus===502);
 assert.equal(writes,1);
});
