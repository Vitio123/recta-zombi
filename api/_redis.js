// Cliente mínimo de Upstash Redis por REST (sin dependencias).
// Las variables las inyecta Vercel al conectar Upstash desde Storage / Marketplace.
const URL_ = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

async function pipeline(cmds) {
  if (!URL_ || !TOKEN) throw new Error('Falta conectar Upstash Redis en Vercel (KV_REST_API_URL / KV_REST_API_TOKEN)');
  const r = await fetch(URL_.replace(/\/$/, '') + '/pipeline', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds),
  });
  if (!r.ok) throw new Error('Upstash ' + r.status);
  return (await r.json()).map(x => x.result);
}

module.exports = { pipeline };
