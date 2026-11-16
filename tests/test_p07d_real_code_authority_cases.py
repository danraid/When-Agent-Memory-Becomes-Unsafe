"""Mock real-source P07d science and provenance gates without paid requests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.p07d_collect_code_authority_cases import collect,run
from scripts.p07d_code_expert_simulation import ROLES,prompt,parse_vote
from scripts.p07d_detached_code_audit import checked


class RealCodeTests(unittest.TestCase):
    config=Path("protocol/P07D_REAL_CODE_CHANGE_MATRIX.json")

    def api(self,url):
        cfg=json.loads(self.config.read_text())
        n=int(url.split("/pulls/")[1].split("/")[0]) if "/pulls/" in url else int(url.split("/issues/")[1].split("/")[0])
        ix=next(i for i,s in enumerate(cfg["cases"]) if s["pr"]==n)
        if "/files?" in url:
            return json.dumps([{"filename":"src/feature.rs","status":"modified",
                                "changes":2,"patch":"@@ -1 +1 @@\n-legacy()\n+safe_api()"}]).encode()
        if "/reviews?" in url:
            return json.dumps([{"submitted_at":"2026-01-15T00:00:00Z",
                                "body":"Inspect compatibility first.",
                                "state":"COMMENTED"}]).encode()
        if "/issues/" in url:
            return json.dumps([{"created_at":"2026-01-10T00:00:00Z",
                                "body":"Review potential API break."}]).encode()
        return json.dumps({"number":n,"state":"closed",
                           "title":"Source code compatibility change",
                           "body":"Changes actual public code subject to review.",
                           "created_at":"2026-01-01T00:00:00Z",
                           "closed_at":"2026-02-01T00:00:00Z",
                           "merged_at":"2026-02-01T00:00:00Z" if ix in (0,1,4,5) else None,
                           "html_url":"https://github.com/example/pull/"+str(n),
                           "changed_files":1,"head":{"sha":"a"*40}}).encode()

    def raw(self,url):
        if "pep-0387.rst" in url:
            return ("* Similarly a feature cannot be removed without notice\n"
                    "Wait for the warning to appear in at least two minor Python").encode()
        return ("must not specify the "+chr(96)+"#[inline]"+chr(96)+"\n"
                "must not contain any operands except "+chr(96)+"const"+chr(96)+" or "+chr(96)+"sym"+chr(96)).encode()

    def test_cases_are_real_source_shaped_but_not_human_gold(self):
        cases,outcomes,_=collect(self.config,self.api,self.raw)
        self.assertEqual(len(cases["cases"]),8)
        self.assertEqual(len(outcomes["events"]),8)
        self.assertEqual(sum(x["actual_disposition"]=="merged" for x in outcomes["events"]),4)
        for c in cases["cases"]:
            self.assertEqual(len(c["code_patches_retrospective"]),1)
            self.assertEqual(len(c["preclosure_reviews"]),1)
            self.assertTrue(c["historical_normative_applicability_not_verified"])
            self.assertNotIn("actual_disposition",c)
            self.assertNotIn("merged_at",c)
        with TemporaryDirectory() as directory:
            root=Path(directory)/"evidence"
            run(self.config,root,self.api,self.raw)
            checked(root)
            with self.assertRaisesRegex(ValueError,"ALREADY_EXISTS"):
                run(self.config,root,self.api,self.raw)
            (root/"blind_code_cases.json").write_text("corrupted")
            with self.assertRaisesRegex(ValueError,"TAMPERED"):
                checked(root)

    def test_blind_ai_roles_and_verbatim_evidence(self):
        cases,_,_=collect(self.config,self.api,self.raw)
        c=cases["cases"][0]
        self.assertEqual(len(set(ROLES.values())),3)
        for role in ROLES:
            p=prompt(role,c)
            self.assertIn("NOT a human reviewer",p)
            self.assertNotIn("actual_disposition",p)
        v={"assessment":"insufficient_evidence","quote":"safe_api()",
           "rationale":"Historical normative applicability remains unknown.",
           "confidence":0.5,"normative_applicability_verified":False,"human_expert":False}
        self.assertEqual(parse_vote(json.dumps(v),c)[0],v)
        with self.assertRaisesRegex(ValueError,"FALSE_AUTHORITY"):
            parse_vote(json.dumps(dict(v,human_expert=True)),c)
        with self.assertRaisesRegex(ValueError,"VERBATIM"):
            parse_vote(json.dumps(dict(v,quote="Never in source")),c)


if __name__=="__main__":
    unittest.main()
