"""Manual-product response inventory, metadata and byte-preserving import. No inference."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from experiments.common import digest, dump
from experiments.round5_ui_model.collection import archive_response
from experiments.round5_ui_model.storage import ROOT, read, verify_freeze, verify_history

SLOTS = [f'S{arm}_{n:02d}' for n in range(1, 9) for arm in (1, 2)]
DEFAULT_SETTINGS = {
    'product': None, 'model_label': None, 'thinking_setting': None, 'tools': None,
    'backend_version': None, 'fresh_context': None, 'memory_isolated': None,
    'custom_instructions_isolated': None, 'contamination_risk': None,
    'prompt_hash_matches': None, 'failed': False, 'truncated': False,
    'elapsed_seconds': None, 'token_usage': None, 'subscription_allocated_cost': None,
    'conversation_reference': None, 'notes': '',
    'provenance': 'user_manual_product_conversation; settings_not_yet_reported'
}


def inbox_files(inbox, resolved_slots=()):
    found, conflicts = {}, []
    for slot in SLOTS:
        matches = [Path(inbox) / (slot + suffix) for suffix in ('.md', '.txt')]
        matches = [p for p in matches if p.is_file()]
        if len(matches) > 1:
            if slot not in resolved_slots:
                conflicts.append(slot)
        elif matches:
            found[slot] = matches[0]
    if conflicts:
        raise ValueError('Both .md and .txt present; preserve both and select explicitly with register: ' + repr(conflicts))
    return found


def primary_records(archive_root):
    primaries = {}
    for path in sorted(Path(archive_root).glob('*/attempt_*/record.json')):
        record = read(path)
        raw = Path(record['raw_path'])
        if not raw.is_file() or digest(raw) != record['raw_sha256']:
            raise ValueError('Archived raw bytes changed: ' + str(path))
        if record['primary']:
            if record['slot'] in primaries:
                raise ValueError('Multiple primary records: ' + record['slot'])
            primaries[record['slot']] = record
    return primaries


def import_inbox(inbox, archive_root, settings, prompt_hashes=None):
    hashes = prompt_hashes or {slot: digest(ROOT / 'prompts' / (slot + '.md')) for slot in SLOTS}
    records, issues, created = [], [], 0
    primaries=primary_records(archive_root)
    for slot in primaries:
        if all((Path(inbox)/(slot+suffix)).is_file() for suffix in ['.md','.txt']):
            issues.append({'slot':slot,'issue':'both_inbox_versions_preserved; explicitly_registered_primary_used'})
    for slot, source in inbox_files(inbox, primaries).items():
        metadata = {**DEFAULT_SETTINGS, **settings}
        sidecar = Path(inbox) / (slot + '.meta.json')
        if sidecar.is_file():
            metadata.update(read(sidecar))
        metadata['expected_prompt_sha256'] = hashes[slot]
        # The stored prompt hash is known; actual UI copy and context are operator reports.
        metadata['prompt_copy_verification_basis'] = 'operator_report_only'
        if not source.stat().st_size and metadata.get('failed') is not True:
            issues.append({'slot': slot, 'issue': 'empty_raw_without_recorded_failure'})
            continue
        previous = [read(p) for p in (Path(archive_root) / slot).glob('attempt_*/record.json')]
        same = next((r for r in previous if r['raw_sha256'] == digest(source)), None)
        if same:
            if digest(Path(same['raw_path'])) != same['raw_sha256']:
                raise ValueError('Archived bytes changed')
            records.append(same)
            if same['metadata'] != metadata:
                issues.append({'slot': slot, 'issue': 'metadata_changed_after_archive; primary_metadata_preserved'})
            continue
        record = archive_response(source, archive_root, slot, metadata)
        records.append(record)
        created += 1
    return {'new_archives': created, 'records': records, 'issues': issues,
            'primary_count': len(primary_records(archive_root))}


def update_index():
    primary = primary_records(ROOT / 'responses/archive')
    sources = inbox_files(ROOT / 'responses', primary)
    def link(label, path):
        return f'[{label}](<{path.resolve().as_posix()}>)'
    count = sum(any((ROOT/'responses'/(slot+suffix)).is_file() and (ROOT/'responses'/(slot+suffix)).stat().st_size>0
                    for suffix in ['.md','.txt']) for slot in SLOTS)
    rows = []
    for n in range(1, 9):
        status = []
        for arm in (1, 2):
            slot = f'S{arm}_{n:02d}'
            if slot in primary:
                meta = primary[slot]['metadata']
                flag = '失败' if meta.get('failed') else '截断' if meta.get('truncated') else '待评审'
                status.append(f'{slot}：已归档/{flag}')
            elif slot in sources and sources[slot].stat().st_size:
                status.append(f'{slot}：原文已保存/未归档')
            else:
                status.append(f'{slot}：待取得原文')
        order = 'S1 → S2' if n % 2 else 'S2 → S1'
        rows.append(f'| {n:02d} | {link(f"S1_{n:02d}", ROOT/f"prompts/S1_{n:02d}.md")} | '
                    f'{link(f"S2_{n:02d}", ROOT/f"prompts/S2_{n:02d}.md")} | {order} | {"；".join(status)} |')
    text = ('# 手动实验索引\n\n'
            '阶段一准备完成后，用户在产品中手动取得原文。每个编号、每种条件都使用全新独立对话；不能在同一个对话里先后跑 S1/S2。\n\n'
            f'计划 16 份；当前收件箱非空原文 {count}/16；首次输出已归档 {len(primary)}/16。没有原文的槽位不补写模型结果。\n\n'
            '先配置同一产品、同一界面模型及思考设置，隔离记忆和自定义指令；全批工具关闭。复制提示文件的完整正文，只取第一份回答。\n\n'
            '首先复制 **S1_01**，然后 S2_01、S2_02、S1_02，依表继续。每份都新建对话，不追问或重新生成。\n\n'
            '| 案例 | S1 普通导师提示 | S2 证据约束提示 | 操作顺序 | 状态 |\n|---|---|---|---|---|\n'
            + '\n'.join(rows) + '\n\n'
            + f'保存方法见 {link("response_collection_guide.md", ROOT/"response_collection_guide.md")}。'
            '原文单独保存为 responses/S1_01.md 等；模型设置和失败/截断标记放元数据，不加到原文。\n\n'
            '该索引用于操作，不提供参考原因或评分。不要向模型发送整个实验目录。刷新命令：'
            '`python -m experiments.round5_ui_model.collect status`。\n')
    (ROOT / 'manual_test_index.md').write_text(text, encoding='utf-8')
    return {'planned': 16, 'inbox_nonempty': count, 'archived_primary': len(primary),
            'missing': [s for s in SLOTS if s not in primary], 'phase': 'awaiting_manual_UI_responses'}


def settings():
    path = ROOT / 'responses/session_settings.json'
    return read(path) if path.exists() else dict(DEFAULT_SETTINGS)


def configure():
    print('只填写产品界面设置。不要输入 API Key、Cookie 或登录 Token。无法确认的项按回车，保存为 unknown/null。')
    meta = dict(DEFAULT_SETTINGS)
    for key, label in [('product','产品名（ChatGPT 或 Codex）'), ('model_label','界面显示的模型名称'),
                       ('thinking_setting','界面思考设置；无可选项请写界面无此选项'), ('tools','工具设置，例如全部关闭')]:
        value = input(label + '：').strip()
        meta[key] = value or None
    for key, label in [('fresh_context','每个槽位都新建独立对话'),('memory_isolated','已隔离历史记忆'),
                       ('custom_instructions_isolated','已隔离自定义/全局指令'),('prompt_hash_matches','将完整复制对应提示，不添加其他内容'),
                       ('contamination_risk','存在上下文或其他污染风险')]:
        value = input(label + '？y=是，n=否，回车=无法确认：').strip().lower()
        meta[key] = True if value == 'y' else False if value == 'n' else None
    meta['notes'] = input('其他界面设置或限制（可留空）：').strip()
    meta['provenance'] = 'operator_UI_self_report_not_independently_verified'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = ROOT / 'responses/settings_history'; folder.mkdir(exist_ok=True)
    dump(folder / (stamp + '.json'), meta)
    dump(ROOT / 'responses/session_settings.json', meta)
    print('模型设置已保存；未显示的后台版本、token 和成本保持 unknown。请在导入原文前完成设置。')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('configure'); sub.add_parser('status'); sub.add_parser('import')
    reg = sub.add_parser('register')
    reg.add_argument('--slot', choices=SLOTS, required=True)
    reg.add_argument('--source', type=Path, required=True)
    reg.add_argument('--failed', action='store_true'); reg.add_argument('--truncated', action='store_true')
    reg.add_argument('--elapsed-seconds', type=float)
    args = parser.parse_args()
    verify_freeze(); verify_history()
    if args.command == 'configure':
        configure(); return
    if args.command == 'import':
        result = import_inbox(ROOT / 'responses', ROOT / 'responses/archive', settings())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'register':
        meta = {**DEFAULT_SETTINGS, **settings()}
        sidecar = ROOT / 'responses' / (args.slot + '.meta.json')
        if sidecar.is_file():
            meta.update(read(sidecar))
        if args.elapsed_seconds is not None and args.elapsed_seconds < 0:
            raise ValueError('Elapsed seconds cannot be negative')
        meta.update({'failed': args.failed or meta['failed'], 'truncated': args.truncated or meta['truncated'],
                     'expected_prompt_sha256': digest(ROOT / 'prompts' / (args.slot + '.md')),
                     'prompt_copy_verification_basis': 'operator_report_only'})
        if args.elapsed_seconds is not None:
            meta['elapsed_seconds'] = args.elapsed_seconds
        result = archive_response(args.source, ROOT / 'responses/archive', args.slot, meta)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(update_index(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
