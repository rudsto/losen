'''Losens tilpasninger av Agent S3 (gui-agents 0.3.2).

Kall apply() én gang ved oppstart, før agenten opprettes. S3-filene endres ikke;
funksjoner byttes ut i minnet. Har S3 endret prompten sin, stopper apply() med en tydelig feil.

Tilpasninger:
- Kodeagenten: fjernet fra prompten og låst.
- Regel 7 (OSWorld-passord og sudo): fjernet.
- Regel 6 (hurtigtaster): snudd til synlige klikk. Hurtigtaster er av og låst, med mindre allow_hotkeys=True.
- Anthropic-kall: temperature fjernes når SDK-en ikke tar imot den, og tekstblokker
  legges først i svaret (nye Claude-modeller kan starte med en tenkeblokk; S3 leser content[0].text).
'''
import functools
import inspect
import re

from anthropic.resources.messages import Messages
from gui_agents.s3.agents.grounding import OSWorldACI
from gui_agents.s3.memory.procedural_memory import PROCEDURAL_MEMORY

_original_build = PROCEDURAL_MEMORY.construct_simple_worker_procedural_memory

HOTKEY_ACTIONS = ['hotkey', 'hold_and_press']
_ORIGINAL_ACTIONS = {name: getattr(OSWorldACI, name) for name in HOTKEY_ACTIONS + ['call_code_agent']}
_settings = {'allow_hotkeys': False}

GUI_ONLY_GUIDELINES = '''## Agent Usage Guidelines
You only have access to GUI actions. Use them for every task: clicking, typing, navigation and application features. There is no code agent.

# General Task Guidelines
- If creating a new sheet with no name specified, use default sheet names (e.g., 'Sheet1', 'Sheet2', etc.).
- After opening or reopening applications, wait at least 3 seconds for full loading.

'''

VISIBLE_RULE_NO_HOTKEYS = '6. Use visible actions the user can follow: click buttons and menus. Keyboard shortcuts are not available.'
VISIBLE_RULE_WITH_HOTKEYS = '6. Prefer visible actions the user can follow: click buttons and menus. Only use agent.hotkey() when there is no visible alternative.'

_START = '## Agent Usage Guidelines'
_END = 'Never assume a task is done'
_PASSWORD_LINE = re.compile(r'^.*osworld-public-evaluation.*\n', re.MULTILINE)
_HOTKEY_RULE = re.compile(r'^([ \t]*)6\. Whenever possible, your grounded action should use hot-keys.*$', re.MULTILINE)


def _replace_once(pattern, repl, text, what):
    new, n = pattern.subn(repl, text)
    if n != 1:
        raise RuntimeError(f'S3-prompten har endret seg: forventet én forekomst av {what}, fant {n}. Sjekk s3_adapt.')
    return new


def _build_worker_prompt(agent_class, skipped_actions):
    skipped = list(skipped_actions) + ['call_code_agent']
    if not _settings['allow_hotkeys']:
        skipped += HOTKEY_ACTIONS
    prompt = _original_build(agent_class, skipped_actions=skipped)

    start, end = prompt.find(_START), prompt.find(_END)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError('S3-prompten har endret seg: fant ikke kodeagent-seksjonen. Sjekk s3_adapt.')
    prompt = prompt[:start] + GUI_ONLY_GUIDELINES + prompt[end:]

    prompt = _replace_once(_PASSWORD_LINE, '', prompt, 'passordlinjen (regel 7)')
    rule = VISIBLE_RULE_WITH_HOTKEYS if _settings['allow_hotkeys'] else VISIBLE_RULE_NO_HOTKEYS
    prompt = _replace_once(_HOTKEY_RULE, lambda m: m.group(1) + rule, prompt, 'hurtigtastregelen (regel 6)')
    return prompt


def _blocked(label):
    def blocked(self, *args, **kwargs):
        raise PermissionError(f'{label} er låst av i Losen.')
    return blocked


def text_blocks_first(content):
    '''Legg tekstblokker først og behold resten (f.eks. tenkeblokker) etter.'''
    texts = [b for b in content if getattr(b, 'type', None) == 'text']
    others = [b for b in content if getattr(b, 'type', None) != 'text']
    return texts + others


def _fix_anthropic_messages():
    if getattr(Messages.create, '_losen_patched', False):
        return
    original = Messages.create
    drop_temperature = 'temperature' not in inspect.signature(original).parameters

    @functools.wraps(original)
    def create(self, *args, **kwargs):
        if drop_temperature:
            kwargs.pop('temperature', None)
        response = original(self, *args, **kwargs)
        content = getattr(response, 'content', None)
        if content:
            response.content = text_blocks_first(content)
        return response

    create._losen_patched = True
    Messages.create = create


def apply(allow_hotkeys=False):
    _settings['allow_hotkeys'] = allow_hotkeys
    _fix_anthropic_messages()
    PROCEDURAL_MEMORY.construct_simple_worker_procedural_memory = staticmethod(_build_worker_prompt)
    OSWorldACI.call_code_agent = _blocked('Kodeagenten')
    for name in HOTKEY_ACTIONS:
        if allow_hotkeys:
            setattr(OSWorldACI, name, _ORIGINAL_ACTIONS[name])
        else:
            setattr(OSWorldACI, name, _blocked(f'Hurtigtasten ({name})'))
