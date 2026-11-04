'''Kommandoen losen: én oppgave, godkjenning før hver handling, og hendelser i JSONL.

  losen "Åpne Kalkulator og regn ut 2+2" --grounding_width 1470 --grounding_height 956
  losen --falsk "Prøv sløyfen"      falsk S3: ingen modellkall, ingen skjermhandlinger

Modellvalgene er de samme som for losen-s3. Hvert flagg kan også settes som miljøvariabel,
for eksempel LOSEN_MODEL eller LOSEN_GROUNDING_WIDTH. Flagget vinner over miljøvariabelen.
Nøkkelen leses fra ANTHROPIC_API_KEY og kan ikke gis som flagg.
'''
import argparse
import datetime
import io
import os
import platform
import sys
import time

from losen import terminal
from losen.hendelser import Hendelseslogg
from losen.kjerne import MAKS_STEG, Kjerne

STANDARD_MODELL = 'claude-sonnet-5-5'


def _env(navn, standard=None, type=str):
    verdi = os.environ.get('LOSEN_' + navn.upper())
    if verdi in (None, ''):
        return standard
    return type(verdi)


def lag_parser():
    p = argparse.ArgumentParser(
        prog='losen',
        description='Losen: agenten foreslår, du godkjenner hvert steg (j/n/s).')
    p.add_argument('oppgave', nargs='?', help='Oppgaven. Spørres om hvis den mangler.')
    p.add_argument('--provider', default=_env('provider', 'anthropic'))
    p.add_argument('--model', default=_env('model', STANDARD_MODELL))
    p.add_argument('--model_url', default=_env('model_url', ''))
    p.add_argument('--ground_provider', default=_env('ground_provider', 'anthropic'))
    p.add_argument('--ground_url', default=_env('ground_url', 'https://api.anthropic.com'))
    p.add_argument('--ground_model', default=_env('ground_model'),
                   help='Standard: samme som --model.')
    p.add_argument('--grounding_width', type=int, default=_env('grounding_width', type=int))
    p.add_argument('--grounding_height', type=int, default=_env('grounding_height', type=int))
    p.add_argument('--max_trajectory_length', type=int, default=_env('max_trajectory_length', 8, int))
    p.add_argument('--maks_steg', type=int, default=_env('maks_steg', MAKS_STEG, int))
    p.add_argument('--logg', default=_env('logg', 'logs'), help='Mappe for hendelsesloggen.')
    p.add_argument('--hurtigtaster', action='store_true', default=bool(_env('hurtigtaster', '')),
                   help='Slå på hurtigtaster (av som standard).')
    p.add_argument('--falsk', action='store_true',
                   help='Bruk falsk S3: ingen modellkall og ingenting skjer på skjermen.')
    return p


def les_args(argv=None):
    p = lag_parser()
    args = p.parse_args(argv)
    if args.ground_model is None:
        args.ground_model = args.model
    if not args.falsk and (args.grounding_width is None or args.grounding_height is None):
        p.error('--grounding_width og --grounding_height må settes (eller LOSEN_GROUNDING_WIDTH/HEIGHT). '
                'Verdiene må kalibreres for skjermen din.')
    if args.maks_steg < 1:
        p.error('--maks_steg må være minst 1.')
    return args


def skaler(bredde, høyde, maks=2400):
    faktor = min(maks / bredde, maks / høyde, 1)
    return int(bredde * faktor), int(høyde * faktor)


def _ekte(args):
    '''Motor, observer og utfør for den ekte skjermen.'''
    import pyautogui
    from PIL import Image

    from losen import s3_adapt
    from losen.motor import S3Motor, bygg_s3_agent

    s3_adapt.apply(allow_hotkeys=args.hurtigtaster)
    bredde, høyde = pyautogui.size()
    skalert = skaler(bredde, høyde)
    agent = bygg_s3_agent(args, bredde, høyde, platform.system().lower())

    def observer():
        bilde = pyautogui.screenshot().resize(skalert, Image.LANCZOS)
        buf = io.BytesIO()
        bilde.save(buf, format='PNG')
        return {'screenshot': buf.getvalue()}

    def utfør(kode):
        exec(kode, {})

    return S3Motor(agent), observer, utfør, s3_adapt


def _falsk():
    from losen.falsk_s3 import FalskS3

    def utfør(kode):
        print(f'   (falsk) ville kjørt: {kode}')

    return FalskS3(), (lambda: {'screenshot': b''}), utfør, None


def main(argv=None):
    args = les_args(argv)
    oppgave = args.oppgave or input('Oppgave: ').strip()
    if not oppgave:
        print('Ingen oppgave.')
        return 2
    if not args.falsk and not os.environ.get('ANTHROPIC_API_KEY') and args.provider == 'anthropic':
        print('Mangler ANTHROPIC_API_KEY i miljøet.')
        return 2

    motor, observer, utfør, s3_adapt = _falsk() if args.falsk else _ekte(args)

    tidsstempel = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    logg = Hendelseslogg(os.path.join(args.logg, f'losen-{tidsstempel}.jsonl'))
    kjerne = Kjerne(motor, observer, utfør, terminal.spør, lyttere=[logg, terminal.vis],
                    maks_steg=args.maks_steg, vent=time.sleep, pause_etter=0.0 if args.falsk else 1.0)
    if s3_adapt:
        s3_adapt.add_model_call_listener(kjerne.modellkall)
    try:
        resultat = kjerne.kjør(oppgave)
    finally:
        if s3_adapt:
            s3_adapt.remove_model_call_listener(kjerne.modellkall)
        logg.lukk()
    print(f'Hendelseslogg: {logg.sti}')
    return 0 if resultat in ('løst', 'stoppet') else 1


if __name__ == '__main__':
    sys.exit(main())
