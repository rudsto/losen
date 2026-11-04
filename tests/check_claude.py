import sys

mode = sys.argv[1]
if mode in ('med', 'tenking'):
    from losen import s3_adapt
    s3_adapt.apply()

from gui_agents.s3.core.engine import LMMEngineAnthropic

e = LMMEngineAnthropic(model='claude-sonnet-5-5')
msgs = [
    {'role': 'system', 'content': [{'type': 'text', 'text': 'Svar med ett ord.'}]},
    {'role': 'user', 'content': [{'type': 'text', 'text': 'Si OK'}]},
]
extra = {}
if mode == 'tenking':
    extra = {'max_new_tokens': 2048, 'thinking': {'type': 'adaptive'}}
try:
    print(mode.upper(), '-> SVAR:', e.generate(msgs, **extra))
except Exception as err:
    print(mode.upper(), '->', type(err).__name__ + ':', str(err)[:200])
