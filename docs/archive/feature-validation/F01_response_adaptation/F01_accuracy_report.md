> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F01 分项准确性与不确定性记录

本轮8个预设模拟回答、2道既有题，没有真实学生。语义判定是研究Agent的带原文依据作者初审，全部needs_human_review，独立人类复核0；机械事实核验另列。没有综合准确率或学习提升结论。

S1/S2均为官方Codex CLI独立新exec，gpt-6.1-sol/high，同一1200秒上限及输出格式，两组都禁止完整修复；精确后台快照未知。第一份原始回答保留，无按质量重采样。公开输入一致，旧评分、参考标签、其他回答没有提供给生成会话。工具禁用及本地渲染探针不提供OS deny-read或服务端上下文认证；不能称完全盲测。

“correct”和“reasonable”是作者初审标签，不是独立证实教学准确率。集合匹配只说明分支可接受，不替代语义审查。分母固定8；未取得/未审另列。

## S0

```json
{
  "scenario_denominator": 8,
  "output_status": {
    "complete": 8,
    "failure": 0,
    "not_attempted": 0
  },
  "allowed_action_member": {
    "True": 8,
    "False": 0,
    "None": 0
  },
  "author_metrics": {
    "interpretation": {
      "correct": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "action_quality": {
      "reasonable": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "knowledge_overreach": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repeat_answered_question": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "program_contradiction": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "natural_language_illegal_test": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repair_disclosure": {
      "0": 7,
      "1": 1,
      "2": 0,
      "3": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "teaching_ambiguity": {
      "absent": 7,
      "present": 1,
      "uncertain": 0,
      "unreviewed": 0
    }
  },
  "structured_evidence_quote_valid": 8,
  "execution_requests": 3,
  "legal_execution_requests": 3,
  "illegal_execution_requests": 0,
  "predictions": {
    "actual_prediction_correct": {
      "correct": 3,
      "error": 0,
      "denominator": 3,
      "unpredicted_or_ineligible": 0
    },
    "expected_prediction_correct": {
      "correct": 3,
      "error": 0,
      "denominator": 3,
      "unpredicted_or_ineligible": 0
    }
  },
  "actual_observed_student_steps": null
}
```

## S1

```json
{
  "scenario_denominator": 8,
  "output_status": {
    "complete": 8,
    "failure": 0,
    "not_attempted": 0
  },
  "allowed_action_member": {
    "True": 8,
    "False": 0,
    "None": 0
  },
  "author_metrics": {
    "interpretation": {
      "correct": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "action_quality": {
      "reasonable": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "knowledge_overreach": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repeat_answered_question": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "program_contradiction": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "natural_language_illegal_test": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repair_disclosure": {
      "0": 4,
      "1": 4,
      "2": 0,
      "3": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "teaching_ambiguity": {
      "absent": 7,
      "present": 1,
      "uncertain": 0,
      "unreviewed": 0
    }
  },
  "structured_evidence_quote_valid": 8,
  "execution_requests": 2,
  "legal_execution_requests": 2,
  "illegal_execution_requests": 0,
  "predictions": {
    "actual_prediction_correct": {
      "correct": 2,
      "error": 0,
      "denominator": 2,
      "unpredicted_or_ineligible": 0
    },
    "expected_prediction_correct": {
      "correct": 2,
      "error": 0,
      "denominator": 2,
      "unpredicted_or_ineligible": 0
    }
  },
  "latency": {
    "count": 8,
    "sum_seconds": 1102.349,
    "mean_seconds": 137.794,
    "maximum_seconds": 149.4471
  },
  "token_usage": {
    "input_tokens": 71218,
    "cached_input_tokens": 0,
    "cache_write_input_tokens": 0,
    "output_tokens": 4575,
    "reasoning_output_tokens": 2449
  },
  "usage_missing": 0,
  "actual_observed_student_steps": null
}
```

## S2

```json
{
  "scenario_denominator": 8,
  "output_status": {
    "complete": 8,
    "failure": 0,
    "not_attempted": 0
  },
  "allowed_action_member": {
    "True": 8,
    "False": 0,
    "None": 0
  },
  "author_metrics": {
    "interpretation": {
      "correct": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "action_quality": {
      "reasonable": 8,
      "error": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "knowledge_overreach": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repeat_answered_question": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "program_contradiction": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "natural_language_illegal_test": {
      "absent": 8,
      "present": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "repair_disclosure": {
      "0": 4,
      "1": 4,
      "2": 0,
      "3": 0,
      "uncertain": 0,
      "unreviewed": 0
    },
    "teaching_ambiguity": {
      "absent": 5,
      "present": 3,
      "uncertain": 0,
      "unreviewed": 0
    }
  },
  "structured_evidence_quote_valid": 8,
  "execution_requests": 1,
  "legal_execution_requests": 1,
  "illegal_execution_requests": 0,
  "predictions": {
    "actual_prediction_correct": {
      "correct": 1,
      "error": 0,
      "denominator": 1,
      "unpredicted_or_ineligible": 0
    },
    "expected_prediction_correct": {
      "correct": 1,
      "error": 0,
      "denominator": 1,
      "unpredicted_or_ineligible": 0
    }
  },
  "latency": {
    "count": 8,
    "sum_seconds": 1111.346,
    "mean_seconds": 138.918,
    "maximum_seconds": 148.888
  },
  "token_usage": {
    "input_tokens": 71788,
    "cached_input_tokens": 20736,
    "cache_write_input_tokens": 0,
    "output_tokens": 5256,
    "reasoning_output_tokens": 3003
  },
  "usage_missing": 0,
  "actual_observed_student_steps": null
}
```

## 可由程序确认的范围

原提交输入/输出、合法性、oracle和明确数值预测可以确认。自然语言原因、当前回答含义、教学负担与披露仍需人类。没有执行模型给出的新源码。

完整性核验：

```json
{
  "historical_files_unchanged": 1034,
  "frozen_files_unchanged": 43,
  "distinct_formal_thread_ids": 16,
  "formal_CLI_successes": 16,
  "nonempty_outputs": 16,
  "model_tool_calls": 0,
  "formal_thread_ids_disjoint_from_prior_teachers_and_judges": true,
  "independent_human_reviewers": 0,
  "real_learners": 0,
  "full_OS_isolation": false
}
```
