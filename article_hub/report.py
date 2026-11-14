"""Evidence-bound, non-submittable methods report. Never invent outcomes or citations."""
from __future__ import annotations
from pathlib import Path
from .evidence import sha256, write_json
from . import VERSION


def create_manifest(files, *, root, classification='PIPELINE_TECHNICAL_EVIDENCE'):
    root = Path(root).resolve()
    entries = []
    for path in sorted(set(map(Path, files))):
        absolute = path.resolve()
        if not absolute.is_file() or not absolute.is_relative_to(root):
            raise ValueError('Evidence file not beneath designated root')
        entries.append({'path': str(absolute.relative_to(root)), 'bytes': absolute.stat().st_size, 'sha256': sha256(absolute.read_bytes())})
    return {
        'classification': classification,
        'scientifically_approved': False,
        'hub_version': VERSION,
        'submission_authorized': False,
        'files': entries,
    }


def render_technical_report(paper, results, manifest):
    if results.get('classification') != 'SYNTHETIC_METHODS_DEMONSTRATION':
        raise ValueError('Only synthetic demonstration reports supported by generic hub')
    if not results.get('claim_about_real_agents') is False:
        raise ValueError('Unsafe result classification')
    analysis = results['analysis']
    title = paper.get('title', 'Unconfigured research study').replace('\n', ' ')
    return (f'# {title}\n\n'
            '**TECHNICAL PIPELINE REPORT. NOT A SCIENTIFIC ARTICLE OR SUBMISSION.**\n\n'
            '## Demonstration methods\n\n'
            f"A reproducible fictional Bernoulli paired experiment used seed `{results['seed']}` "
            f"and `{results['n']}` artificial paired observations. "
            'The parameters were chosen for software testing, not inferred from agent behaviour.\n\n'
            '## Observed synthetic output\n\n'
            f"- Artificial control event rate: {analysis['risk_control']:.4f}\n"
            f"- Artificial intervention event rate: {analysis['risk_treatment']:.4f}\n"
            f"- Paired risk difference: {analysis['risk_difference']:.4f}\n"
            f"- Illustrative normal-approximation 95% interval: "
            f"[{analysis['ci_95_normal_approx'][0]:.4f}, {analysis['ci_95_normal_approx'][1]:.4f}]\n\n"
            '## Explicit limitations\n\n'
            f"{results['limitations']}\n\n"
            '## Provenance and publication lock\n\n'
            f"- Evidence files: {len(manifest['files'])}\n"
            '- Scientific validation: NOT PERFORMED\n'
            '- Bibliographic full-text review: NOT PERFORMED\n'
            '- Confirmatory or holdout data: NOT ACCESSED\n'
            '- Publication/submission: NOT AUTHORIZED\n')


def run_demo(*, paper, output, seed=2026, n=400):
    from .experiment import synthetic_paired_demo
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = synthetic_paired_demo(seed=seed, n=n)
    result_file = output/'synthetic_experiment.json'
    write_json(result_file, result)
    report_file = output/'technical_report.md'
    preliminary = create_manifest([result_file], root=output)
    report_file.write_text(render_technical_report(paper, result, preliminary), encoding='utf-8')
    manifest = create_manifest([result_file, report_file], root=output)
    source_root = Path(__file__).resolve().parents[1]
    manifest['engine_sources'] = {
        f'article_hub/{name}': sha256((source_root/'article_hub'/name).read_bytes())
        for name in ('evidence.py', 'experiment.py', 'statistics.py', 'report.py')
    }
    manifest_file = output/'manifest.json'
    write_json(manifest_file, manifest)
    return {'result': str(result_file), 'manifest': str(manifest_file), 'report': str(report_file), 'classification': result['classification'], 'scientific_approval': False}
