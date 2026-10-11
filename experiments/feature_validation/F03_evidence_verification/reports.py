"""Generate two short reports from saved evidence; never execute code or call a model."""
import json
from statistics import median

from experiments.common import digest
from .verifier import ROOT, load_registry


def link(path, label=None):
    path = path.resolve()
    return '[' + (label or path.name) + '](<' + path.as_posix() + '>)'


def main():
    registry = load_registry()
    formal = ROOT / 'results/formal_v1'
    summary = json.loads((formal / 'summary.json').read_text(encoding='utf-8'))
    rows = json.loads((formal / 'raw_results.json').read_text(encoding='utf-8'))
    statuses = [json.loads((ROOT / 'results' / name).read_text(encoding='utf-8'))['exit_code']
                for name in ['formal_command_status.json', 'regression_command_status.json', 'cli_smoke_status.json']]
    assert statuses == [0, 0, 0] and summary['all_frozen_expectations_match']
    table = []
    quotes = []
    for row in rows:
        r = row['record']
        check = row['check_id']
        show = lambda x: json.dumps(x, ensure_ascii=False) if x is not None else '未运行'
        verdict = {'supported': '支持', 'refuted': '反驳', 'inconclusive': '无法核验'}[row['actual_status']]
        table.append(f"| {check} | {r['source_version']} | `{show(r['args'])}` | {show(r['actual_output'])} | {show(r['reference_output'])} | {verdict} | {link(formal / check / 'result.json', check + '证据')} |")
        source = r['claim'].get('source')
        origin = '作者负例，非模型输出' if not source else link(ROOT / source['path'], source.get('field') or '历史原文')
        if check == 'B02':
            origin += '；模型引用的冻结模拟学生话语，不是模型自己的结论'
        quotes.append(f"- {check}：“{r['claim']['text']}”。来源：{origin}。")
    times = [row['record']['elapsed_ms'] for row in rows if row['record']['execution_success']]
    full = '\n'.join(table)
    quoted = '\n'.join(quotes)
    result = f'''# F03 实际测试结果

2026-10-11。一次正式主测试，三个复用案例各三项核验；本轮新增模型调用 **0 次**。未生成或修改历史模型回答。

正式结果：**6 条可执行谓词，正确支持 4 条、正确反驳 2 条，错误支持/反驳 0 条；其余 3 条无法核验。** 这是显式谓词核验结果，不是自然语言诊断或教学准确率。

| 核验 | 源码版本 | 合法参数 | 实际返回 | 参考返回 | 陈述判定 | 证据 |
|---|---|---|---|---|---|---|
{full}

A 是边界错误。预测输出 3 可以成立，同时它不满足应输出 6 的题意。A03 的学生理解不由运行决定。

B 使用以前审核过的局部修改：n=1 返回 1，满足该输入；n=3 返回 8，而参考为 6。完整修复陈述被合法反例反驳。B03 引用原版输出 5，但要求核验局部版，执行前拦截，不把旧预测误判为该版本的错误输出。原版和局部版源码哈希不同。

C 含可疑的 `best=0`，但另有全负数处理。三个执行输入均与参考相符，模块未报告 bug；这些有限执行仍不足以确认整个输入域或唯一原因。

## 分母与来源

| 指标 | 实际计数与分母 |
|---|---|
| 可执行谓词得到明确判定 | 6/9 核验；其中支持 4/6，反驳 2/6 |
| 错误支持或错误反驳 | 0/6，按冻结显式谓词与实际执行核对 |
| 无法核验 | 3/9：学生理解、版本冲突、整体正确性陈述各 1 |
| 版本冲突拦截 | 1/9 |
| 非法输入拦截 | 正式主测试 0/9；守卫回归 4/4 非法输入 |
| 实际执行 | 8/9，成功 8/8，异常 0/8 |
| 其他冻结预期是否满足 | 9/9；不把此数当作教学准确率 |

历史真实 AI 的四条明确输出预测均获支持。两个反驳分别是作者人工负例和 AI 引用的模拟学生“完全修好”陈述，**不能报告为两条真实 AI 错误诊断**。历史 AI 的另外三条被保留为无法核验。本轮没有从选定原文中发现可用的错误数值预测，故明确使用作者负例验证反驳功能。

自然语言到结构化谓词的转换由作者明确标注，并有以下原文供人工复核；程序自动验证的是转换后的命题，不是任意自然语言语义。没有独立人类语义认证。

{quoted}

## 受控执行与记录

复用既有 `experiments.runner.execute`、输入合同与独立 `common.oracle`。正式执行为 Python 3.12.10 / Windows。8/8 执行包报告 1.5 秒、8192 字节、128 MiB 内存限制已建立，Windows Job 活动进程限制 1。本次执行成功项含哈希校验的接口耗时 {min(times):.3f}～{max(times):.3f} ms，中位数 {median(times):.3f} ms；不据此宣称任意程序的延迟稳定性。

每项保存请求、实际源码及哈希、实际执行器返回包、参考来源、原文及其来源哈希、核验状态和证据路径。版本冲突项保留请求与失败记录，没有执行结果。未公开的底层进程 stderr 不被冒称为完整原始字节日志。

采用白名单审核代码；Job、AST 限制与超时不构成针对恶意代码的文件/网络隔离，不能执行任意用户或 AI 新代码。当前结果可信范围限于已审核版本、合法输入与已审核参考合同。

## 必要修复与确定性回归

首次冻结准备因旧清单的反斜杠路径发生 KeyError，正式主测试尚未开始。修复为两侧路径统一，且只允许空目录恢复；未改动案例或历史结果。见 {link(ROOT / 'results/prepare_failure_01.log')}。实现前红测试失败保留在 {link(ROOT / 'results/tests_red.log')}。正式主测试未出现需要重跑的客观核验错误。

回归 **9/9 测试方法通过**，产生 17 条独立核验记录、7 次实际执行，另验证一次拒绝覆盖：非法输入 4 条，未知版本/哈希/陈述版本冲突各 1 条；参考冲突 1 条、放宽限制 2 条均在执行前拦截。三个既有守卫夹具实际触发 timeout、IndexError、output_limit，各 1 次；全部保留包和失败日志，均不支持或反驳输出预测。bool 预测不被当作整数 0；单个局部修改通过仍保持整体正确性待定。

见 {link(ROOT / 'results/regression_command.log')}、{link(ROOT / 'results/regression_v1/archived_path_map.json', '回归归档索引')}。归档包保持临时路径原文，索引提供当前存储位置与哈希。

CLI 从项目目录外实际运行成功，证据路径均存在；见 {link(ROOT / 'results/cli_smoke_status.json')}。此单次接口冒烟检查不混入正式九项分母。没有重采样、替换失败样本或追加教学案例。

汇总和完整命令见 {link(formal / 'summary.json')}、{link(ROOT / 'results/formal_command.log')}。是否保留功能见 {link(ROOT / 'F03_next_step_decision.md')}。
'''
    decision = '''# F03 下一步决策

**F03 工程验收 PASS；建议保留为审核代码的确定性证据层。** 不据此恢复 A+B 工作台或宣称教学创新成立。

| 验收问题 | 本轮实际判断 |
|---|---|
| 是否真实运行 | 是：一次正式主测试，8 次实际执行、1 次版本冲突阻断；CLI 从项目外实际启动成功。 |
| 执行可信且可复现吗 | 在审核版本和合同范围内有可信依据：源码/参考/输入与历史来源哈希、资源限制、执行包和命令齐全；一次主测试不代表跨环境稳定性已经验证。 |
| 事实支持/反驳准确吗 | 六条明确可执行谓词中支持 4、反驳 2，与冻结预期和实际运行一致，错误支持/反驳 0/6。仅此探索性样本，不能推为通用自然语言准确率。 |
| 是否有误报/漏报 | 本样本未见客观核验误报/漏报；正确特殊写法的三项输入均匹配参考。未作程序全域或任意陈述的完备性评价。 |
| 局部修改、版本和非法输入 | 局部版 n=1 通过，n=3 失败；不确认完整修复。陈述版本冲突被拦截。未知版本、错误哈希、4 条非法输入的回归都阻止执行。 |
| 可直接复用吗 | 接口可以作为后续功能的证据层复用，但本轮未接入 F01/F02。调用者须传入登记版本、合法输入及明确谓词；不能自行提供任意代码。 |
| 哪些仍无法执行确认 | 学生意图/理解、长期知识状态、唯一根因、自然语言因果解释、单次测试能否证明整体修复。语义映射仍需人工复核。 |
| 是否值得进入 F04 | 从证据层工程条件看，值得由用户审核后另行开展 F04 小范围验证；尚未定义或验收 F04，不自动进入。 |

保留最小实现：既有执行器＋输入合同/独立参考＋冻结版本白名单＋结构化谓词＋追加式证据记录。无需为 F03 增加 S2、AI 自评、根因自动确诊、知识图谱或新平台。

局限是审核范围小、参考实现依赖已有人工审核、历史自然语言映射未经独立人类复核，以及没有任意恶意代码的 OS 隔离。调用者不得把 `supported` 展示为“学生已经掌握”“唯一根因成立”或“程序整体正确”。有限通过应表述为“该版本在该输入上通过”；反例应同时展示版本、输入、实际和参考结果。

新增代码或变换必须审核并注册新版本；哈希不同不能继承旧证据。执行失败保留错误并返回无法核验，不能补造输出。工程验收、教学判断可靠性和产品创新性分别为 **PASS／本轮未验证／本轮未验证**。

本轮已结束。停止 F03 扩展，不开发 F04、网页实时 AI 或完整学习工作台，等待用户审核。
'''
    for name, text in [('F03_test_results.md', result), ('F03_next_step_decision.md', decision)]:
        with (ROOT / name).open('x', encoding='utf-8') as file:
            file.write(text)
    print('Generated two short reports from saved results; no execution or model call.')


if __name__ == '__main__':
    main()
