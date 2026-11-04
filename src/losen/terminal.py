'''Terminalgrensesnittet i del 1: viser hendelsene og spør j/n/s før hver handling.

Grensesnittet kjenner bare hendelsene og forslagene fra kjernen, ikke S3.
'''

RESULTATER = {
    'løst': 'Agenten mener oppgaven er løst. Sjekk resultatet selv; agentens «ferdig» er ingen fasit.',
    'umulig': 'Agenten mener oppgaven ikke kan løses.',
    'stoppet': 'Stoppet. Ingen flere handlinger blir utført.',
    'maks_steg': 'Nådde maks antall steg uten å bli ferdig.',
    'feil': 'Stoppet på grunn av en feil. Se loggen.',
}


def vis(hendelse, skriv=print):
    '''Lytter: skriver de hendelsene utvikleren trenger å se.'''
    t, steg = hendelse['type'], hendelse.get('steg')
    if t == 'økt_startet':
        skriv(f'\nLosen: {hendelse["oppgave"]}')
        skriv(f'Maks {hendelse["maks_steg"]} steg. Stopp med s, Ctrl+C eller ved å dra musen til et hjørne.')
    elif t == 'vurderer':
        skriv(f'\n── Steg {steg} ── tar skjermbilde og spør modellen …')
    elif t == 'modellkall':
        skriv(f'   modellkall: {hendelse["modell"]}, {hendelse["tokens_inn"]} inn / '
              f'{hendelse["tokens_ut"]} ut, {hendelse["sekunder"]} s')
    elif t == 'forslag':
        if hendelse.get('refleksjon'):
            skriv(f'Refleksjon: {hendelse["refleksjon"]}')
        skriv(f'Plan:      {hendelse["neste"] or "(ingen Next Action)"}')
        skriv(f'Handling:  {hendelse["handling"]}')
        if hendelse['art'] == 'handling':
            skriv(f'Kode:      {hendelse["kode"]}')
    elif t == 'venter':
        skriv(f'Venter {hendelse["sekunder"]} s (ingen skjermhandling).')
    elif t == 'notat':
        skriv('Notat i agentens tekstbuffer (ingen skjermhandling).')
    elif t == 'utført':
        skriv('Utført.')
    elif t == 'avvist' and hendelse['valg'] == 'n':
        skriv('Ikke utført. Agenten får beskjed og prøver noe annet.')
    elif t == 'feil':
        skriv(f'FEIL ({hendelse["hvor"]}): {hendelse["feil"]}')
    elif t == 'ferdig':
        skriv('\n' + RESULTATER.get(hendelse['resultat'], hendelse['resultat']))


def spør(forslag, les=input, skriv=print):
    '''Spør om handlingen skal utføres. Returnerer (valg, kommentar).'''
    while True:
        try:
            svar = les('Utføre? [j]a / [n]ei / [s]topp: ').strip().lower()
        except EOFError:
            return 's', ''
        if svar in ('j', 'ja'):
            return 'j', ''
        if svar in ('s', 'stopp'):
            return 's', ''
        if svar in ('n', 'nei'):
            try:
                kommentar = les('Hvorfor? Agenten får vite det (valgfritt, Enter for å hoppe over): ').strip()
            except EOFError:
                kommentar = ''
            return 'n', kommentar
        skriv('Svar j, n eller s.')
