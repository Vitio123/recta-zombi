# Math Sucks

Juego de matemáticas en la recta numérica: dibujas el resultado y la manzana salta a ese número.

## Sonido

Toda la música usa instrumentos reales muestreados (`snd/*.json`, mp3 mono en base64, se cargan por partes según lo que suene). Se regeneran con `python tools/buildsnd.py` (requiere ffmpeg).

- **FluidR3 GM** (Frank Wen), vía [gleitz/midi-js-soundfonts](https://github.com/gleitz/midi-js-soundfonts) — [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/): piano, piano eléctrico, sintetizador, cuerdas, violín, chelo, contrabajo, timbales, guitarras, bajos, glockenspiel, xilófono, marimba, acordeón y metales.
- **VCSL — Versilian Community Sample Library** (Sam Gossner), vía [danigb/samples](https://github.com/danigb/samples) — [CC0](https://creativecommons.org/publicdomain/zero/1.0/): batería acústica, bongós, congas, claves, cencerro, güiro, shaker, pandereta, cabasa, triángulo, gong, matraca y cajón.
- **Roland TR-808 Sample Set** (Michael Fischer, 1994) — distribución gratuita: caja de ritmos.

En el menú y contra los jefes suena música clásica con arreglos cinematográficos (percusión épica, «braaams», ostinatos de cuerda, bajo sintético y guitarras) que suman capas en cada vuelta y pasan a la siguiente obra en vez de repetirse: Mozart (Sinfonía n.º 40, Rondo alla turca, Pequeña serenata nocturna), Beethoven (Sinfonía n.º 5, «Claro de luna», Para Elisa, Himno de la alegría), Pachelbel (Canon en re), Grieg (En la gruta del rey de la montaña) y Bach (Tocata y fuga en re menor). Todas las obras son de dominio público; los arreglos son propios.

Durante los niveles normales suena un género distinto cada vez, sin repetir hasta pasar por todos: pop, rock, rock and roll, jazz, blues, hip hop / rap, reguetón, salsa, cumbia, country, R&B, soul, funk, disco, house, techno, reggae y ska. El instrumento solista y las capas de percusión van rotando, y cada 32 compases entra otro género.
