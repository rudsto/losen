'''Kjør S3 sin kommandolinje med Losens tilpasninger. Tar de samme flaggene som agent_s.

Installert som kommandoen losen-s3 (se pyproject.toml).
'''


def main():
    from losen import s3_adapt

    s3_adapt.apply()

    from gui_agents.s3.cli_app import main as s3_main

    s3_main()


if __name__ == '__main__':
    main()
