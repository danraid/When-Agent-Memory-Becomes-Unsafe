"""Version-pinned standalone paper generator, no remote or network side effects."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from . import VERSION
from .evidence import sha256, write_json

SLUG = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
PAPER_TESTS = ('test_contract.py', 'test_discovery.py', 'test_experiment.py', 'test_llm.py', 'test_empirical.py', 'test_editorial.py', 'test_homologation.py')


def source_digest(root):
    folders = ('article_hub', 'templates/article', 'scripts', 'tests', 'docs')
    files = [p for folder in folders for p in (root/folder).rglob('*')
             if p.is_file() and p.suffix != '.pyc' and '__pycache__' not in p.parts]
    files += [root/'AGENTS.md', root/'README.md']
    entries = '\n'.join(f'{p.relative_to(root)}:{sha256(p.read_bytes())}' for p in sorted(files))
    return sha256(entries.encode('utf-8'))


def init_paper(root: Path, output: Path, slug: str, title: str):
    if not SLUG.fullmatch(slug):
        raise ValueError('Slug must be lowercase letters, digits and hyphens')
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Title must not be empty')
    if output.exists():
        raise FileExistsError('Destination exists; refusing to overwrite')
    source = root/'templates/article'
    if not (source/'paper.json').is_file():
        raise FileNotFoundError('Missing paper template')
    shutil.copytree(source, output)
    shutil.copytree(root/'article_hub', output/'article_hub', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (output/'scripts').mkdir()
    shutil.copy2(root/'scripts/hub.py', output/'scripts/hub.py')
    shutil.copy2(root/'scripts/homologate.py', output/'scripts/homologate.py')
    (output/'tests').mkdir()
    for name in PAPER_TESTS:
        shutil.copy2(root/'tests'/name, output/'tests'/name)
    shutil.copytree(root/'tests/fixtures', output/'tests/fixtures')
    shutil.copy2(root/'AGENTS.md', output/'AGENTS.md')
    (output/'docs').mkdir()
    for name in ('SCIENTIFIC_CONTRACT.md','OPERATOR_GUIDE.md','EMPIRICAL_ENGINE.md','EDITORIAL_ENGINE.md','HOMOLOGATION.md'):
        shutil.copy2(root/'docs'/name, output/'docs'/name)
    shutil.copy2(root/'.gitignore', output/'.gitignore')
    paper = json.loads((output/'paper.json').read_text(encoding='utf-8'))
    paper['slug'], paper['title'] = slug, title.strip()
    write_json(output/'paper.json', paper)
    write_json(output/'GENERATED_FROM_HUB.json', {
        'hub_version': VERSION, 'hub_source_sha256': source_digest(root),
        'created_utc': datetime.now(timezone.utc).isoformat(), 'kind': 'version_pinned_template_copy'})
    return output
