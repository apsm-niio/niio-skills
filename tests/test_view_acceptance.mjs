import test from 'node:test';
import assert from 'node:assert/strict';
import {readOne} from '../acceptance/view-readonly.mjs';
import {parseArray,parseNumber,parseOptions,isRelationCount} from '../skills/api/niio-view-plugin/scripts/field_values.mjs';
const ids={appId:'mock-app',worksheetId:'mock-sheet',viewId:'mock-view'};
test('mock SDK uses one bounded read; rejects target and response mismatch', async()=>{
  let calls=0;
  const api={async getFilterRows(args){calls++;assert.equal(args.pageSize,1);return {data:[{rowid:'mock'}]};}};
  assert.equal((await readOne(api,ids,ids)).rowCount,1);
  await assert.rejects(()=>readOne(api,{...ids,viewId:'wrong'},ids));
  assert.equal(calls,1);
  await assert.rejects(()=>readOne({getFilterRows:async()=>({data:'HTML'})},ids,ids));
});
test('field parsing distinguishes missing, zero, invalid and relation counts',()=>{
  assert.equal(parseNumber('0'),0);
  assert.equal(parseNumber('  '),null);
  for(const bad of ['12oops',true,[],{},Infinity]) assert.throws(()=>parseNumber(bad));
  assert.deepEqual(parseArray('[1]'),[1]);
  for(const bad of ['{}','oops',false]) assert.throws(()=>parseArray(bad));
  for(const bad of [null,false,[],{},'',-1,'-1','1.5',Infinity]) assert.equal(isRelationCount(bad),false);
  for(const good of [0,2,'2']) assert.equal(isRelationCount(good),true);
  assert.deepEqual(parseOptions('["unknown"]',{options:[]}),[{key:'unknown',text:'unknown',known:false}]);
});
