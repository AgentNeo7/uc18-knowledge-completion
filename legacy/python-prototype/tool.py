"""Standalone deterministic synthetic prototype. No runtime integration or domain authority."""
import argparse
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys


def obj(x, keys):
    if not isinstance(x, dict) or set(x) != set(keys.split()):
        raise ValueError("object fields must be: " + keys)
    return x


def text(x):
    if not isinstance(x, str) or not x or len(x) > 2048:
        raise ValueError("expected nonempty bounded string")
    return x


def arr(x):
    if not isinstance(x, list) or len(x) > 500:
        raise ValueError("expected list of at most 500 elements")
    return x


def names(x):
    values = [text(v) for v in arr(x)]
    if len(values) != len(set(values)):
        raise ValueError("duplicate identifiers")
    return values


def num(x, minimum=0):
    if type(x) not in (int, float) or not math.isfinite(x) or x < minimum or x > 1e12:
        raise ValueError("invalid bounded number")
    return x


def integer(x, minimum=0):
    if type(x) is not int:
        raise ValueError("expected integer")
    return num(x, minimum)


def boolean(x):
    if type(x) is not bool:
        raise ValueError("expected boolean")
    return x


def unique(rows):
    ids = [text(x["id"]) for x in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate record ID")


def scalar(x):
    if x is not None and type(x) not in (str, int, float, bool):
        raise ValueError("expected scalar value")
    if type(x) in (int,float) and not math.isfinite(x):
        raise ValueError("nonfinite number")
    return x


def result(**kw):
    return {"evidence_class": "simulated", "analysis_completed": True, **kw}


def analyze(payload):
    obj(payload, "spec_version evidence_class data")
    if type(payload["spec_version"]) is not int or payload["spec_version"] != 1 or payload["evidence_class"] != "simulated":
        raise ValueError("only spec_version 1 synthetic evidence_class simulated supported")
    return run(copy.deepcopy(payload["data"]))


def matches(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and matches(actual[k], v) for k,v in expected.items())
    return actual == expected


def read_json(path):
    if path.stat().st_size > 1000000:
        raise ValueError("input exceeds 1000000 bytes")
    return json.loads(path.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--expect", type=Path, help="optional recursive subset oracle; mismatch exits 1")
    a=p.parse_args()
    try:
        if a.input.resolve() == a.output.resolve() or (a.expect and a.expect.resolve() == a.output.resolve()):
            raise ValueError("output must not overwrite input or oracle")
        output=analyze(read_json(a.input))
        expected=read_json(a.expect) if a.expect else None
        a.output.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
        return 0 if expected is None or matches(output,expected) else 1
    except (ValueError, KeyError, TypeError, OSError, RecursionError, OverflowError) as e:
        print("invalid input: "+str(e),file=sys.stderr)
        return 2

def run(d):
    obj(d,'questions scenarios approved_answers budget');questions=arr(d['questions']);unique(questions);scenarios=arr(d['scenarios']);unique(scenarios);answers=arr(d['approved_answers']);budget=num(d['budget'])
    qi={q['id']:q for q in questions}
    for q in questions:obj(q,'id effort source');num(q['effort'],0.000001);text(q['source'])
    unsupported=[];valid=[]
    for s in scenarios:
        obj(s,'id requires supported');names(s['requires']);boolean(s['supported'])
        if not s['supported'] or not set(s['requires'])<=set(qi):unsupported.append(s['id'])
        else:valid.append(s)
    known=set();ignored=[]
    for a in answers:
        obj(a,'question status owner revision');text(a['question']);text(a['status']);text(a['owner']);text(a['revision'])
        if a['question'] not in qi:raise ValueError('answer references unknown question')
        if a['status']=='approved' and a['owner']!='AI':known.add(a['question'])
        else:ignored.append(a['question'])
    def covered(ks):return {s['id'] for s in valid if set(s['requires'])<=ks}
    initial=covered(known);selected=[];spent=0;ks=set(known)
    while True:
        candidates=[]
        for q in questions:
            if q['id'] in ks or spent+q['effort']>budget:continue
            gain=len(covered(ks|{q['id']})-covered(ks))
            support=sum(q['id'] in s['requires'] for s in valid)
            if support:candidates.append((-gain/q['effort'],-support/q['effort'],q['id']))
        if not candidates:break
        chosen=sorted(candidates)[0][2];selected.append(chosen);ks.add(chosen);spent+=qi[chosen]['effort']
    fs=set(known);frequency_order=[];fs_spent=0
    for q in sorted(questions,key=lambda q:(-sum(q['id'] in s['requires'] for s in valid),q['id'])):
        if q['id'] not in fs and fs_spent+q['effort']<=budget and any(q['id'] in s['requires'] for s in valid):
            fs.add(q['id']);frequency_order.append(q['id']);fs_spent+=q['effort']
    return result(status='unsupported_scenarios' if not valid else 'question_plan', selected_questions=selected,newly_resolvable=sorted(covered(ks)-initial),effort_assumption=spent,unsupported_scenarios=sorted(unsupported),ignored_unapproved=sorted(ignored),published_answers=0,question_sources={q:qi[q]['source'] for q in selected},frequency_baseline={'selected_questions':frequency_order,'newly_resolvable':sorted(covered(fs)-initial),'effort':fs_spent},comparative_limit='Only authored synthetic mappings; no expert-time or held-out benefit established.')

if __name__ == "__main__":
    sys.exit(main())
