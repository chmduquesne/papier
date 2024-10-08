"""importing into papier"""

import os
import re
import argparse
from papier.cli.commands import command, add_argument
import papier
import papier.library
import papier.plugin.organize  # should we allow importing a plugin?
import confuse
from tempfile import NamedTemporaryFile as TempFile
import logging
from pypdf import PdfReader, PdfWriter
from argcomplete.completers import FilesCompleter
from typing import Generator, List, Any
import tqdm


# Logger for this plugin
log = logging.getLogger(__name__)


# Which files we process
PDF = re.compile(r'.*\.pdf', re.IGNORECASE)


def find_pdfs(path: str) -> Generator[str, str, str]:
    """returns all the pdfs under a given path"""
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path, p))


def get_conf() -> str:
    """returns the import config"""
    params = {
        'copy': bool,
        'delete': bool,
        'modify': bool,
        'ocr': str,
        'redo_ocr': bool,
        'autotag': bool,
        'set': dict
        }
    return papier.config['import'].get(params)


def process(path: str) -> None:
    log.info(f'processing {path}')
    doc = papier.Document.from_import(path)
    hide_progress = (not papier.config['progress'].get(bool))

    if papier.library.has(doc):
        log.info(f'skipping {path}')
        return

    tags, choices = dict(), dict()

    progressbar = tqdm.tqdm(papier.extractors, disable=hide_progress)
    for e in progressbar:
        progressbar.set_description(f'[{doc.path}] {e.plugin}')

        sure, unsure = e.extract(doc, tags)

        # Handle faulty plugins
        for tag in unsure:
            if tag in sure:
                log.warning(f'{e.plugin} is both sure and unsure about '
                            f'{tag}. Assuming unsure.')
                sure.pop(tag, None)

        # Override the config so that set_tags always wins
        if e.plugin == 'set_tags':
            for tag in sure:
                papier.config['autotag']['priority'][tag] = 'set_tags'

        # Handle conflicts between plugins, tag by tag
        for tag in sure | unsure:
            if tag in tags | choices:
                try:
                    prio = papier.config['autotag']['priority'][tag].get()
                    if e.plugin == prio:
                        tags.pop(tag, None)
                        choices.pop(tag, None)
                    else:
                        sure.pop(tag, None)
                        unsure.pop(tag, None)
                except confuse.ConfigError:
                    raise papier.ConfigError(
                            f'"{e.plugin}" is trying to overwrite "{tag}". '
                            f'Please specify config.autotag.priority.{tag}'
                            )

        # Merge the results
        tags |= sure
        choices |= unsure

    log.info(f'tags: {tags}')
    log.info(f'choices: {choices}')

    required = papier.config['import']['require'].get(list)

    # filter out non required tags
    unwanted = set(choices) - set(required)
    for k in unwanted:
        del choices[k]

    # TODO: add a procedure to choose when unsure
    if choices:
        log.info(f'Missing tags: {list(choices.keys())}')

    if all([tag in tags for tag in required]):
        log.info(f'All required tags are set for {doc}, adding to library')
        if not papier.config['dry_run'].get(bool):
            papier.library.add(doc, tags)
        desired_path = papier.plugin.organize.desired_path(doc, tags)
        log.info(f'desired_path: {desired_path}')


def tag(path: str,
        tags: dict[str, str] = {"/Author": "Christophe-Marie Duquesne"}
        ) -> str:
    with TempFile(dir='.', delete=False) as tmp:
        reader = PdfReader(path)

        writer = PdfWriter()
        writer.appendPagesFromReader(reader)
        writer.addMetadata(reader.getDocumentInfo())

        # Add the metadata
        writer.add_metadata(tags)
        writer.write(tmp)
        return tmp.name


def split_pair(tag_pair: str) -> tuple[str, ...]:
    """splits the input string at the first equals sign"""
    i = tag_pair.find('=')
    if i == -1:
        raise papier.CommandError(
                'Wrong argument for --set: expected <key>=<value>')
    return (tag_pair[:i], tag_pair[i+1:])


@command(
        add_argument('path', help='path to import',
                     completer=FilesCompleter(allowednames=('.pdf'))),
        add_argument('--copy', action=argparse.BooleanOptionalAction,
                     help='Copy files to the library directory after import',
                     default=argparse.SUPPRESS),
        add_argument('--delete', action=argparse.BooleanOptionalAction,
                     help='Delete files that were succesfully imported',
                     default=argparse.SUPPRESS),
        add_argument('--overwrite-text', action=argparse.BooleanOptionalAction,
                     help='Rewrite the files copied to the library',
                     default=argparse.SUPPRESS),
        add_argument('--overwrite-tags', action=argparse.BooleanOptionalAction,
                     help='Rewrite the files copied to the library',
                     default=argparse.SUPPRESS),
        add_argument('--ocr', action=argparse.BooleanOptionalAction,
                     help='Run OCR prior to import if no text is embedded',
                     choices=['always', 'never', 'empty'],
                     default=argparse.SUPPRESS),
        add_argument('--set', action='append',
                     help='Set the given tag to the given value',
                     default=argparse.SUPPRESS),
        add_argument('--autotag', action=argparse.BooleanOptionalAction,
                     help='Automatically tag the files',
                     default=argparse.SUPPRESS),
        command_name='import')
def run(args: List[Any]) -> None:
    if hasattr(args, 'set'):
        for tag_pair in args.set:
            tag_key, tag_value = split_pair(tag_pair)
            papier.config['import']['set'][tag_key].set(tag_value)
        del args.__dict__['set']

    papier.config['import'].set_args(args)
    for p in find_pdfs(args.path):
        process(p)
