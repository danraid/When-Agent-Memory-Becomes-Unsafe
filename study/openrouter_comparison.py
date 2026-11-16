"""Exploratory LongMemEval-S comparative benchmark via OpenRouter.

Independent from WAMBU-001 preregistration and private confirmatory holdout.
Requires the upstream cleaned LongMemEval dataset; never fabricates cases.
No automatic retries of potentially billable requests.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

DATASET_URL = ("https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/"
               "resolve/main/longmemeval_s_cleaned.json")
TYPES = ("knowledge-update", "temporal-reasoning", "multi-session",
         "single-session-user", "single-session-assistant", "single-session-preference")
ARMS = ("full_history", "recent_window", "recursive_summary")
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


class BenchmarkError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def json_bytes(data) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(json_bytes(value) + b"\n")
    temporary.replace(path)


def load_dataset(path: Path, variant: str) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    records = json.loads(raw)
    if not isinstance(records, list) or len(records) != 500:
        raise BenchmarkError("OFFICIAL_LONGMEMEVAL_EXPECTS_500_INSTANCES")
    if variant not in ("s_cleaned", "oracle"):
        raise BenchmarkError("UNSUPPORTED_BENCHMARK_VARIANT")
    expected_file = "longmemeval_s_cleaned.json" if variant == "s_cleaned" else "longmemeval_oracle.json"
    if path.name != expected_file:
        raise BenchmarkError("DATASET_FILENAME_VARIANT_MISMATCH")
    seen = set()
    for row in records:
        if not isinstance(row, dict) or not all(k in row for k in (
            "question_id", "question_type", "question", "answer", "question_date",
            "haystack_sessions", "haystack_dates", "haystack_session_ids")):
            raise BenchmarkError("INVALID_OFFICIAL_DATASET_RECORD")
        if row["question_id"] in seen or row["question_type"] not in TYPES:
            raise BenchmarkError("DUPLICATE_ID_OR_UNKNOWN_QUESTION_TYPE")
        seen.add(row["question_id"])
        if not (len(row["haystack_sessions"]) == len(row["haystack_dates"]) ==
                len(row["haystack_session_ids"])):
            raise BenchmarkError("MISMATCHED_SESSION_METADATA")
    return records, digest(raw)


def select_questions(rows: list[dict], count: int, seed: str) -> list[dict]:
    if not 1 <= count <= min(500, len(rows)) or not seed:
        raise BenchmarkError("INVALID_SELECTION")
    grouped = defaultdict(list)
    for entry in rows:
        grouped[entry["question_type"]].append(entry)
    for key in TYPES:
        grouped[key].sort(key=lambda row: digest((seed + "|" + row["question_id"]).encode()))
    selected = []
    for index in range(500):
        for key in TYPES:
            if index < len(grouped[key]):
                selected.append(grouped[key][index])
                if len(selected) == count:
                    return selected
    raise BenchmarkError("SELECTION_IMPOSSIBLE")


def public_sessions(entry: dict) -> list[dict]:
    """Strip ALL answer/evidence/annotation fields before any model call."""
    sessions = []
    triples = zip(entry["haystack_dates"], entry["haystack_sessions"], range(len(entry["haystack_sessions"])))
    for date, turns, original_index in triples:
        if not isinstance(turns, list):
            raise BenchmarkError("MALFORMED_SESSION")
        clean = []
        for turn in turns:
            if not isinstance(turn, dict) or turn.get("role") not in ("user", "assistant") or not isinstance(turn.get("content"), str):
                raise BenchmarkError("MALFORMED_TURN")
            clean.append({"role": turn["role"], "content": turn["content"]})
        sessions.append({"session_date": str(date), "turns": clean, "_index": original_index})
    sessions.sort(key=lambda row: (row["session_date"], row["_index"]))
    for row in sessions:
        del row["_index"]
    return sessions


def compaction_prompt(previous: str, new_sessions: list[dict]) -> str:
    return ("You maintain a compact chronological memory of past user-assistant conversations. "
            "Preserve superseded and updated facts with the latest valid value, dates, user preferences, "
            "and uncertainty. Do not fabricate details. Summarise without seeing the future question. "
            "Your output replaces your previous memory. Use no more than 350 words.\n"
            "PREVIOUS MEMORY:\n" + previous + "\nNEW SESSIONS:\n" +
            json.dumps(new_sessions, ensure_ascii=False) + "\nUPDATED MEMORY:")


def answer_prompt(question: str, question_date: str, context: str, arm: str) -> str:
    return ("I will give you several history chats between you and a user. "
            "Please answer the question based on the relevant chat history. "
            "If the information is not available, say you cannot determine it. "
            "Use the latest information when facts are updated.\n\n"
            "History Chats (" + arm + "):\n" + context +
            "\n\nCurrent Date: " + str(question_date) +
            "\nQuestion: " + question + "\nAnswer:")


def judge_prompt(entry: dict, response: str) -> str:
    """Task-specific LongMemEval judge criteria adapted from upstream evaluate_qa.py."""
    question, answer, task = entry["question"], str(entry["answer"]), entry["question_type"]
    if "_abs" in entry["question_id"]:
        instruction = ("I will give you an unanswerable question, an explanation, and a response "
                       "from a model. Please answer yes if the model correctly identifies the "
                       "question as unanswerable. The model could say that the information is "
                       "incomplete, or some other information is given but the asked information is not.")
        label = "Explanation"
        ending = "Does the model correctly identify the question as unanswerable? Answer yes or no only."
    elif task == "single-session-preference":
        instruction = ("I will give you a question, a rubric for desired personalized response, "
                       "and a response from a model. Please answer yes if the response satisfies "
                       "the desired response. The model does not need to reflect all the points "
                       "in the rubric. The response is correct as long as it recalls and utilizes "
                       "the user's personal information correctly.")
        label = "Rubric"
        ending = "Is the model response correct? Answer yes or no only."
    else:
        instruction = ("I will give you a question, a correct answer, and a response from a model. "
                       "Please answer yes if the response contains the correct answer. Otherwise, "
                       "answer no. If the response is equivalent to the correct answer or contains "
                       "all the intermediate steps to get the correct answer, you should also answer "
                       "yes. If the response only contains a subset of the information required by "
                       "the answer, answer no.")
        if task == "temporal-reasoning":
            instruction += (" In addition, do not penalize off-by-one errors for the number of days. "
                            "If the question asks for the number of days/weeks/months, etc., "
                            "and the model makes off-by-one errors, the response is still correct.")
        elif task == "knowledge-update":
            instruction += (" If the response contains some previous information along with an "
                            "updated answer, the response is correct if it provides the required updated answer.")
        label = "Correct Answer"
        ending = "Is the model response correct? Answer yes or no only."
    return (instruction + "\n\nQuestion: " + question + "\n\n" + label + ": " + answer
            + "\n\nModel Response: " + response + "\n\n" + ending)


def parse_judge(text: str) -> bool | None:
    value = text.strip().lower().strip(".! ")
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def request_chat(key: str, payload: dict, timeout: int = 130) -> dict:
    body = json_bytes(payload)
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe",
        "X-Title": "WAMBU LongMemEval Exploratory Comparison"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Never print response bodies: providers occasionally echo sensitive inputs.
        raise BenchmarkError("OPENROUTER_HTTP_" + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise BenchmarkError("OPENROUTER_TRANSPORT_OUTCOME_UNKNOWN_NO_RETRY") from None


class OpenRouter:
    def __init__(self, key: str, ledger_path: Path, max_calls: int, transport=None):
        if not key:
            raise BenchmarkError("OPENROUTER_SECRET_NOT_SET")
        self.key, self.path, self.cap = key, ledger_path, max_calls
        self.count, self.transport = 0, transport or request_chat
        save(self.path, {"reserved_calls": 0, "max_calls": self.cap,
                         "note": "pre-send reservations; not provider billing"})

    def call(self, model: str, prompt: str, max_tokens: int) -> dict:
        if self.count >= self.cap:
            raise BenchmarkError("FINITE_CALL_LIMIT_REACHED")
        if len(prompt.encode("utf-8")) > 1500000:
            raise BenchmarkError("PROMPT_BYTES_LIMIT_EXCEEDED")
        self.count += 1  # Reserve before network; unknown outcomes are not retried.
        save(self.path, {"reserved_calls": self.count, "max_calls": self.cap,
                         "note": "pre-send reservations; not provider billing"})
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
                   "temperature": 0, "max_tokens": max_tokens, "stream": False}
        started = time.monotonic()
        response = self.transport(self.key, payload)
        if not isinstance(response, dict) or not isinstance(response.get("choices"), list) or not response["choices"]:
            raise BenchmarkError("MALFORMED_PROVIDER_RESPONSE")
        choice = response["choices"][0]
        message = choice.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise BenchmarkError("EMPTY_PROVIDER_CONTENT")
        response_id = response.get("id")
        if not isinstance(response_id, str) or not response_id:
            raise BenchmarkError("MISSING_PROVIDER_RESPONSE_ID")
        observed_model = response.get("model")
        if not isinstance(observed_model, str) or not observed_model:
            raise BenchmarkError("MISSING_OBSERVED_PROVIDER_MODEL")
        return {"text": content.strip(), "response_id": response_id,
                "requested_model": model, "observed_model": observed_model,
                "usage": response.get("usage") or {}, "finish_reason": choice.get("finish_reason"),
                "latency_s": round(time.monotonic() - started, 3),
                "prompt_sha256": digest(prompt.encode("utf-8"))}


def call_outcome(client: OpenRouter, model: str, prompt: str, tokens: int) -> tuple[dict | None, str | None]:
    try:
        return client.call(model, prompt, tokens), None
    except (BenchmarkError, ValueError) as exc:
        return None, str(exc)[:120]


def planned_calls(selected: list[dict], n_models: int, chunk_size: int) -> int:
    # Every subject uses one compaction per chunk, three readers, three separate judges.
    return n_models * sum(math.ceil(len(entry["haystack_sessions"]) / chunk_size) + 6
                          for entry in selected)


def metrics(records: list[dict], selected: list[dict], models: list[str]) -> dict:
    result = {}
    for model in models:
        result[model] = {}
        for arm in ARMS:
            rows = [r for r in records if r["model"] == model and r["arm"] == arm]
            correct = sum(r.get("judge_correct") is True for r in rows)
            scored = sum(r.get("judge_correct") is not None for r in rows)
            n = len(selected)
            per_type = {}
            for typ in TYPES:
                chunk = [r for r in rows if r["question_type"] == typ]
                if chunk:
                    per_type[typ] = {"correct": sum(r.get("judge_correct") is True for r in chunk),
                                     "total": len(chunk)}
            result[model][arm] = {
                "expected_cases": n, "observed_cases": len(rows),
                "scored_cases": scored, "correct": correct, "failed_or_unscored": n - scored,
                "coverage": scored/n, "accuracy_lower_bound_failures_wrong": correct/n,
                "accuracy_on_scored_only_descriptive": correct/scored if scored else None,
                "by_question_type": per_type}
    return result


def run(*, dataset: Path, config_path: Path, output: Path, count: int,
        seed: str, variant: str, secret: str, transport=None) -> dict:
    records, data_hash = load_dataset(dataset, variant)
    config_raw = config_path.read_bytes()
    config = json.loads(config_raw)
    models = config.get("subject_models")
    judge = config.get("judge_model")
    if (not isinstance(models, list) or not 2 <= len(models) <= 8 or
            len(set(models)) != len(models) or
            any(not isinstance(m, str) or not re.fullmatch(r"[a-z0-9_.-]+/[a-zA-Z0-9_.:-]+", m) for m in models)
            or not isinstance(judge, str) or judge in models):
        raise BenchmarkError("INVALID_DISTINCT_MODEL_MATRIX")
    chunk_size = config.get("chunk_sessions", 8)
    recent_size = config.get("recent_sessions", 8)
    cap = config.get("max_calls", 450)
    if (type(chunk_size) is not int or not 2 <= chunk_size <= 20 or
            type(recent_size) is not int or not 1 <= recent_size <= 20 or
            type(cap) is not int or not 1 <= cap <= 5000):
        raise BenchmarkError("INVALID_FINITE_LIMITS")
    selected = select_questions(records, count, seed)
    expected = planned_calls(selected, len(models), chunk_size)
    if expected > cap:
        raise BenchmarkError("PLANNED_CALLS_EXCEED_FINITE_LIMIT:" + str(expected))
    if not secret:
        raise BenchmarkError("OPENROUTER_SECRET_NOT_SET")
    if output.exists() and any(output.iterdir()):
        raise BenchmarkError("OUTPUT_DIRECTORY_MUST_BE_EMPTY")
    output.mkdir(parents=True, exist_ok=True)
    client = OpenRouter(secret, output/"provider_ledger.json", cap, transport)
    selected_ids = [entry["question_id"] for entry in selected]
    metadata = {"classification": "EXPLORATORY_PUBLIC_BENCHMARK_NOT_CONFIRMATORY",
                "benchmark": "LongMemEval", "variant": variant, "official_dataset_url": DATASET_URL if variant == "s_cleaned" else
                DATASET_URL.replace("longmemeval_s_cleaned.json", "longmemeval_oracle.json"),
                "dataset_sha256": data_hash, "config_sha256": digest(config_raw),
                "source_sha256": digest(Path(__file__).read_bytes()),
                "git_sha": os.environ.get("GITHUB_SHA"), "seed": seed,
                "selected_question_ids": selected_ids, "sample_size": len(selected_ids),
                "models": models, "judge_model": judge, "arms": list(ARMS),
                "chunk_sessions": chunk_size, "recent_sessions": recent_size,
                "planned_calls_upper_bound": expected, "max_calls": cap,
                "holdout_touched": False, "scientifically_approved": False,
                "submission_authorized": False, "generated_at": datetime.now(timezone.utc).isoformat()}
    save(output/"run_metadata.json", metadata)
    observations, compactions = [], []
    observed_ids = set()

    def persist():
        save(output/"observations.json", observations)
        save(output/"compactions.json", compactions)

    for entry in selected:
        public = public_sessions(entry)
        history = json.dumps(public, ensure_ascii=False)
        recent = json.dumps(public[-recent_size:], ensure_ascii=False)
        for model in models:
            summary = ""
            error_summary = None
            for offset in range(0, len(public), chunk_size):
                prompt = compaction_prompt(summary, public[offset:offset+chunk_size])
                result, error = call_outcome(client, model, prompt, config.get("summary_max_tokens", 700))
                if error:
                    error_summary = error
                    break
                if result["response_id"] in observed_ids:
                    error_summary = "DUPLICATE_PROVIDER_RESPONSE_ID"
                    break
                observed_ids.add(result["response_id"])
                summary = result["text"]
                compactions.append({"question_id": entry["question_id"], "model": model,
                                    "depth": offset//chunk_size + 1, "error": None,
                                    "summary_sha256": digest(summary.encode()),
                                    "response": {k:v for k,v in result.items() if k != "text"}})
                persist()
            for arm in ARMS:
                record = {"question_id": entry["question_id"], "question_type": entry["question_type"],
                          "abstention": "_abs" in entry["question_id"], "model": model,
                          "arm": arm, "judge_correct": None, "error": None}
                if arm == "recursive_summary" and error_summary:
                    record["error"] = "COMPACTION_FAILED:" + error_summary
                else:
                    context = history if arm == "full_history" else recent if arm == "recent_window" else summary
                    prompt = answer_prompt(entry["question"], entry["question_date"], context, arm)
                    response, err = call_outcome(client, model, prompt, config.get("answer_max_tokens", 300))
                    record["input_prompt_sha256"] = digest(prompt.encode())
                    if err:
                        record["error"] = "ANSWER_FAILED:" + err
                    elif response["response_id"] in observed_ids:
                        record["error"] = "DUPLICATE_PROVIDER_RESPONSE_ID"
                    else:
                        observed_ids.add(response["response_id"])
                        record["hypothesis"] = response["text"]
                        record["answer_provenance"] = {k:v for k,v in response.items() if k != "text"}
                        jprompt = judge_prompt(entry, response["text"])
                        jres, jerr = call_outcome(client, judge, jprompt, config.get("judge_max_tokens", 16))
                        record["judge_prompt_sha256"] = digest(jprompt.encode())
                        if jerr:
                            record["error"] = "JUDGE_FAILED:" + jerr
                        elif jres["response_id"] in observed_ids:
                            record["error"] = "DUPLICATE_JUDGE_RESPONSE_ID"
                        else:
                            observed_ids.add(jres["response_id"])
                            record["judge_correct"] = parse_judge(jres["text"])
                            record["judge_raw"] = jres["text"]
                            record["judge_provenance"] = {k:v for k,v in jres.items() if k != "text"}
                            if record["judge_correct"] is None:
                                record["error"] = "INVALID_JUDGE_VERDICT"
                observations.append(record)
                persist()
                print(entry["question_id"], model, arm,
                      "scored" if record["judge_correct"] is not None else "unscored", flush=True)

    aggregate = metrics(observations, selected, models)
    total_expected = len(selected) * len(models) * len(ARMS)
    scored = sum(r["judge_correct"] is not None for r in observations)
    status = {"classification": metadata["classification"],
              "status": "EXPLORATORY_COMPLETE_NOT_SCIENTIFICALLY_APPROVED"
              if scored == total_expected else "INCOMPLETE_WITH_PRESERVED_FAILURES",
              "selected_questions": len(selected), "models": len(models),
              "expected_answers": total_expected, "scored_answers": scored,
              "provider_calls_reserved": client.count,
              "descriptive_metrics": aggregate, "scientifically_approved": False,
              "submission_authorized": False, "holdout_touched": False,
              "limitations": [
                  "Small stratified pilots do not estimate population benchmark accuracy.",
                  "LongMemEval measures retrieval/answer updating, not unauthorised policy actions.",
                  "Full history vs compacted vs recent has unequal information/token budgets.",
                  "This client uses adapted official judge criteria via OpenRouter; not the upstream official scoring executable.",
                  "LLM judge may disagree with independent human adjudication.",
                  "No p-values, independent external validation, or confirmatory conclusions."]}
    save(output/"summary.json", status)
    for model in models:
        filename = re.sub(r"[^A-Za-z0-9_.-]", "_", model)
        for arm in ARMS:
            path = output/"hypotheses"/(filename + "__" + arm + ".jsonl")
            path.parent.mkdir(parents=True, exist_ok=True)
            subset = [r for r in observations if r["model"] == model and r["arm"] == arm and "hypothesis" in r]
            path.write_text("".join(json.dumps({"question_id": r["question_id"],
                                                "hypothesis": r["hypothesis"]}, ensure_ascii=False) + "\n"
                                    for r in subset), encoding="utf-8")
    manifest = {"classification": metadata["classification"], "dataset_sha256": data_hash,
                "source_sha256": metadata["source_sha256"], "config_sha256": metadata["config_sha256"],
                "files_sha256": {p.relative_to(output).as_posix(): digest(p.read_bytes())
                                 for p in sorted(output.rglob("*")) if p.is_file() and p.name != "manifest.json"},
                "scientifically_approved": False, "submission_authorized": False}
    save(output/"manifest.json", manifest)
    return status


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--config", default=Path("study/openrouter_models.json"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--variant", choices=("s_cleaned", "oracle"), default="s_cleaned")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--seed", default="WAMBU-OPENROUTER-LONGMEMEVAL-DEVELOPMENT-V1")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("Live provider calls require --execute")
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER")
    result = run(dataset=args.dataset, config_path=args.config, output=args.out,
                 count=args.limit, seed=args.seed, variant=args.variant, secret=key or "")
    print(json.dumps({k: result[k] for k in ("status", "selected_questions", "expected_answers",
                                             "scored_answers", "provider_calls_reserved")}, indent=2))
    return 0 if result["status"] == "EXPLORATORY_COMPLETE_NOT_SCIENTIFICALLY_APPROVED" else 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BenchmarkError as exc:
        raise SystemExit("BLOCKED_OR_FAILED:" + str(exc)) from None
