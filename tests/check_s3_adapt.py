import inspect

from gui_agents.s3.agents.grounding import OSWorldACI
from gui_agents.s3.memory.procedural_memory import PROCEDURAL_MEMORY
from losen import s3_adapt

before = PROCEDURAL_MEMORY.construct_simple_worker_procedural_memory(OSWorldACI, skipped_actions=[])
s3_adapt.apply()
after = PROCEDURAL_MEMORY.construct_simple_worker_procedural_memory(OSWorldACI, skipped_actions=[])


def check(name, ok):
    print(('OK   ' if ok else 'FEIL ') + name)
    return ok


def raises_permission(fn):
    try:
        fn(None)
    except PermissionError:
        return True
    return False


rest = after.lower().replace('there is no code agent', '')
results = [
    check('regel 7 fantes før', 'osworld-public-evaluation' in before),
    check('passordet er borte', 'osworld-public-evaluation' not in after),
    check('sudo er borte', 'sudo' not in after.lower()),
    check('kodeagent-seksjonen fantes før', '### Code Agent' in before),
    check('ingen omtale av kodeagent igjen', 'code agent' not in rest and 'code_agent' not in rest),
    check('call_code_agent er ikke i handlingslisten', 'def call_code_agent' not in after),
    check('call_code_agent er låst', raises_permission(OSWorldACI.call_code_agent)),
    check('regel 6 (hurtigtaster) fantes før', 'use hot-keys' in before),
    check('regel 6 er snudd', 'use hot-keys' not in after and s3_adapt.VISIBLE_RULE_NO_HOTKEYS in after),
    check('hotkey og hold_and_press er ikke i handlingslisten', 'def hotkey' not in after and 'def hold_and_press' not in after),
    check('ingen agent.hotkey( igjen i prompten', 'agent.hotkey(' not in after),
    check('hotkey er låst', raises_permission(OSWorldACI.hotkey)),
    check('click og type er med', 'def click' in after and 'def type' in after),
    check('type kan trykke Enter selv', 'enter' in str(inspect.signature(OSWorldACI.type))),
]

s3_adapt.apply(allow_hotkeys=True)
opt_in = PROCEDURAL_MEMORY.construct_simple_worker_procedural_memory(OSWorldACI, skipped_actions=[])
results += [
    check('opt-in: hotkey er tilgjengelig', 'def hotkey' in opt_in),
    check('opt-in: synlige klikk foretrekkes fortsatt', s3_adapt.VISIBLE_RULE_WITH_HOTKEYS in opt_in),
]
s3_adapt.apply()


from types import SimpleNamespace as B
order = s3_adapt.text_blocks_first([B(type='thinking'), B(type='text', text='x')])
results.append(check('tekstblokk legges først', order[0].type == 'text' and order[1].type == 'thinking'))
print('LENGDE', len(before), '->', len(after))
print('ALT OK' if all(results) else 'NOE FEILET')
