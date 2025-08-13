export const InsightEnvelopeSchema = {
  type: 'object',
  required: ['version', 'type', 'payload', 'created_at'],
  properties: {
    version: { type: 'string', enum: ['v1'] },
    type: { type: 'string', enum: ['plan_daily', 'adherence_daily'] },
    device_id: { type: 'string' },
    created_at: { type: 'string' },
    payload: { type: 'object' }
  }
};

export const PlanDailySchema = {
  type: 'object',
  required: ['date', 'band', 'score', 'plan', 'schema_version'],
  properties: {
    date: { type: 'string' },
    band: { type: 'string', enum: ['Take it easy', 'Maintain', 'Go for it'] },
    score: { type: 'number' },
    delta: { type: 'number' },
    plan: {
      type: 'object',
      required: ['type', 'minutes_range', 'addons'],
      properties: {
        type: { type: 'string', enum: ['easy', 'maintain', 'hard'] },
        minutes_range: { type: 'string' },
        addons: { type: 'array', items: { type: 'string' } }
      }
    },
    why: { type: 'array', items: { type: 'string' }, maxItems: 2 },
    schema_version: { type: 'string' }
  }
};
