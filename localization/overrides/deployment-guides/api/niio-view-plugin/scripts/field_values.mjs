// Parsing helpers only: no SDK, network, logging or mutation.
export function parseArray(value) {
  if (value == null || value === '') return [];
  const parsed = typeof value === 'string' ? JSON.parse(value) : value;
  if (!Array.isArray(parsed)) throw new TypeError('Expected array');
  return parsed;
}
export function parseNumber(value) {
  if (value == null || (typeof value === 'string' && value.trim() === '')) return null;
  if (!['number', 'string'].includes(typeof value)) throw new TypeError('Expected number');
  const number = Number(value);
  if (!Number.isFinite(number)) throw new TypeError('Invalid number');
  return number;
}
export function isRelationCount(value) {
  if (typeof value === 'string' && !/^\d+$/.test(value)) return false;
  if (!['number', 'string'].includes(typeof value)) return false;
  return Number.isSafeInteger(Number(value)) && Number(value) >= 0;
}
export function parseOptions(value, control) {
  const keys = parseArray(value);
  if (keys.some(key => typeof key !== 'string')) throw new TypeError('Expected option keys');
  if (!Array.isArray(control?.options)) throw new TypeError('Missing option metadata');
  return keys.map(key => {
    const option = control.options.find(o => o && o.key === key);
    return {key, text: option?.value ?? key, known: !!option};
  });
}
