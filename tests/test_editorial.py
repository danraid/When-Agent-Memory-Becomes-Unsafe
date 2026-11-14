import copy
import json
from pathlib import Path
import tempfile
import unittest

from article_hub.bibliography import CitationError, validate_catalogue, verify_claims
from article_hub.editorial import EditorialGateError, build_editorial
from article_hub.evidence import sha256, canonical
from article_hub.empirical import run_benchmark
from scripts.hub import verify_manifest

ROOT=Path(__file__).resolve().parents[1]


def template(path):
    p=ROOT/path
    if not p.exists(): p=ROOT/'templates/article'/path
    return json.loads(p.read_text(encoding='utf-8'))


def sample():
    snapshot={'DOI':'10.1234/journal.2025.7','title':['Verified Sample Paper'],
              'author':[{'family':'Smith','given':'Alex'}]}
    record={'doi':'10.1234/journal.2025.7','title':'Verified Sample Paper','authors':['Alex Smith'],
        'publication_year':2025,'venue':'Journal of Tests','status':'METADATA_VERIFIED',
        'metadata_check':'CROSSREF_IDENTITY_MATCH','crossref_source_sha256':sha256(canonical(snapshot)),
        'is_retracted_flag':False,'source':{'provider':'OpenAlex','url':'https://openalex.org/W1'}}
    catalogue={'classification':'BIBLIOGRAPHIC_METADATA_ONLY','records':[record],
               'crossref_snapshots':{'10.1234/journal.2025.7':snapshot}}
    return catalogue


class EditorialTests(unittest.TestCase):
    def test_default_scaffold_has_no_fake_references(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'editorial'
            report=build_editorial(paper=template('paper.json'),author=template('editorial/author.json'),
                content=template('editorial/content.json'),catalogue=template('editorial/catalogue.json'),
                claims=template('editorial/claims.json'),source_root=ROOT,output=dest,
                profile=template('editorial/journal_profile.json'))
            self.assertFalse(report['ready_for_author_review'])
            self.assertFalse(report['scientific_approval'])
            self.assertEqual(report['recorded_fulltext_claims'],0)
            self.assertEqual((dest/'references.bib').read_text(),'')
            self.assertIn('NO FULL-TEXT-VERIFIED CITATIONS',(dest/'manuscript.md').read_text())
            self.assertEqual(verify_manifest(dest)['verified_files'],6)

    def test_real_citation_path_requires_audit_and_source_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            excerpt=root/'evidence/excerpts/source-1.txt'
            excerpt.parent.mkdir(parents=True)
            excerpt.write_text('A short, manually checked excerpt from the source paper.\n')
            claim={'id':'source1','doi':'10.1234/journal.2025.7',
                'claim_text':'The authors investigated a small benchmark design.',
                'excerpt_path':'evidence/excerpts/source-1.txt',
                'excerpt_sha256':sha256(excerpt.read_bytes()),'locator':{'section':'2.1'},
                'human_review':{'decision':'VERIFIED','method':'MANUAL_FULLTEXT_REVIEW',
                                'reviewer':'Test Human Reviewer','reviewed_at_utc':'2026-11-14T00:00:00Z'}}
            dossier={'schema_version':1,'claims':[claim]}
            catalog=sample()
            valid, records=verify_claims(catalog,dossier,source_root=root)
            self.assertEqual(len(valid),1)
            self.assertEqual(valid[0]['key'],'doi_10_1234_journal_2025_7')
            content=template('editorial/content.json')
            content['sections']['introduction']='The study has limited evidence. [@doi_10_1234_journal_2025_7]'
            author={'authors':['Researcher X']}
            output=root/'draft'
            summary=build_editorial(paper=template('paper.json'),author=author,content=content,
                catalogue=catalog,claims=dossier,source_root=root,output=output,
                profile=template('editorial/journal_profile.json'))
            self.assertEqual(summary['recorded_fulltext_claims'],1)
            self.assertFalse(summary['submission_authorized'])
            self.assertIn('\\citep{doi_10_1234_journal_2025_7}',(output/'manuscript.tex').read_text())
            self.assertIn('10.1234/journal.2025.7',(output/'references.bib').read_text())
            self.assertEqual(verify_manifest(output)['verified_files'],6)
            excerpt.write_text('tampered')
            with self.assertRaisesRegex(CitationError,'hash mismatch'):
                verify_claims(catalog,dossier,source_root=root)

    def test_fake_and_mismatched_crossref_metadata_rejected(self):
        fixture=sample()
        fixture['classification']='SYNTHETIC_BIBLIOGRAPHIC_FIXTURE'
        with self.assertRaisesRegex(CitationError,'SYNTHETIC'):
            validate_catalogue(fixture)
        fixture=sample()
        fixture['crossref_snapshots']['10.1234/journal.2025.7']['title']=['Other title entirely']
        self.assertEqual(validate_catalogue(fixture),{})

    def test_unverified_author_citation_rejected(self):
        content=template('editorial/content.json')
        content['sections']['introduction']='Unsupported reference [@doi_10_0000_fake]'
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(EditorialGateError,'UNVERIFIED_AUTHOR_CITATION'):
                build_editorial(paper=template('paper.json'),author=template('editorial/author.json'),
                    content=content,catalogue=template('editorial/catalogue.json'),
                    claims=template('editorial/claims.json'),source_root=ROOT,output=Path(d)/'draft')

    def test_empirical_mock_result_is_preserved_as_mock_not_science(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            run_benchmark(paper=template('paper.json'),protocol=template('experiment_protocol.json'),
                output=root/'run',episodes=2,steps=7)
            report=build_editorial(paper=template('paper.json'),author=template('editorial/author.json'),
                content=template('editorial/content.json'),catalogue=template('editorial/catalogue.json'),
                claims=template('editorial/claims.json'),source_root=ROOT,output=root/'draft',
                results_directory=root/'run')
            self.assertFalse(report['has_empirical_gpt_run'])
            self.assertFalse(report['ready_for_author_review'])
            text=(root/'draft/manuscript.md').read_text()
            self.assertIn('TECHNICAL MOCK RESULTS',text)
            self.assertIn('MOCK',text)

    def test_pdf_opt_in_is_draft_and_manifest_bound(self):
        try:
            import reportlab
        except ImportError:
            self.skipTest('Optional ReportLab unavailable')
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'pdf-draft'
            report=build_editorial(paper=template('paper.json'),author=template('editorial/author.json'),
                content=template('editorial/content.json'),catalogue=template('editorial/catalogue.json'),
                claims=template('editorial/claims.json'),source_root=ROOT,output=dest,pdf=True)
            self.assertFalse(report['submission_authorized'])
            self.assertGreater((dest/'manuscript.pdf').stat().st_size,1000)
            self.assertEqual(verify_manifest(dest)['verified_files'],7)


if __name__=='__main__': unittest.main()
