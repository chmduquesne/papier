import papier
# from papier.cli.commands import command, add_argument
import jinja2
import os.path
import logging
import shutil

# Logger for this plugin
log = logging.getLogger(__name__)


def desired_path(document: papier.Document, tags: dict[str, str]) -> str:
    env = jinja2.Environment()

    rules = papier.config['organize'].get(list)
    for rule in rules:
        # proceed by default (no 'when' statement)
        proceed = True

        # process the conditions
        if 'when' in rules:
            when = rule['when']
            conditions = []
            for statement in when:
                # every statement should render as 'True'
                rendered = (env
                            .from_string('{{ ' + statement + '}}')
                            .render(**tags))
                conditions.append(rendered == 'True')
            proceed = all(conditions)

        # Render the desired path
        if proceed:
            path = rule['path']
            return env.from_string(path).render(**tags)

    # If no rule was matched, return the existing path
    return document.path


def organize(document: papier.Document, tags: dict[str, str]) -> None:
    libdir = papier.config['directory'].as_path()
    desired = desired_path(document, tags)
    desired = os.path.join(libdir, desired)
    dest = desired

    # Find non taken path
    i = 1
    name, ext = os.path.splitext(desired)
    while os.path.exists(dest):
        dest = f'{name}-{i}' + ext
        i += 1

    log.info(f'Organizing {document} in {dest}')

    # Copy the file
    shutil.copy(document.tmpfile, dest)

    # Update the path of the document in the library
    document.path = os.path.join(libdir, dest)
    papier.library.update(document)
