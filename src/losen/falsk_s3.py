'''Falsk S3: en motor som returnerer forhåndsbestemte steg. Brukes i tester og i `losen --falsk`.

Ingen modellkall, ingen skjerm. Hvert steg er en tuple (handling, kode, neste):
  handling  agentens handling slik S3 skriver den, f.eks. agent.click("Fil-menyen")
  kode      koden S3 ville kjørt (pyautogui-kode, DONE, FAIL, WAIT eller time.sleep)
  neste     teksten i (Next Action)
'''

EKSEMPEL = [
    ('agent.click("The Calculator app icon in the dock")',
     'import pyautogui; pyautogui.click(100, 200)',
     'Open the Calculator app by clicking its icon in the dock.'),
    ('agent.wait(1.0)', 'import time; time.sleep(1.0)', 'Wait for Calculator to open.'),
    ('agent.type(text="2+2", enter=True)',
     "import pyautogui; pyautogui.write('2+2'); pyautogui.press('enter'); ",
     'Type 2+2 and press Enter to calculate the result.'),
    ('agent.done()', 'DONE', 'The result 4 is shown. The task is complete.'),
]


def lag_plan(neste, handling):
    return (
        '(Previous action verification)\nFalsk S3.\n\n'
        '(Screenshot Analysis)\nFalsk S3 ser ikke på skjermen.\n\n'
        f'(Next Action)\n{neste}\n\n'
        f'(Grounded Action)\n```python\n{handling}\n```'
    )


class FalskS3:
    def __init__(self, steg=None, feil_ved=None):
        self.steg = list(EKSEMPEL if steg is None else steg)
        self.feil_ved = feil_ved      # kast en feil i predict ved dette kallet (1-basert)
        self.meldinger = []           # alt agenten har fått via meld()
        self.kall = 0
        self.observasjoner = []

    def reset(self):
        self.kall = 0
        self.meldinger = []
        self.observasjoner = []

    def predict(self, oppgave, obs):
        self.kall += 1
        self.observasjoner.append(obs)
        if self.feil_ved == self.kall:
            raise RuntimeError('falsk modellfeil')
        if self.kall > len(self.steg):
            handling, kode, neste = 'agent.fail()', 'FAIL', 'No more scripted steps.'
        else:
            handling, kode, neste = self.steg[self.kall - 1]
        info = {'plan': lag_plan(neste, handling), 'plan_code': handling, 'exec_code': kode,
                'reflection': None}
        return info, [kode]

    def meld(self, tekst):
        self.meldinger.append(tekst)
