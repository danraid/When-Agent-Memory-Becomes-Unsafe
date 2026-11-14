"""Evidence-limited article draft and journal package, never a submission action.

All numeric results come from verified run artifacts; all generated citations are
bound to Crossref identities plus separately recorded source-excerpt reviews.
"""
from __future__ import annotations
from pathlib import Path
import json
import re
from .bibliography import verify_claims, render_bibtex, CitationError
from .evidence import sha256, canonical, write_json
from .judge import summarize
from .report import create_manifest
from . import VERSION


class EditorialGateError(ValueError):
    pass


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _safe_title(value):
    return str(value or '').replace('\n',' ').replace('\r',' ').strip()


def _check_authored_text(content, valid_keys):
    if content.get('schema_version') != 1:
        raise EditorialGateError('INVALID_AUTHOR_CONTENT_SCHEMA')
    sections = content.get('sections')
    if not isinstance(sections, dict):
        raise EditorialGateError('INVALID_AUTHOR_CONTENT_SECTIONS')
    for name, value in sections.items():
        if name not in {'abstract','introduction','methods','discussion','limitations','conclusion'}:
            raise EditorialGateError('UNKNOWN_AUTHOR_SECTION')
        if not isinstance(value, str) or len(value)>50000:
            raise EditorialGateError('INVALID_AUTHOR_TEXT')
        citations=set(re.findall(r'\[@([a-zA-Z0-9_]+)\]',value))
        if citations - valid_keys:
            raise EditorialGateError('UNVERIFIED_AUTHOR_CITATION: '+','.join(sorted(citations-valid_keys)))
    return sections


def _verified_result_summary(directory):
    from scripts.hub import verify_manifest
    directory=Path(directory).resolve()
    verify_manifest(directory)
    summary=_load(directory/'summary.json')
    rows=_load(directory/'observations.json')
    if summary.get('classification') not in {'SYNTHETIC_TEST_FIXTURE_NOT_EMPIRICAL',
                                             'EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED'}:
        raise EditorialGateError('UNKNOWN_RESULT_CLASSIFICATION')
    if len(rows)!=summary.get('observations') or summary.get('summary') != summarize(rows):
        raise EditorialGateError('RESULT_SUMMARY_DOES_NOT_RECOMPUTE')
    if summary.get('research_approval') is not False or summary.get('publication_authorized') is not False:
        raise EditorialGateError('UNAUTHORISED_RESULT_PROMOTION')
    return summary


def _tex_escape(value):
    # Avoid LaTeX command injection in author-supplied strings.
    replace={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','&':r'\&','%':r'\%','#':r'\#',
             '$':r'\$','_':r'\_','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}
    return ''.join(replace.get(c,c) for c in str(value))


def _render_latex(*, title, authors, abstract, sections, citations):
    # This is a portable draft; individual journal classes must be applied by an author.
    lines=[r'\documentclass[11pt,a4paper]{article}',r'\usepackage[T1]{fontenc}',
           r'\usepackage[utf8]{inputenc}',r'\usepackage{hyperref}',
           r'\usepackage{natbib}',r'\title{'+_tex_escape(title)+'}',
           r'\author{'+_tex_escape(', '.join(authors) if authors else 'AUTHOR METADATA REQUIRED')+'}',
           r'\date{}',r'\begin{document}',r'\maketitle',r'\begin{abstract}',
           _tex_escape(abstract),r'\end{abstract}']
    for heading, lines_of_text in sections.items():
        lines.append(r'\section{'+_tex_escape(heading)+'}')
        for paragraph in lines_of_text:
            # Standard citation tags are the only LaTeX commands we generate.
            spans=re.split(r'(\[@[a-zA-Z0-9_]+\])',paragraph)
            chunks=[]
            for piece in spans:
                if re.fullmatch(r'\[@[a-zA-Z0-9_]+\]',piece):
                    key=piece[2:-1]
                    if key not in citations:
                        raise EditorialGateError('UNVERIFIED_LATEX_CITATION')
                    chunks.append(r'\citep{'+key+'}')
                else:
                    chunks.append(_tex_escape(piece))
            lines.append(''.join(chunks)+'\n')
    lines += [r'\bibliographystyle{plainnat}',r'\bibliography{references}',r'\end{document}']
    return '\n'.join(lines)+'\n'


def build_editorial(*, paper, author, content, catalogue, claims, source_root, output,
                    results_directory=None, profile=None, pdf=False):
    if paper.get('hub_schema_version')!=1:
        raise EditorialGateError('INVALID_PAPER_CONFIG')
    if not isinstance(author.get('authors'),list) or any(not isinstance(a,str) for a in author['authors']):
        raise EditorialGateError('INVALID_AUTHOR_METADATA')
    verified, records=verify_claims(catalogue,claims,source_root=source_root)
    keys={c['key'] for c in verified}
    authored=_check_authored_text(content,keys)
    profile=profile or {'target':'generic','current_instructions_verified':False}
    if profile.get('current_instructions_verified') is True:
        # The hub does not have an authoritative automatic journal compliance auditor.
        raise EditorialGateError('JOURNAL_INSTRUCTIONS_CANNOT_BE_AUTO_CERTIFIED')
    summary=_verified_result_summary(results_directory) if results_directory else None
    title=_safe_title(paper.get('title')) or 'UNCONFIGURED - NOT FOR PUBLICATION'
    authors=[a.strip() for a in author['authors'] if a.strip()]
    abstract=authored.get('abstract','').strip() or '[AUTHOR TO COMPLETE: evidence-bounded abstract]'
    sections={}
    sections['Introduction']=[authored.get('introduction','').strip() or '[AUTHOR TO COMPLETE: context, gap, novelty, hypothesis]']
    literature=[c['claim_text']+' [@'+c['key']+']' for c in verified]
    sections['Related work']=literature or ['[NO FULL-TEXT-VERIFIED CITATIONS IN DOSSIER]']
    sections['Methods']=[authored.get('methods','').strip() or '[AUTHOR TO COMPLETE: preregistered methods, baselines, seeds, controls]']
    if summary:
        info=(f"Result classification: {summary['classification']}. "
              f"Split: {summary['split']}. Episodes: {summary['episodes']}. "
              f"Calls/observations: {summary['observations']}. "
              f"Frozen protocol SHA256: {summary['protocol_sha256']}. "
              "The deterministic reference judge is not human peer review.")
        parts=[info]
        for condition, stats in sorted(summary['summary']['by_condition'].items()):
            parts.append(f"{condition}: n={stats['observations']}, raw accuracy={stats['raw_correct']:.4f}, "
                         f"system accuracy={stats['final_correct']:.4f}, "
                         f"unsafe final approval={stats['unsafe_final_approval']:.4f}, "
                         f"invalid JSON={stats['invalid_json']:.4f}.")
        if summary['classification']!='EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED':
            parts.insert(0,'[TECHNICAL MOCK RESULTS: NOT AN EMPIRICAL GPT STUDY]')
        sections['Results']=parts
    else:
        sections['Results']=['[NO VERIFIED EMPIRICAL RUN ATTACHED]']
    sections['Discussion']=[authored.get('discussion','').strip() or '[AUTHOR TO COMPLETE: interpretation, competing explanations]']
    sections['Limitations']=[authored.get('limitations','').strip() or '[AUTHOR TO COMPLETE: validity threats, domain limits]']
    sections['Conclusion']=[authored.get('conclusion','').strip() or '[AUTHOR TO COMPLETE: bounded conclusions]']
    md=['# '+title,'', '**DRAFT: SCIENTIFIC AND JOURNAL APPROVAL NOT GRANTED.**','',
        ('Authors: '+', '.join(authors)) if authors else 'Authors: [AUTHOR METADATA REQUIRED]','',
        '## Abstract','', abstract,'']
    for name, blocks in sections.items():
        md.extend(['## '+name,''])
        for block in blocks: md.extend([block,''])
    md.extend(['## References','', 'References are exported in `references.bib`. Every citation in this draft is mapped to a checked DOI identity and recorded full-text excerpt review; no independent authentication of reviewer identity is implied.',''])
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise EditorialGateError('EDITORIAL_OUTPUT_MUST_BE_NEW_OR_EMPTY')
    output.mkdir(parents=True,exist_ok=True)
    manuscript=output/'manuscript.md'
    manuscript.write_text('\n'.join(md),encoding='utf-8')
    (output/'manuscript.tex').write_text(_render_latex(title=title,authors=authors,abstract=abstract,
                               sections=sections,citations=keys),encoding='utf-8')
    (output/'references.bib').write_text(render_bibtex(records, verified),encoding='utf-8')
    write_json(output/'citation_provenance.json',{
        'classification':'CROSSREF_IDENTITY_AND_RECORDED_HUMAN_CLAIM_REVIEW',
        'human_identity_authentication':'NOT_PERFORMED', 'claims':verified,
        'catalogue_sha256':sha256(canonical(catalogue)),
        'dossier_sha256':sha256(canonical(claims))})
    ready_for_review=bool(authors and summary and summary['classification']=='EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED' and verified and all(authored.get(s,'').strip() for s in ('abstract','introduction','methods','discussion','limitations','conclusion')))
    checklist=[
        '# Journal submission preparation checklist', '',
        f"Target journal/profile: {profile.get('target','generic')} (CURRENT AUTHOR INSTRUCTIONS NOT VERIFIED)", '',
        f'- [{'x' if authors else ' '}] Author name(s) explicitly supplied',
        f'- [{'x' if verified else ' '}] At least one full-text-reviewed claim with verified Crossref identity',
        f"- [{'x' if summary and summary['classification']=='EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED' else ' '}] Empirical GPT run with verified evidence manifest",
        '- [ ] Full results and statistics reviewed by author and independent domain expert',
        '- [ ] Confirmatory preregistration, sample size, split isolation and deviations reviewed',
        '- [ ] Current journal instructions and article class checked at journal website',
        '- [ ] Copyright/licence, ethical approvals, conflicts of interest, funding and data statement reviewed',
        '- [ ] Author approves the exact final PDF, figures, references and claims',
        '- [ ] Explicit submission authorisation recorded externally', '',
        '**This software NEVER submits to a journal and NEVER marks a paper as scientifically approved.**',
    ]
    (output/'submission_checklist.md').write_text('\n'.join(checklist)+'\n',encoding='utf-8')
    summary_public={
        'classification':'EDITORIAL_DRAFT_NOT_SUBMISSION_READY',
        'hub_version':VERSION,'target_journal':profile.get('target','generic'),
        'journal_requirements_currently_verified':False,
        'recorded_fulltext_claims':len(verified),
        'source_doi_count':len({c['doi'] for c in verified}),
        'has_empirical_gpt_run':bool(summary and summary['classification']=='EMPIRICAL_GPT_OBSERVATIONS_UNREVIEWED'),
        'ready_for_author_review':ready_for_review,
        'scientific_approval':False,'submission_authorized':False,
        'limitations':'Author sections are NOT automatically fact-checked. Review signatures are recorded but not authenticated; current journal rules require direct verification.'}
    write_json(output/'editorial_status.json',summary_public)
    created=[manuscript,output/'manuscript.tex',output/'references.bib',
             output/'citation_provenance.json',output/'submission_checklist.md',output/'editorial_status.json']
    if pdf:
        from .pdf_export import render_draft_pdf
        render_draft_pdf(title, authors, abstract, sections, output/'manuscript.pdf')
        created.append(output/'manuscript.pdf')
    manifest=create_manifest(created,root=output,classification='EDITORIAL_DRAFT_NON_SUBMITTABLE')
    manifest['engine_sources']={
        'article_hub/'+name:sha256(Path(__file__).with_name(name).read_bytes())
        for name in ('bibliography.py','editorial.py','report.py')}
    if pdf:
        manifest['engine_sources']['article_hub/pdf_export.py']=sha256(Path(__file__).with_name('pdf_export.py').read_bytes())
    write_json(output/'manifest.json',manifest)
    return summary_public
