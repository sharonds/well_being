// Lightweight JSON Schema validator (subset): supports type, required, properties, enum, items, maxItems
// Returns { valid: boolean, errors: string[] }

function typeOf(val) {
  if (Array.isArray(val)) return 'array';
  return typeof val; // 'object', 'string', 'number', 'boolean', 'undefined'
}

function validateNode(data, schema, path, errors) {
  if (!schema || typeof schema !== 'object') return;

  // type check
  if (schema.type) {
    const t = schema.type;
    const actual = typeOf(data);
    const ok = Array.isArray(t) ? t.includes(actual) : actual === (t === 'integer' ? 'number' : t);
    if (!ok) {
      errors.push(`${path || 'value'}: expected type ${Array.isArray(t) ? t.join('|') : t}, got ${actual}`);
      return; // further checks depend on type
    }
  }

  // enum
  if (schema.enum) {
    const ok = schema.enum.some(v => v === data);
    if (!ok) errors.push(`${path || 'value'}: not in enum [${schema.enum.join(', ')}]`);
  }

  // object properties
  if (schema.type === 'object' && schema.properties) {
    const props = schema.properties || {};
    const req = schema.required || [];
    for (const k of req) {
      if (!(k in (data || {}))) errors.push(`${path || 'object'}: missing required property '${k}'`);
    }
    for (const [k, sub] of Object.entries(props)) {
      if (data && k in data) validateNode(data[k], sub, path ? `${path}.${k}` : k, errors);
    }
  }

  // array items
  if (schema.type === 'array') {
    if (!Array.isArray(data)) {
      errors.push(`${path || 'value'}: expected array`);
      return;
    }
    if (typeof schema.maxItems === 'number' && data.length > schema.maxItems) {
      errors.push(`${path || 'array'}: has ${data.length} items, exceeds maxItems ${schema.maxItems}`);
    }
    if (schema.items) {
      for (let i = 0; i < data.length; i++) {
        validateNode(data[i], schema.items, `${path || 'array'}[${i}]`, errors);
      }
    }
  }
}

export function validateJson(data, schema) {
  const errors = [];
  validateNode(data, schema, '', errors);
  return { valid: errors.length === 0, errors };
}
