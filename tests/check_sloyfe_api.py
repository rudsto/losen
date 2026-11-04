'''Nivå 2: sløyfen med ekte AgentS3 og Claude, men uten å røre skjermen.

Observasjonen er et kunstig skjermbilde. Første forslag avvises (n), andre stoppes (s), så
utfør() skal aldri kalles. Sjekker at avvisningen kommer frem til modellen og at API-et godtar
meldingene. Koster noen få kall med bilde.
'''
import io
import os
import sys

from PIL import Image, ImageDraw

from losen import s3_adapt

s3_adapt.apply()

from losen.cli import les_args  # noqa: E402
from losen.kjerne import AVVIST_BESKJED, Kjerne  # noqa: E402
from losen.motor import S3Motor, bygg_s3_agent  # noqa: E402

BREDDE, HØYDE = 1470, 956
results = []


def check(name, ok):
    print(('OK   ' if ok else 'FEIL ') + name)
    results.append(bool(ok))


def skjermbilde():
    bilde = Image.new('RGB', (BREDDE, HØYDE), 'white')
    tegn = ImageDraw.Draw(bilde)
    tegn.rectangle([600, 420, 870, 520], outline='black', width=4, fill='#dde')
    tegn.text((705, 460), 'OK', fill='black')
    buf = io.BytesIO()
    bilde.save(buf, format='PNG')
    return {'screenshot': buf.getvalue()}


model = os.environ.get('LOSEN_MODEL', 'claude-sonnet-5-5')
args = les_args(['x', '--model', model, '--grounding_width', str(BREDDE), '--grounding_height', str(HØYDE)])
agent = bygg_s3_agent(args, BREDDE, HØYDE, 'darwin')
motor = S3Motor(agent)
hendelser, utført = [], []
svar = [('n', 'Try a different approach.'), ('s', '')]

k = Kjerne(motor, skjermbilde, utført.append, lambda f: svar.pop(0), lyttere=[hendelser.append],
           maks_steg=4, vent=lambda s: None, pause_etter=0)
s3_adapt.add_model_call_listener(k.modellkall)
resultat = k.kjør('Click the OK button in the middle of the screen.')
s3_adapt.remove_model_call_listener(k.modellkall)

typer = [h['type'] for h in hendelser]
feil = [h for h in hendelser if h['type'] == 'feil']
for h in feil:
    print('     ', h['hvor'], h['feil'][:300])
forslag = [h for h in hendelser if h['type'] == 'forslag']
kall = [h for h in hendelser if h['type'] == 'modellkall']
brukermeldinger = [m for m in agent.executor.generator_agent.messages if m['role'] == 'user']

check('ingen feil', not feil)
check('ingenting er utført', utført == [])
check('stoppet etter n og s', resultat == 'stoppet' and typer.count('avvist') == 2)
check('forslagene har plan og handling', len(forslag) >= 2 and all(f['plan'] and f['handling'] for f in forslag))
check('modellkall er logget med tokens', kall and all((h['tokens_inn'] or 0) > 0 for h in kall))
check('avvisningen kom frem til generatoren',
      any(AVVIST_BESKJED in m['content'][0]['text'] for m in brukermeldinger))
for f in forslag:
    print(f'      steg {f["steg"]}: {f["handling"][:100]}')

print('ALT OK' if all(results) else 'NOE FEILET')
sys.exit(0 if all(results) else 1)
