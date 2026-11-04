'''Kjør Losens sjekker. Virker på macOS, Windows og Linux.

  python tests/run_checks.py         nivå 1: uten nøkkel og uten å styre skjermen
  python tests/run_checks.py --api   nivå 1 + 2: også små, ekte kall til Claude (krever ANTHROPIC_API_KEY, koster litt)

På Linux uten skjerm (sky, CI) trengs en virtuell skjerm, fordi S3 importerer pyautogui:
  xvfb-run python tests/run_checks.py
'''
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*args):
    print('$ python', ' '.join(args), flush=True)
    return subprocess.run([sys.executable, *args], cwd=ROOT).returncode


def main():
    codes = [run(os.path.join('tests', 'check_s3_adapt.py'))]
    if '--api' in sys.argv:
        if not os.environ.get('ANTHROPIC_API_KEY'):
            print('Mangler ANTHROPIC_API_KEY, hopper over nivå 2.')
            codes.append(1)
        else:
            for mode in ('uten', 'med', 'tenking'):
                codes.append(run(os.path.join('tests', 'check_claude.py'), mode))
    print('NIVÅ OK' if not any(codes) else 'NOE FEILET')
    sys.exit(1 if any(codes) else 0)


if __name__ == '__main__':
    main()
