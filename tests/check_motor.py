'''Nivå 1: S3Motor mot ekte AgentS3-objekter, uten modellkall.

Sjekker at beskjeder fra meld() havner i neste brukermelding til generatoren og refleksjonen,
og at modellkall meldes til lytterne med tokens.
'''
import sys
from types import SimpleNamespace

from losen import s3_adapt

s3_adapt.apply()

from losen.cli import les_args  # noqa: E402
from losen.motor import S3Motor, bygg_s3_agent  # noqa: E402

results = []


def check(name, ok):
    print(('OK   ' if ok else 'FEIL ') + name)
    results.append(bool(ok))


def tekst(melding):
    return melding['content'][0]['text']


args = les_args(['x', '--grounding_width', '1470', '--grounding_height', '956'])
agent = bygg_s3_agent(args, 1920, 1080, 'darwin')
motor = S3Motor(agent)
worker = agent.executor
check('motoren bruker ekte AgentS3', type(agent).__name__ == 'AgentS3')
check('generator og refleksjon finnes', hasattr(worker, 'generator_agent') and hasattr(worker, 'reflection_agent'))

motor.meld('LOSEN: avvist')
worker.reflection_agent.add_message(text_content='forrige plan', role='user')
worker.generator_agent.add_message('neste steg', role='user')
check('refleksjonen får beskjeden', tekst(worker.reflection_agent.messages[-1]).startswith('LOSEN: avvist'))
check('generatoren får beskjeden', tekst(worker.generator_agent.messages[-1]).startswith('LOSEN: avvist'))
check('generatoren får fortsatt sin egen tekst', tekst(worker.generator_agent.messages[-1]).endswith('neste steg'))

worker.generator_agent.add_message('svar', role='assistant')
worker.generator_agent.add_message('steget etter', role='user')
check('assistentsvar endres ikke', tekst(worker.generator_agent.messages[-2]) == 'svar')
check('beskjeden kommer bare én gang', tekst(worker.generator_agent.messages[-1]) == 'steget etter')

motor.meld('LOSEN: før reset')
motor.reset()
check('reset lager ny worker', agent.executor is not worker)
agent.executor.generator_agent.add_message('første', role='user')
check('reset tømmer beskjedene', tekst(agent.executor.generator_agent.messages[-1]) == 'første')
motor.meld('LOSEN: etter reset')
agent.executor.generator_agent.add_message('andre', role='assistant')
agent.executor.generator_agent.add_message('tredje', role='user')
check('nye worker er koblet til', tekst(agent.executor.generator_agent.messages[-1]).startswith('LOSEN: etter reset'))

# Modellkall meldes med tokens (uten nettverk: kaller s3_adapt sin rapportering direkte)
kall = []
s3_adapt.add_model_call_listener(lambda *a: kall.append(a))
svar = SimpleNamespace(usage=SimpleNamespace(input_tokens=1200, output_tokens=80))
s3_adapt._report_model_call('claude-test', svar, 1.5)
check('modellkall meldes med tokens', kall == [('claude-test', 1200, 80, 1.5)])
s3_adapt._report_model_call('claude-test', SimpleNamespace(), 0.1)
check('svar uten usage gir None', kall[-1] == ('claude-test', None, None, 0.1))
check('create er fortsatt pakket inn', getattr(__import__('anthropic').resources.messages.Messages.create, '_losen_patched', False))

print('ALT OK' if all(results) else 'NOE FEILET')
sys.exit(0 if all(results) else 1)
