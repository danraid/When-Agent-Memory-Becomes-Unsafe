import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from article_hub.experiment import synthetic_paired_demo
from article_hub.report import run_demo
from article_hub.statistics import paired_difference
from scripts.hub import verify_manifest


class ExperimentTests(unittest.TestCase):
    def test_paired_statistics(self):
        out=paired_difference([True,False,True,True],[False,False,True,False])
        self.assertEqual(out['pairs'],4)
        self.assertAlmostEqual(out['risk_difference'],0.5)
        with self.assertRaises(ValueError):
            paired_difference([True],[False])

    def test_synthetic_is_deterministic_and_not_empirical(self):
        one=synthetic_paired_demo(seed=40,n=300)
        self.assertEqual(one,synthetic_paired_demo(seed=40,n=300))
        self.assertNotEqual(one['outcomes_sha256'],synthetic_paired_demo(seed=41,n=300)['outcomes_sha256'])
        self.assertFalse(one['scientific_evidence'])
        self.assertFalse(one['claim_about_real_agents'])

    def test_report_hash_verification_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'demo'
            run_demo(paper={'title':'Test Synthetic Study'}, output=folder, seed=2026, n=200)
            self.assertEqual(verify_manifest(folder)['verified_files'],2)
            manifest=json.loads((folder/'manifest.json').read_text())
            self.assertIn('article_hub/experiment.py',manifest['engine_sources'])
            self.assertIn('NOT A SCIENTIFIC ARTICLE',(folder/'technical_report.md').read_text())
            (folder/'synthetic_experiment.json').write_text('tampered')
            with self.assertRaisesRegex(ValueError,'hash or size mismatch'):
                verify_manifest(folder)

    def test_report_rejects_changed_engine_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'demo'
            run_demo(paper={'title':'Test'},output=root)
            p=root/'manifest.json'
            record=json.loads(p.read_text())
            record['engine_sources']['article_hub/experiment.py']='0'*64
            p.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'engine source mismatch'):
                verify_manifest(root)

    def test_report_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            run_demo(paper={'title':'Test'},output=root/'demo')
            path=root/'demo/manifest.json'
            data=json.loads(path.read_text())
            data['files'][0]['path']='../../outside.json'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Unsafe or missing'):
                verify_manifest(root/'demo')

    def test_cli_offline_full_cycle(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'demo'
            cmd=[sys.executable,str(root/'scripts/hub.py'),'demo','--output',str(dest)]
            completed=subprocess.run(cmd,cwd=root,capture_output=True,text=True)
            self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
            self.assertFalse(json.loads(completed.stdout)['scientific_approval'])
            check=subprocess.run([sys.executable,str(root/'scripts/hub.py'),'verify','--directory',str(dest)],
                cwd=root,capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stderr)
