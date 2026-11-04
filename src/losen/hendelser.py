'''Hendelser fra kjernen og loggen av dem.

Kjernen sender hver hendelse som en dict til alle lyttere. Grensesnittet (terminalen nå,
sluttbrukervinduet senere) er bare en lytter og vet ingenting om S3.

Hendelsestyper (se docs/konsept.md, Hendelsesflyt):
  økt_startet, vurderer, modellkall, forslag, venter_på_godkjenning,
  utført, avvist, venter, notat, feil, ferdig
'''
import datetime
import json
import os
import uuid


def nå():
    return datetime.datetime.now().astimezone().isoformat(timespec='milliseconds')


def ny_økt_id():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:6]


class Hendelseslogg:
    '''Skriver hver hendelse som én JSON-linje. Skjermbilder logges aldri.'''

    def __init__(self, sti):
        mappe = os.path.dirname(sti)
        if mappe:
            os.makedirs(mappe, exist_ok=True)
        self.sti = sti
        self._fil = open(sti, 'a', encoding='utf-8')

    def __call__(self, hendelse):
        self._fil.write(json.dumps(hendelse, ensure_ascii=False, default=str) + '\n')
        self._fil.flush()

    def lukk(self):
        self._fil.close()


def les_logg(sti):
    with open(sti, encoding='utf-8') as f:
        return [json.loads(linje) for linje in f if linje.strip()]
