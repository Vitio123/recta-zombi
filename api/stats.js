// Devuelve los contadores para la página /stats
const { pipeline } = require('./_redis');

const toObj = a => { const o = {}; for (let i = 0; a && i < a.length; i += 2) o[a[i]] = +a[i + 1]; return o; };

module.exports = async (req, res) => {
  try {
    const [vd, vs, pd, ps] = await pipeline([
      ['HGETALL', 'rz:visits:day'], ['HGETALL', 'rz:visits:src'],
      ['HGETALL', 'rz:plays:day'], ['HGETALL', 'rz:plays:src'],
    ]);
    res.setHeader('Cache-Control', 'no-store');
    res.status(200).json({
      visits: { day: toObj(vd), src: toObj(vs) },
      plays: { day: toObj(pd), src: toObj(ps) },
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};
