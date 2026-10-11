"""Per-input provenance is a declaration, never authenticated learner identity."""
KINDS = {'manual_browser', 'automated_test', 'simulated_student', 'historical_replay', 'unknown'}


def record(kind=None, session=None):
    kind = kind if kind in KINDS else 'unknown'
    if kind == 'unknown' and session and session.get('source_type') == 'automated_test':
        kind = 'automated_test'
    return {'kind': kind, 'basis': 'caller_declaration_not_identity_certification',
            'real_student_verified': False}


def answer_origin(turn):
    correction = turn.get('input_origin_correction')
    if correction and correction.get('kind') in KINDS:
        return {'kind':correction['kind'],'basis':'append_only_source_correction',
                'correction_event_id':correction['event_id'],'real_student_verified':False}
    public = turn.get('public_input') or {}
    explicit = public.get('answer_input_origin')
    if explicit:
        return explicit
    # Legacy explicit automated-input metadata can be retained. A session tag
    # or interactive_user_unverified_role is insufficient to certify a person.
    kind = 'automated_test' if public.get('data_origin') == 'automated_engineering_test_not_real_user' else 'unknown'
    return {'kind': kind, 'basis': 'legacy_input_metadata' if kind != 'unknown' else 'legacy_origin_not_recorded',
            'real_student_verified': False}


def data_label(origin):
    return {'manual_browser':'browser_manual_input_role_unverified',
            'automated_test':'automated_engineering_test_not_real_user',
            'simulated_student':'frozen_simulated_student_not_real_user',
            'historical_replay':'historical_replay_not_live_user',
            'unknown':'input_origin_unknown_not_certified'}[origin['kind']]
