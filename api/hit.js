// Registra una visita o una partida, agrupadas por día y por fuente (?ref=tiktok, referrer, etc.)
const { pipeline } = require('./_redis');

const clean = (s, max) => String(s || '').toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, max);

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST' });
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  const ev = body && body.ev === 'play' ? 'plays' : 'visits';
  const src = clean(body && body.src, 30) || 'directo';
  const day = new Date().toISOString().slice(0, 10);
  try {
    await pipeline([
      ['HINCRBY', 'rz:' + ev + ':day', day, 1],
      ['HINCRBY', 'rz:' + ev + ':src', src, 1],
    ]);
    res.status(204).end();
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};
