'''Nivå 1: sløyfen i kjernen med falsk S3. Ingen modellkall, ingen skjerm, ingen pyautogui.'''
import os
import sys
import tempfile

from losen import cli, terminal
from losen.falsk_s3 import EKSEMPEL, FalskS3
from losen.hendelser import Hendelseslogg, les_logg
from losen.kjerne import AVVIST_BESKJED, Kjerne, klassifiser, neste_handling

results = []


def check(name, ok):
    print(('OK   ' if ok else 'FEIL ') + name)
    results.append(bool(ok))


def kjør(svar, steg=None, utfør=None, maks_steg=15, feil_ved=None):
    '''Kjør en oppgave med faste svar. Returnerer (resultat, hendelser, utførte, motor, spurt).'''
    motor = FalskS3(steg, feil_ved=feil_ved)
    hendelser, utførte, spurt = [], [], []
    svar = list(svar)

    def spør(forslag):
        spurt.append(forslag)
        return svar.pop(0) if svar else ('s', '')

    k = Kjerne(motor, lambda: {'screenshot': b'png'}, utfør or utførte.append, spør,
               lyttere=[hendelser.append], maks_steg=maks_steg, vent=lambda s: None, pause_etter=0)
    return k.kjør('Regn ut 2+2'), hendelser, utførte, motor, spurt


def typer(hendelser):
    return [h['type'] for h in hendelser]


# Klassifisering og Next Action
check('DONE er løst', klassifiser('DONE') == ('løst', 0.0))
check('FAIL er umulig', klassifiser('FAIL') == ('umulig', 0.0))
check('WAIT er notat', klassifiser('WAIT')[0] == 'notat')
check('sleep er vent', klassifiser('import time; time.sleep(1.333)') == ('vent', 1.333))
check('lang vent kappes', klassifiser('import time; time.sleep(600)') == ('vent', 10.0))
check('klikk er handling', klassifiser('import pyautogui; pyautogui.click(1, 2)')[0] == 'handling')
check('sleep med mer kode er handling',
      klassifiser('import time; time.sleep(1); import pyautogui; pyautogui.click(1, 2)')[0] == 'handling')
check('tekst med «done» er handling', klassifiser("import pyautogui; pyautogui.write('done')")[0] == 'handling')
check('Next Action trekkes ut',
      neste_handling('(Next Action)\nKlikk på Fil.\n\n(Grounded Action)\n```python\nagent.click("Fil")\n```')
      == 'Klikk på Fil.')

# j på alt: eksempelet kjører til DONE
resultat, h, utført, motor, spurt = kjør([('j', ''), ('j', '')])
handlinger = [s for s in EKSEMPEL if klassifiser(s[1])[0] == 'handling']
check('j: oppgaven løses', resultat == 'løst')
check('j: begge handlingene er utført', utført == [s[1] for s in handlinger])
check('j: spurt én gang per handling', len(spurt) == len(handlinger))
check('j: vent spørres ikke om', all(f.art == 'handling' for f in spurt))
check('j: hendelsene starter og slutter riktig', typer(h)[0] == 'økt_startet' and h[-1]['type'] == 'ferdig' and h[-1]['resultat'] == 'løst')
check('j: alle hendelser har tid, økt og steg', all({'tid', 'økt', 'steg', 'type'} <= set(x) for x in h))
check('j: én økt-id', len({x['økt'] for x in h}) == 1)
check('j: forslag har plan, handling, kode og tokens',
      all({'plan', 'handling', 'kode', 'tokens_inn', 'tokens_ut'} <= set(x) for x in h if x['type'] == 'forslag'))
check('j: hver utført har en godkjenning foran seg',
      all(typer(h)[i - 1] == 'venter_på_godkjenning' for i, t in enumerate(typer(h)) if t == 'utført'))

# n: ikke utført, agenten får beskjed med kommentaren
resultat, h, utført, motor, spurt = kjør([('n', 'feil knapp'), ('j', ''), ('j', '')],
                                         steg=[EKSEMPEL[0], EKSEMPEL[0], EKSEMPEL[2], EKSEMPEL[3]])
check('n: avvist handling er ikke utført', len(utført) == 2)
check('n: agenten fikk beskjed', len(motor.meldinger) == 1 and motor.meldinger[0].startswith(AVVIST_BESKJED))
check('n: kommentaren er med', 'feil knapp' in motor.meldinger[0])
check('n: avvist er logget med kommentar',
      any(x['type'] == 'avvist' and x['valg'] == 'n' and x['kommentar'] == 'feil knapp' for x in h))

# s: stopp før noe skjer
resultat, h, utført, motor, spurt = kjør([('s', '')])
check('s: stoppet', resultat == 'stoppet')
check('s: ingenting utført', utført == [])
check('s: ingen nye kall etter stopp', motor.kall == 1)

# Ingen svar betyr stopp (EOF i terminalen)
check('EOF i terminalen betyr stopp', terminal.spør(None, les=lambda _: (_ for _ in ()).throw(EOFError())) == ('s', ''))
svar = iter(['x', 'n', ''])
check('ugyldig svar spørres om igjen', terminal.spør(None, les=lambda _: next(svar), skriv=lambda *_: None) == ('n', ''))

# Ctrl+C under godkjenning
def avbryt(forslag):
    raise KeyboardInterrupt


motor = FalskS3()
h, utført = [], []
k = Kjerne(motor, lambda: {}, utført.append, avbryt, lyttere=[h.append], vent=lambda s: None, pause_etter=0)
check('Ctrl+C: stoppet', k.kjør('x') == 'stoppet' and utført == [] and h[-1]['resultat'] == 'stoppet')


# Musen i hjørnet (pyautogui.FailSafeException) under utføring
class FailSafeException(Exception):
    pass


def hjørne(kode):
    raise FailSafeException('hjørne')


resultat, h, utført, motor, spurt = kjør([('j', '')], utfør=hjørne)
check('hjørnet: stoppet', resultat == 'stoppet')
check('hjørnet: ikke flere kall', motor.kall == 1)


# Feil under utføring: logges, agenten får beskjed, sløyfen fortsetter
def feiler_først(kode, teller=[0]):
    teller[0] += 1
    if teller[0] == 1:
        raise ValueError('ugyldig koordinat')


resultat, h, utført, motor, spurt = kjør([('j', ''), ('j', '')], utfør=feiler_først)
check('utføringsfeil: logget', any(x['type'] == 'feil' and x['hvor'] == 'utføring' for x in h))
check('utføringsfeil: agenten fikk beskjed', any('ugyldig koordinat' in m for m in motor.meldinger))
check('utføringsfeil: sløyfen fortsatte', resultat == 'løst')

# Modellfeil: stopper med feil
resultat, h, utført, motor, spurt = kjør([], feil_ved=1)
check('modellfeil: resultat feil', resultat == 'feil' and h[-1]['resultat'] == 'feil')

# Maks steg
resultat, h, utført, motor, spurt = kjør([('j', '')] * 5, steg=[EKSEMPEL[0]] * 5, maks_steg=3)
check('maks steg: stopper', resultat == 'maks_steg' and len(utført) == 3)

# FAIL fra agenten
resultat, h, utført, motor, spurt = kjør([], steg=[('agent.fail()', 'FAIL', 'Umulig.')])
check('FAIL: umulig', resultat == 'umulig')

# Modellkall gir tokens i hendelsene
motor = FalskS3()
h = []


def spør_med_kall(forslag):
    return 'j', ''


k = Kjerne(motor, lambda: {}, lambda kode: None, spør_med_kall, lyttere=[h.append], vent=lambda s: None, pause_etter=0)
original = motor.predict


def predict_med_kall(oppgave, obs):
    k.modellkall('claude-test', 100, 20, 0.5)
    return original(oppgave, obs)


motor.predict = predict_med_kall
k.kjør('x')
forslag = [x for x in h if x['type'] == 'forslag']
check('modellkall logges', any(x['type'] == 'modellkall' and x['tokens_inn'] == 100 for x in h))
check('tokens summeres per steg', forslag[0]['tokens_inn'] == 100 and forslag[0]['tokens_ut'] == 20)

# Hendelsesloggen i JSONL
with tempfile.TemporaryDirectory() as mappe:
    sti = os.path.join(mappe, 'logs', 'test.jsonl')
    logg = Hendelseslogg(sti)
    resultat, h, utført, motor, spurt = kjør([('j', ''), ('j', '')])
    for x in h:
        logg(x)
    logg.lukk()
    lest = les_logg(sti)
check('loggen har alle hendelsene', lest == h)
check('loggen har æøå i klartekst', any(x['type'] == 'økt_startet' for x in lest))
check('loggen har ingen skjermbilder', not any('screenshot' in str(x) for x in lest))

# Kommandolinjen
args = cli.les_args(['oppgave', '--grounding_width', '1470', '--grounding_height', '956'])
check('cli: standardmodell', args.model == cli.STANDARD_MODELL and args.ground_model == args.model)
check('cli: hurtigtaster er av', args.hurtigtaster is False)
os.environ['LOSEN_GROUNDING_WIDTH'], os.environ['LOSEN_GROUNDING_HEIGHT'] = '1000', '600'
os.environ['LOSEN_MODEL'] = 'claude-env'
args = cli.les_args(['oppgave'])
check('cli: miljøvariabler brukes', args.grounding_width == 1000 and args.model == 'claude-env')
args = cli.les_args(['oppgave', '--model', 'claude-flagg'])
check('cli: flagg vinner over miljøvariabel', args.model == 'claude-flagg')
for navn in ('LOSEN_GROUNDING_WIDTH', 'LOSEN_GROUNDING_HEIGHT', 'LOSEN_MODEL'):
    del os.environ[navn]
check('cli: ingen pyautogui ved import', 'pyautogui' not in sys.modules)

print('ALT OK' if all(results) else 'NOE FEILET')
sys.exit(0 if all(results) else 1)
