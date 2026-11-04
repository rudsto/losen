'''Losens sløyfe: predict, vurdering, godkjenning, utføring og hendelser.

Kjernen kjenner bare et motorgrensesnitt og noen funksjoner den får inn:

  motor.reset()                   start en ny oppgave
  motor.predict(oppgave, obs)     -> (info, [kode]) som AgentS3.predict
  motor.meld(tekst)               beskjed til agenten som kommer med i neste kall
  observer()                      -> {'screenshot': png-bytes}
  utfør(kode)                     kjører koden (exec), bare etter godkjenning
  spør(forslag)                   -> ('j' | 'n' | 's', kommentar)

Regelen kjernen håndhever: utfør() kalles aldri uten at spør() har svart 'j'.
Venting og notater til agentens tekstbuffer er ikke handlinger på skjermen. De kjøres
ikke gjennom utfør(), men vises og logges.
'''
import re
import time
from dataclasses import dataclass, field

from losen.hendelser import nå, ny_økt_id

MAKS_STEG = 15
MAKS_VENT = 10.0

AVVIST_BESKJED = (
    'LOSEN: The user rejected your previous proposed action, so it was NOT executed. '
    'Nothing changed on the screen because of it. Propose a different action.'
)
FEIL_BESKJED = 'LOSEN: Your previous action raised an error when it was executed and may not have taken effect: '

_VENT = re.compile(r'^\s*import time;\s*time\.sleep\(\s*([0-9.]+)\s*\)\s*;?\s*$')
_NESTE = re.compile(r'\(Next Action\)\s*(.*?)\s*(?:\(Grounded Action\)|```|$)', re.DOTALL)


@dataclass
class Forslag:
    steg: int
    art: str            # handling, vent, notat, løst, umulig
    neste: str          # S3 sin Next Action (engelsk)
    plan: str           # hele svaret fra generatoren
    handling: str       # agentens handling, f.eks. agent.click("…")
    kode: str           # koden som kjøres
    refleksjon: str = ''
    sekunder: float = 0.0
    tokens: dict = field(default_factory=lambda: {'inn': 0, 'ut': 0})


def klassifiser(kode):
    '''Hva slags steg er dette? Returnerer (art, sekunder).'''
    ren = (kode or '').strip()
    if ren == 'DONE':
        return 'løst', 0.0
    if ren == 'FAIL':
        return 'umulig', 0.0
    if ren == 'WAIT':   # save_to_knowledge: notat i agentens tekstbuffer
        return 'notat', 0.0
    m = _VENT.match(ren)
    if m:
        return 'vent', min(float(m.group(1)), MAKS_VENT)
    return 'handling', 0.0


def neste_handling(plan):
    '''Trekk ut avsnittet (Next Action) fra S3 sitt svar.'''
    m = _NESTE.search(plan or '')
    return m.group(1).strip() if m else ''


def _er_stopp(feil):
    # pyautogui.FailSafeException: musen dratt til et hjørne. Kjernen importerer ikke pyautogui.
    return isinstance(feil, KeyboardInterrupt) or type(feil).__name__ == 'FailSafeException'


class Kjerne:
    def __init__(self, motor, observer, utfør, spør, lyttere=(), maks_steg=MAKS_STEG,
                 vent=time.sleep, pause_etter=1.0):
        self.motor = motor
        self.observer = observer
        self.utfør = utfør
        self.spør = spør
        self.lyttere = list(lyttere)
        self.maks_steg = maks_steg
        self.vent = vent
        self.pause_etter = pause_etter
        self.økt = None
        self.steg = 0
        self._tokens = {'inn': 0, 'ut': 0}

    # Hendelser

    def send(self, type, **felt):
        hendelse = {'tid': nå(), 'økt': self.økt, 'steg': self.steg, 'type': type, **felt}
        for lytter in self.lyttere:
            lytter(hendelse)
        return hendelse

    def modellkall(self, modell, inn, ut, sekunder):
        '''Kalles for hvert modellkall (generator, refleksjon og grounding).'''
        self._tokens['inn'] += inn or 0
        self._tokens['ut'] += ut or 0
        self.send('modellkall', modell=modell, tokens_inn=inn, tokens_ut=ut,
                  sekunder=round(sekunder, 2))

    # Sløyfen

    def kjør(self, oppgave):
        '''Kjør én oppgave. Returnerer resultatet: løst, umulig, stoppet, maks_steg eller feil.'''
        self.økt = ny_økt_id()
        self.steg = 0
        self.send('økt_startet', oppgave=oppgave, maks_steg=self.maks_steg)
        try:
            self.motor.reset()
            resultat = self._sløyfe(oppgave)
        except BaseException as feil:
            if not _er_stopp(feil):
                self.send('feil', hvor='kjerne', feil=f'{type(feil).__name__}: {feil}')
                self.send('ferdig', resultat='feil')
                if isinstance(feil, Exception):
                    return 'feil'
                raise
            resultat = 'stoppet'
        self.send('ferdig', resultat=resultat)
        return resultat

    def _sløyfe(self, oppgave):
        for steg in range(1, self.maks_steg + 1):
            self.steg = steg
            forslag = self._vurder(oppgave)
            if forslag is None:
                return 'feil'
            if forslag.art in ('løst', 'umulig'):
                return forslag.art
            if forslag.art == 'notat':
                self.send('notat', handling=forslag.handling)
                continue
            if forslag.art == 'vent':
                self.send('venter', sekunder=forslag.sekunder)
                self.vent(forslag.sekunder)
                continue

            self.send('venter_på_godkjenning')
            valg, kommentar = self.spør(forslag)
            if valg == 's':
                self.send('avvist', valg='s', kommentar=kommentar)
                return 'stoppet'
            if valg != 'j':
                self.send('avvist', valg='n', kommentar=kommentar)
                beskjed = AVVIST_BESKJED + (f' User comment: {kommentar}' if kommentar else '')
                self.motor.meld(beskjed)
                continue

            try:
                self.utfør(forslag.kode)
            except BaseException as feil:
                if _er_stopp(feil):
                    raise
                tekst = f'{type(feil).__name__}: {feil}'
                self.send('feil', hvor='utføring', feil=tekst)
                self.motor.meld(FEIL_BESKJED + tekst)
                continue
            self.send('utført', valg='j', kode=forslag.kode)
            self.vent(self.pause_etter)
        return 'maks_steg'

    def _vurder(self, oppgave):
        self._tokens = {'inn': 0, 'ut': 0}
        self.send('vurderer')
        obs = self.observer()
        start = time.monotonic()
        try:
            info, koder = self.motor.predict(oppgave, obs)
        except Exception as feil:
            self.send('feil', hvor='modell', feil=f'{type(feil).__name__}: {feil}')
            return None
        kode = koder[0] if koder else ''
        art, sekunder = klassifiser(kode)
        plan = info.get('plan', '') or ''
        forslag = Forslag(
            steg=self.steg, art=art, neste=neste_handling(plan), plan=plan,
            handling=info.get('plan_code', '') or '', kode=kode,
            refleksjon=info.get('reflection') or '', sekunder=sekunder,
            tokens=dict(self._tokens),
        )
        self.send('forslag', art=art, neste=forslag.neste, handling=forslag.handling,
                  kode=kode, plan=plan, refleksjon=forslag.refleksjon,
                  tokens_inn=forslag.tokens['inn'], tokens_ut=forslag.tokens['ut'],
                  sekunder=round(time.monotonic() - start, 2))
        return forslag
