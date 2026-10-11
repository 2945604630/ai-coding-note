"""Reuse immutable v1 rules/prompts/controlled executor; phase2-only storage."""
import json
from pathlib import Path
from experiments.feature_validation.F01_response_adaptation import core as v1
from experiments.common import dump,digest

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent
S0=v1.baseline
IDS=[f'H{n:02d}' for n in range(1,13)]
JUDGE_IDS=['H01','H04','H07','H08','H10','H12']


def literal_quote(output,field,quote):return isinstance(output.get(field),str) and bool(quote) and quote in output[field]


def make_trace(answer,output,metadata,understood,feedback,origin):
    return {'input_original':answer,'model_output':output,'metadata':metadata,
        'model_next_action':output.get('next_action') if isinstance(output,dict) else None,
        'understood_system_intent_self_report':understood,'user_feedback_original':feedback,
        'origin':origin,'formal_difficult_sample':False,'real_student_outcome_measured':False,
        'user_is_beginner_verified':False}


def preserve_history():
    previous=v1.read(PARENT/'completion_manifest.json')['sha256']
    hashes={str((PARENT/p).resolve()):sha for p,sha in previous.items()}
    hashes[str((PARENT/'completion_manifest.json').resolve())]=digest(PARENT/'completion_manifest.json')
    hashes.update(v1.read(PARENT/'historical_manifest.json')['sha256'])
    for path,sha in hashes.items():
        if digest(path)!=sha:raise ValueError('Historical file changed: '+path)
    return hashes


def verify():
    manifest=v1.read(ROOT/'freeze_manifest.json')
    for path,sha in manifest['sha256'].items():
        if digest(path)!=sha:raise ValueError('Phase2 frozen file changed: '+path)
    for path,sha in v1.read(ROOT/'historical_manifest.json')['sha256'].items():
        if digest(path)!=sha:raise ValueError('Historical result changed: '+path)
    return len(manifest['sha256'])
