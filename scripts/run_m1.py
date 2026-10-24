#!/usr/bin/env python3
"""Standard-library M1 controller for isolated database-first trials."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
JDK21 = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
JAVA = JDK21 / "bin" / "java"
CP = f"{ROOT / 'target/classes'}:{ROOT / 'target/dependency'}/*"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def run_java(class_name, *args):
    return subprocess.run([str(JAVA), "-cp", CP, class_name, *args], text=True,
                          capture_output=True, check=True, timeout=45)


def save(path, name, content):
    (path / name).write_text(content, encoding="utf-8")


def snapshot(path, name, topic, group, account):
    result = run_java("com.jeshwin.crashlab.M1Inspector", topic, group, account, name)
    save(path, f"{name}.json", result.stdout)
    return json.loads(result.stdout)


def hashes():
    files = [p for p in ROOT.rglob("*") if p.is_file() and "target" not in p.parts
             and "results" not in p.parts]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}


def image_digests():
    result = subprocess.run(
        ["docker", "image", "inspect", "apache/kafka:4.1.2", "postgres:17.11-bookworm",
         "--format", '{{.RepoTags}} {{join .RepoDigests " "}}'],
        text=True, capture_output=True, check=True, timeout=30)
    return result.stdout.splitlines()


def validated_barrier(process, run_id, event_id, expected_offset, log):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        line = process.stdout.readline()
        if line:
            log.append({"timestamp": now(), "stream": "stdout", "line": line.rstrip()})
            if line.startswith("BARRIER "):
                required = [f"runId={run_id}", f"eventId={event_id}",
                            "strategy=db-first", "phase=after-db-commit",
                            f"offset={expected_offset}"]
                if not all(value in line for value in required):
                    raise RuntimeError(f"Unexpected barrier: {line.rstrip()}")
                return line.rstrip()
        elif process.poll() is not None:
            raise RuntimeError(f"Consumer exited before barrier: {process.returncode}")
    raise TimeoutError("Timed out waiting for validated barrier")


def consumer(path, topic, group, event, account, run_id, pause):
    return subprocess.Popen([str(JAVA), "-cp", CP, "com.jeshwin.crashlab.CrashConsumer",
                             topic, group, event, account, str(pause).lower(), run_id],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)


def trial(kind):
    run_id = f"m1-{kind}-{uuid.uuid4().hex[:12]}"
    path = ROOT / "results" / run_id
    path.mkdir(parents=True, exist_ok=False)
    topic = f"account-credits-{run_id}"
    group = f"group-{run_id}"
    event = f"event-{run_id}"
    account = f"account-{run_id}"
    meta = {"runId": run_id, "kind": kind, "strategy": "db-first", "startedAt": now(),
            "topic": topic, "group": group, "eventId": event, "accountId": account,
            "java": subprocess.run([str(JAVA), "-version"], text=True, capture_output=True).stderr,
            "python": sys.version, "sourceHashes": hashes(), "imageDigests": image_digests()}
    try:
        setup = run_java("com.jeshwin.crashlab.M1FixtureTool", topic, group, event, account, run_id)
        save(path, "fixture.json", setup.stdout)
        fixture = json.loads(setup.stdout)
        baseline = snapshot(path, "baseline", topic, group, account)
        logs = []
        first = consumer(path, topic, group, event, account, run_id, kind == "crash")
        if kind == "baseline":
            stdout, stderr = first.communicate(timeout=45)
            save(path, "consumer-baseline.stdout.log", stdout)
            save(path, "consumer-baseline.stderr.log", stderr)
            after = snapshot(path, "post-completion", topic, group, account)
            passed = first.returncode == 0 and after["balance"] == 100 and after["committedOffset"] == fixture["offset"] + 1
            assertion = {"passed": passed, "consumerExit": first.returncode,
                         "expected": {"balance": 100, "committedOffset": fixture["offset"] + 1},
                         "actual": after}
        else:
            barrier = validated_barrier(first, run_id, event, fixture["offset"], logs)
            save(path, "controller-events.json", json.dumps(logs, indent=2) + "\n")
            first.kill()
            first.wait(timeout=15)
            first_stdout, first_stderr = first.communicate()
            save(path, "consumer-killed.stdout.log", first_stdout)
            save(path, "consumer-killed.stderr.log", first_stderr)
            post_kill = snapshot(path, "post-kill-pre-restart", topic, group, account)
            restart = consumer(path, topic, group, event, account, run_id, False)
            restart_stdout, restart_stderr = restart.communicate(timeout=45)
            save(path, "consumer-restart.stdout.log", restart_stdout)
            save(path, "consumer-restart.stderr.log", restart_stderr)
            final = snapshot(path, "post-restart", topic, group, account)
            replayed = f"offset={fixture['offset']}" in restart_stdout and f"eventId={event}" in restart_stdout
            passed = (first.returncode == -signal.SIGKILL and post_kill["balance"] == 100
                      and post_kill["committedOffset"] == fixture["offset"] and restart.returncode == 0
                      and final["balance"] == 200 and final["committedOffset"] == fixture["offset"] + 1 and replayed)
            assertion = {"passed": passed, "barrier": barrier,
                         "killedPid": first.pid, "killedExit": first.returncode,
                         "restartExit": restart.returncode, "replayedSameOffset": replayed,
                         "expected": {"postKillBalance": 100, "postKillCommittedOffset": fixture["offset"],
                                      "finalBalance": 200, "finalCommittedOffset": fixture["offset"] + 1},
                         "postKill": post_kill, "final": final}
        meta["completedAt"] = now()
        meta["fixture"] = fixture
        meta["assertion"] = assertion
        save(path, "result.json", json.dumps(meta, indent=2) + "\n")
        print(json.dumps({"resultPath": str(path), "passed": assertion["passed"]}))
        return 0 if assertion["passed"] else 2
    except Exception as exc:
        meta["completedAt"] = now()
        meta["invalid"] = True
        meta["error"] = repr(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            meta["failedCommand"] = exc.cmd
            meta["failedStdout"] = exc.stdout
            meta["failedStderr"] = exc.stderr
        save(path, "result.json", json.dumps(meta, indent=2) + "\n")
        print(json.dumps({"resultPath": str(path), "invalid": True, "error": repr(exc)}))
        return 3


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"baseline", "crash"}:
        raise SystemExit("Usage: run_m1.py baseline|crash")
    raise SystemExit(trial(sys.argv[1]))
