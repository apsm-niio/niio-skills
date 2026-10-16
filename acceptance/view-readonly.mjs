// Inject the actual platform SDK only after target IDs and read access are confirmed.
// This module neither imports a remote SDK nor logs data/credentials.
export async function readOne(api, config, expected) {
  if (!api || typeof api.getFilterRows !== 'function') throw new Error('Missing SDK');
  for (const key of ['appId', 'worksheetId', 'viewId']) {
    if (!expected[key] || config[key] !== expected[key]) throw new Error('Target mismatch');
  }
  const result = await api.getFilterRows({worksheetId: config.worksheetId, viewId: config.viewId,
    pageIndex: 1, pageSize: 1});
  if (!result || !Array.isArray(result.data) || result.data.length > 1) throw new Error('SDK response contract mismatch');
  return {rowCount: result.data.length, operation: 'getFilterRows', writes: 0};
}
