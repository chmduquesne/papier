import papier
# from papier.cli.commands import command, add_argument
import jinja2


def desired_path(document: papier.Document, tags: dict[str, str]) -> str:
    env = jinja2.Environment()

    rules = papier.config['organize'].get(list)
    for rule in rules:
        # If there is no 'when' statement, we assume a pass
        conditions = [True]
        if 'when' in rules:
            when = rule['when']
            for statement in when:
                # every statement should render as 'True'
                rendered = (env
                            .from_string('{{ ' + statement + '}}')
                            .render(**tags))
                conditions.append(rendered == 'True')
        if all(conditions):
            path = rule['path']
            return env.from_string(path).render(**tags)
    raise Exception('could not match the document with a rule')


def organize(document: papier.Document, tags: dict[str, str]) -> None:
    pass
