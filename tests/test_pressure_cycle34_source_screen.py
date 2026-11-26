import unittest,json
from pathlib import Path
from scripts.pressure_cycle34_source_screen import replay
ROOT=Path(__file__).resolve().parents[1]
class ScreenTests(unittest.TestCase):
    def test_no_automatic_qualification(self):
        f=json.loads((ROOT/"fixtures/PRESSURE_CYCLE34_SCREENED_CANDIDATES.json").read_text())
        self.assertEqual(f["project_counts"],{"nodejs":4,"rust-lang":4,"kubernetes":4,"django":4})
        self.assertTrue(all(not x["eligible_for_execution"] and x["reference_label"] is None for x in f["rows"]))
        lookup={str(x["source_comment_id"]):x for x in f["rows"]}
        def fixture(url):
            x=lookup[url.rsplit("/",1)[1]]
            return {"id":x["source_comment_id"],"html_url":x["source_url"],"created_at":x["observed_publication_timestamp"],"updated_at":x["observed_publication_timestamp"]}
        r=replay(f,fixture)
        self.assertEqual(r["matching"],16);self.assertEqual(r["eligible"],0)
