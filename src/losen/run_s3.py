'''Kjør S3 sin kommandolinje med Losens tilpasninger. Tar de samme flaggene som agent_s.'''
from losen import s3_adapt

s3_adapt.apply()

from gui_agents.s3.cli_app import main  # noqa: E402

if __name__ == '__main__':
    main()
