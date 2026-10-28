export class ServiceError extends Error {
  constructor(code, message, details = {}) { super(message); this.code = code; this.details = details; }
}
export function unpack(result) {
  if (result?.isError) throw new ServiceError('UPSTREAM_TOOL_ERROR', '上游工具回報失敗。');
  let tree;
  try { tree = JSON.parse(result.content.find(x => x.type === 'text').text); }
  catch { throw new ServiceError('UPSTREAM_FORMAT', '上游沒有傳回可核對的 JSON。'); }
  let data = tree;
  while (data && typeof data === 'object' && !Array.isArray(data)) {
    if (data.success === false) {
      const message=data.error?.message??data.errorMsg??data.message;
      const upstreamMessage=typeof message==='string'?message.replace(/pat_[A-Za-z0-9_-]+/g,'[redacted]').replace(/Bearer\s+[A-Za-z0-9._~-]+/gi,'Bearer [redacted]').slice(0,1200):undefined;
      throw new ServiceError('UPSTREAM_BUSINESS_ERROR', '上游業務操作失敗。', { upstreamCode: data.error_code ?? data.errorCode ?? data.error?.code, ...(upstreamMessage?{upstreamMessage}:{}) });
    }
    if ('data' in data && ('success' in data || Object.keys(data).length === 1)) data = data.data;
    else break;
  }
  return { tree, data };
}
export function jsonResult(value) { return { content: [{ type: 'text', text: JSON.stringify(value) }] }; }
export function errorResult(error) {
  const known = error instanceof ServiceError;
  return { ...jsonResult({ success: false, error: { code: known ? error.code : 'SERVICE_FAILURE',
    message: known ? error.message : '服務未完成；若為寫入，請先讀回核對，不要直接重送。',
    ...(known ? error.details : {}) } }), isError: true };
}
export function corrupted(value) {
  if (typeof value === 'string' && /^[\[{]/.test(value.trim())) {
    try { return corrupted(JSON.parse(value)); } catch { return false; }
  }
  if (!value || typeof value !== 'object') return false;
  if ('_nodeFactory' in value && ('_children' in value || '_value' in value)) return true;
  return Object.values(value).some(corrupted);
}
const NUMERIC = new Set(['Number', 'Currency']);
export function validateFields(fields, structure, mode = 'update') {
  if (!Array.isArray(fields) || !fields.length) throw new ServiceError('INVALID_FIELDS', '至少提供一個欄位。');
  const seen = new Set();
  for (const patch of fields) {
    const field = structure.fields.find(f => f.id === patch.id || f.alias === patch.id);
    if (!field) throw new ServiceError('UNKNOWN_FIELD', '找不到指定欄位。');
    if (seen.has(field.id)) throw new ServiceError('DUPLICATE_FIELD', '同一欄位不可重複指定。', { fieldId: field.id });
    seen.add(field.id);
    if (field.isReadOnly) throw new ServiceError('READ_ONLY_FIELD', '不可寫入唯讀欄位。', { fieldId: field.id });
    const v = patch.value;
    if (field.required && (v === '' || v === null || v === undefined || (typeof v === 'string' && !v.trim()) || (Array.isArray(v) && !v.length)))
      throw new ServiceError('REQUIRED_FIELD', '必填欄位不可為空。', { fieldId: field.id });
    if (NUMERIC.has(field.type)) {
      const valid = typeof v === 'number' ? Number.isFinite(v) :
        typeof v === 'string' && (v === '' || (/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/.test(v) && Number.isFinite(Number(v))));
      if (!valid) throw new ServiceError('INVALID_NUMBER', '數字欄位須為有限數字或一般十進位字串；原值未寫入。', { fieldId: field.id });
    }
  }
  if (mode === 'create') for (const field of structure.fields) {
    if (field.required && !field.isReadOnly && !seen.has(field.id) && !field.defaultValue?.length)
      throw new ServiceError('REQUIRED_FIELD', '缺少必填欄位。', { fieldId: field.id });
  }
}
export function normalizeSingleValue(valueRef, field, op = 'set') {
  if (field?.type !== 'SingleSelect' || valueRef?.kind !== 'literal' || !['set', 'eq', 'ne'].includes(op)) return;
  if (Array.isArray(valueRef.value)) {
    if (valueRef.value.length !== 1 || typeof valueRef.value[0] !== 'string')
      throw new ServiceError('INVALID_SINGLE_SELECT', '單選常數只允許一個選項 key。', { fieldId: field.id });
    const key = valueRef.value[0];
    if (!(field.options ?? []).some(o => o.key === key && !o.isDelete))
      throw new ServiceError('INVALID_OPTION', '單選常數不屬於目前欄位。', { fieldId: field.id });
    valueRef.value = key;
  }
}
export function resolveInternalStartReferences(nodes,flow) {
  const alias=flow.trigger?.triggerType==='approval'?'approval_start':flow.trigger?.triggerType==='sub_process'?'sub_trigger':null;
  if(!alias||!flow.trigger?.nodeId||flow.trigger.nodeAlias===alias||(flow.nodes??[]).some(n=>n.nodeAlias===alias))return;
  const visit=value=>{
    if(!value||typeof value!=='object'||value.kind==='literal')return;
    if(!Array.isArray(value)&&value.nodeAlias===alias&&!value.nodeId&&Object.keys(value).every(k=>k==='nodeAlias')){
      delete value.nodeAlias;value.nodeId=flow.trigger.nodeId;return;
    }
    for(const [key,child]of Object.entries(value))if(!['value','samplePayload','code','content','body'].includes(key)||child?.kind)visit(child);
  };
  visit(nodes);
}
export class NiioService {
  constructor(upstream) { this.upstream = upstream; }
  async raw(name, args, signal) {
    const result=await this.upstream.callTool({ name, arguments: args }, undefined, { timeout: 60000, signal });
    for(const item of result.content??[])if(item.type==='text'){
      const gateway=item.text.match(/^\s*<html[^>]*>[\s\S]*?<title>\s*(502|503|504)\b/i);
      if(gateway)throw new ServiceError('UPSTREAM_GATEWAY_UNAVAILABLE','上游服務目前無法處理此工具；需要修復遠端服務，未自動重送。',{upstreamStatus:Number(gateway[1]),tool:name});
    }
    return result;
  }
  async data(name, args, signal) { return unpack(await this.raw(name, args, signal)).data; }
  async structure(appId, worksheet_id, signal) {
    const s = await this.data('get_worksheet_structure', { appId, worksheet_id, responseFormat: 'dsl' }, signal);
    if (!s?.worksheetId || !Array.isArray(s.fields)) throw new ServiceError('STRUCTURE_MISMATCH', '無法確認工作表欄位結構。');
    return s;
  }
  async normalizeConditions(filter, appId, defaultWs, resolveNode, signal) {
    if (!filter || typeof filter !== 'object') return;
    if (filter.left?.kind === 'field' && filter.right?.kind === 'literal') {
      const ws = resolveNode(filter.left.node) ?? defaultWs;
      if (ws) {
        const s = await this.structure(appId, ws, signal);
        normalizeSingleValue(filter.right, s.fields.find(f => f.id === filter.left.fieldId), filter.op);
      }
    }
    for (const child of filter.items ?? []) await this.normalizeConditions(child, appId, defaultWs, resolveNode, signal);
  }
  async normalizeWorkflow(name, args, signal) {
    if (name === 'create_process') {
      const ws = args.trigger?.config?.worksheetId;
      await this.normalizeConditions(args.trigger?.config?.filter, args.appId, ws, () => ws, signal);
      return;
    }
    const flow = await this.data('get_workflow_structure', { appId: args.appId, workflow_id: args.workflow_id, version: 'draft' }, signal);
    resolveInternalStartReferences(args.nodes??[],flow);
    const all = [flow.trigger, ...(flow.nodes ?? []), ...(args.nodes ?? [])].filter(Boolean);
    const resolve = (ref, seen = new Set()) => {
      const node = all.find(n => (ref?.nodeId && n.nodeId === ref.nodeId) || (ref?.nodeAlias && n.nodeAlias === ref.nodeAlias));
      if (!node || seen.has(node)) return;
      seen.add(node);
      return node.config?.worksheetId ?? resolve(node.config?.target?.node, seen);
    };
    for (const node of args.nodes ?? []) {
      const ws = node.config?.worksheetId ?? resolve(node.config?.target?.node);
      if (node.nodeType === 'update_record' || node.nodeType === 'create_record') {
        if (!ws && node.config?.fields?.some(f => f.value?.kind === 'literal' && Array.isArray(f.value.value)))
          throw new ServiceError('UNRESOLVED_TARGET', '陣列賦值需先確認目標工作表，請在節點 config 指定 worksheetId。');
        if (ws) {
          const s = await this.structure(args.appId, ws, signal);
          for (const write of node.config?.fields ?? []) {
            const f = s.fields.find(f => f.id === write.fieldId);
            if (!f) throw new ServiceError('UNKNOWN_FIELD', '工作流欄位不屬於目標表。');
            normalizeSingleValue(write.value, f, write.op ?? 'set');
            if (NUMERIC.has(f.type) && write.value?.kind === 'literal') validateFields([{ id: f.id, value: write.value.value }], s);
          }
        }
      }
      await this.normalizeConditions(node.config?.filter, args.appId, ws, resolve, signal);
    }
  }
  async completeList(args, signal) {
    if (args.responseFormat === 'md' || !args.fields?.length) return this.raw('get_record_list', args, signal);
    const s = await this.structure(args.appId, args.worksheet_id, signal);
    const fields = args.fields.map(id => s.fields.find(f => f.id === id));
    if (fields.some(f => !f)) throw new ServiceError('UNKNOWN_FIELD', '完整欄位讀取必須使用目前工作表的實體欄位 ID。');
    // Retain the exact original row selection, view, filter, search, sort, pagination.
    const result = await this.raw('get_record_list', args, signal);
    const { tree, data } = unpack(result);
    if (!Array.isArray(data?.rows)) throw new ServiceError('UPSTREAM_FORMAT', '清單回應缺少 rows。');
    // Bound fan-out. No retries or broader view/row selection.
    for (let start = 0; start < data.rows.length; start += 4) {
      await Promise.all(data.rows.slice(start, start + 4).map(async row => {
        const id = row.rowid ?? row.rowId;
        if (!id) throw new ServiceError('MISSING_ROW_ID', '無法核對清單記錄 ID。');
        const detail = await this.data('get_record_details', { appId: args.appId, worksheet_id: args.worksheet_id, row_id: id, includeSystemFields: false }, signal);
        if (detail.rowId !== id && detail.rowid !== id) throw new ServiceError('ROW_ID_MISMATCH', '清單與詳情記錄不一致。');
        for (const field of fields) {
          const keys = [field.alias, field.id].filter(Boolean);
          const key = keys.find(k => Object.hasOwn(detail, k));
          if (key === undefined) throw new ServiceError('FIELD_UNAVAILABLE', '目前身分無法讀回要求的欄位；不把缺值當成空值。', { fieldId: field.id });
          row[args.useFieldIdAsKey ? field.id : (field.alias || field.id)] = detail[key];
        }
      }));
    }
    return { content: [{ type: 'text', text: JSON.stringify(tree) }], _meta: { niioLocal: { fieldValuesSource: 'authorized_record_details', rowSelectionSource: 'original_list', atomicSnapshot: false } } };
  }
  async call(name, input, signal) {
    const args = structuredClone(input);
    if (name === 'create_process' && args.publish === true)
      throw new ServiceError('SEPARATE_PUBLISH_REQUIRED', '請先建立草稿，再用 publish_process 發布，以核對實際儲存內容。');
    if (['create_record', 'update_record', 'batch_create_records', 'batch_update_records'].includes(name)) {
      const s = await this.structure(args.appId, args.worksheet_id, signal);
      if (name === 'batch_create_records') {
        for (const row of args.rows) validateFields(row.fields, s, 'create');
      } else validateFields(args.fields, s, name === 'create_record' ? 'create' : 'update');
    }
    if (name === 'get_record_list') return this.completeList(args, signal);
    if (['create_process', 'batch_create_process_nodes'].includes(name)) await this.normalizeWorkflow(name, args, signal);
    if (['validate_process', 'publish_process'].includes(name)) {
      const draft = await this.data('get_workflow_structure', { appId: args.appId, workflow_id: args.workflow_id, version: 'draft' }, signal);
      if (corrupted(draft)) {
        if (name === 'validate_process') return jsonResult({ success: true, data: { valid: false, canPublish: false, issueCount: 1,
          issues: [{ code: 'CORRUPT_LITERAL', message: '草稿含內部 JSON 樹污染，必須修正後發布。' }] } });
        throw new ServiceError('CORRUPT_LITERAL', '草稿含內部 JSON 樹污染，未送出發布。');
      }
    }
    const result = await this.raw(name, args, signal);
    if (['create_process', 'batch_create_process_nodes'].includes(name)) {
      const created = unpack(result).data;
      const flowId = created?.processId ?? args.workflow_id;
      if (flowId) {
        const draft = await this.data('get_workflow_structure', { appId: args.appId, workflow_id: flowId, version: 'draft' }, signal);
        if (corrupted(draft)) throw new ServiceError('WRITE_READBACK_FAILED', '節點已送出但讀回仍有污染；請依流程 ID 核對，勿直接重送。', { workflowId: flowId, mutationMayHaveSucceeded: true });
      }
    }
    return result;
  }
}
