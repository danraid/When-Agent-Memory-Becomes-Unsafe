#!/usr/bin/env python3
"""Verify real public supersession document provenance, without assigning gold.

Uses git cat-file and git show from prechecked exact-revision repositories.
Never uses the live main branch, no API inference or confirmatory access.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def git(root, *args):
    return subprocess.run(["git","-C",str(root),*args],check=True,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout


def verify(manifest:Path, roots:dict[str,Path]):
    raw=json.loads(manifest.read_text(encoding="utf-8"))
    if raw["split"]!="public_development_source_review_only":
        raise ValueError("NON_PUBLIC_DEVELOPMENT_SPLIT")
    if raw["status"]!="SOURCE_CANDIDATES_NOT_HUMAN_ADJUDICATED":
        raise ValueError("UNAUTHORISED_SCIENTIFIC_PROMOTION")
    rows=[]
    for pair in raw["paired_documents"]:
        repo=pair["repository"]
        root=roots[repo]
        commit=git(root,"rev-parse","HEAD").decode().strip()
        if commit!=pair["revision"]:
            raise ValueError("PINNED_SOURCE_COMMIT_MISMATCH_"+pair["id"])
        texts=[]
        for kind in ("source","target"):
            path=pair[kind+"_path"]
            blob=git(root,"rev-parse",f"{commit}:{path}").decode().strip()
            if blob!=pair[kind+"_blob_sha"]:
                raise ValueError("SOURCE_BLOB_SHA_MISMATCH_"+pair["id"])
            body=git(root,"show",f"{commit}:{path}")
            texts.append(body.decode("utf-8"))
        source,target=texts
        num=pair["target_number"]
        if repo=="python/peps":
            if not re.search(r"(?mi)^Superseded-By:\s*"+re.escape(num)+r"\s*$",source):
                raise ValueError("MISSING_EXPLICIT_SOURCE_SUPERSESSION_"+pair["id"])
            if not re.search(r"(?mi)^PEP:\s*"+re.escape(num)+r"\s*$",target):
                raise ValueError("TARGET_ID_MISMATCH_"+pair["id"])
        elif repo=="rust-lang/rfcs":
            if not re.search(r"(?i)superseded\s+by[^\n]{0,120}"+re.escape(num),source):
                raise ValueError("MISSING_EXPLICIT_SOURCE_SUPERSESSION_"+pair["id"])
            if not target.startswith("- Feature Name:"):
                raise ValueError("TARGET_NOT_RFC_"+pair["id"])
            if num not in pair["target_path"]:
                raise ValueError("TARGET_ID_MISMATCH_"+pair["id"])
        else:
            raise ValueError("UNAPPROVED_SOURCE_REPOSITORY")
        if pair["reference_action"] is not None or pair["human_review_status"]!="PENDING":
            raise ValueError("FORGED_HUMAN_REVIEW")
        rows.append({
            "id":pair["id"],"repository":repo,"source_commit":commit,
            "source_blob_sha":pair["source_blob_sha"],"target_blob_sha":pair["target_blob_sha"],
            "source_sha256":hashlib.sha256(source.encode()).hexdigest(),
            "target_sha256":hashlib.sha256(target.encode()).hexdigest(),
            "explicit_document_supersession_link_verified":True,
            "temporal_authority_adjudication":"NOT_DONE",
            "human_reference":"NOT_DONE","source_text_redistributed":False
        })
    return {"status":"PUBLIC_SOURCE_SUPERSESSION_PROVENANCE_VERIFIED_ONLY",
            "pairs":len(rows),"rows":rows,"human_adjudications":0,
            "model_calls":0,"confirmatory_touched":False,
            "scientific_approval":False,
            "task_action_labels_created":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,default=Path("protocol/P07_PUBLIC_SOURCE_CANDIDATES.json"))
    p.add_argument("--python-peps",type=Path,required=True)
    p.add_argument("--rust-rfcs",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=verify(a.manifest,{"python/peps":a.python_peps,"rust-lang/rfcs":a.rust_rfcs})
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","pairs","human_adjudications","model_calls")},indent=2))

if __name__=="__main__":
    main()
