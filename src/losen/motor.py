'''Motoren: Agent S3 bak grensesnittet kjernen forventer (reset, predict, meld).

S3Motor pakker inn AgentS3 uten å endre S3-filene. Beskjeder fra meld() legges foran neste
brukermelding til generatoren og refleksjonen, slik at agenten får vite at et steg ble avvist
eller feilet.
'''


class S3Motor:
    def __init__(self, agent):
        self.agent = agent
        self._beskjeder = []
        self._kobl_til()

    def reset(self):
        self._beskjeder = []
        self.agent.reset()
        self._kobl_til()

    def predict(self, oppgave, obs):
        return self.agent.predict(instruction=oppgave, observation=obs)

    def meld(self, tekst):
        self._beskjeder.append(tekst)

    def _ventende(self):
        return '\n'.join(self._beskjeder)

    def _kobl_til(self):
        worker = self.agent.executor
        # Refleksjonen kalles før generatoren i hvert steg. Den leser beskjeden,
        # generatoren leser den og tømmer køen.
        self._pakk_inn(worker.reflection_agent, tøm=False)
        self._pakk_inn(worker.generator_agent, tøm=True)

    def _pakk_inn(self, llm, tøm):
        original = llm.add_message

        def add_message(text_content, *args, role=None, **kwargs):
            if role == 'user' and self._beskjeder:
                text_content = self._ventende() + '\n\n' + (text_content or '')
                if tøm:
                    self._beskjeder = []
            return original(text_content, *args, role=role, **kwargs)

        llm.add_message = add_message


def bygg_s3_agent(args, skjerm_bredde, skjerm_høyde, plattform):
    '''Lag AgentS3 med samme oppsett som S3 sin kommandolinje (gui_agents.s3.cli_app).'''
    from gui_agents.s3.agents.agent_s import AgentS3
    from gui_agents.s3.agents.grounding import OSWorldACI

    engine_params = {
        'engine_type': args.provider,
        'model': args.model,
        'base_url': args.model_url,
        'api_key': '',
        'temperature': None,
    }
    grounding_params = {
        'engine_type': args.ground_provider,
        'model': args.ground_model,
        'base_url': args.ground_url,
        'api_key': '',
        'grounding_width': args.grounding_width,
        'grounding_height': args.grounding_height,
    }
    grounding_agent = OSWorldACI(
        env=None,
        platform=plattform,
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=grounding_params,
        width=skjerm_bredde,
        height=skjerm_høyde,
    )
    return AgentS3(
        engine_params,
        grounding_agent,
        platform=plattform,
        max_trajectory_length=args.max_trajectory_length,
        enable_reflection=True,
    )
