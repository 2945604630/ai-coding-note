# 保留的本机文件与删除不确定项

这些文件不随 Git 分发，也不是新 Agent 默认阅读材料。未确认价值时保留，不为目录整洁破坏证据。

## 明确保留且不得入 Git

| 路径/类型 | 原因 |
| --- | --- |
| data/ 下 SQLite、学习历史、工件、sandbox 收据 | 当前本机真实状态和学习数据，不改/不删/不上传 |
| backups/（含 github_original_*、teaching_execution_*、原数据库及本轮 documents 原字节备份） | 脱敏前字节、迁移前安全依据及可恢复快照，不能当普通重复备份删除 |
| output/aic-v3-test/ | 含开发数据库、任务和实际执行证据，保留本机 |
| .playwright-cli/ 的 aic-all.json / aic-turns.csv | 本地导出可能含会话内容，不上传 |
| output/playwright/ 的截图与脚本 | 两方向 UI 和异常路径的开发验收依据，私人内容未经发布审查 |
| experiments/**/user_runs、responses、runs、results 等 Git 外原始工件 | 历史调用、输入、失败与冻结依据，保留原字节 |

## 目前不确定能否删除

| 文件/范围 | 未决原因与处理 |
| --- | --- |
| output/p1_evidence_audit.py、output/p1_evidence_audit.json、output/p1_docker_*.json | 正式报告引用本机执行/安全证据，无法确认完全被报告替代，保留 |
| output/teaching_execution_audit.py、output/teaching_execution_audit.json、output/teaching_execution_ABC.json | 历史完整性与真实场景核验，不删除 |
| output/teaching_execution_regression_intermediate_failure.log | 未确认根因的 F02 轮询失败，必须保留 |
| output/prepare_github.py、sanitize_github.py、audit_github.py、check_github_bundle.py 及 github_*.json | 发布脱敏及一致性复验可能仍需，未确认所有脚本已被维护脚本替代 |
| web_lab/v2_validation/、web_lab/demo_validation/ 的本机脚本、JSON、preserved_* | 可能复核旧记录和改写前状态；仅移动已审核文档，其余保留 |
| .playwright-cli/page-*.yml、console-*.log；output/*server*.log | 有些是自动化临时记录，但可能关联验收或仍被运行进程占用，没有逐条认定无价值 |
| Python __pycache__、.pytest_cache（若存在） | 可重建，但 Git 未跟踪；本次未做不可由 Git 恢复的本机删除 |

这些不确定项均继续忽略；本轮没有对它们作无价值判断。

## 冻结/历史路径例外：74 份原件

下面按历史/冻结清单交叉引用保留；其中完整模型原文报告没有公开归档副本。原件保持原路径和原字节，公开归档仅提供阅读与决策追溯。此列表是明确保留依据，不是待自动删除清单。

| 原件路径（仅本机） | 引用清单示例（仅本机/或 Git 静态依赖） |
| --- | --- |
| `docs/research/F02_validation_repair/F02_cli_regression_report.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `docs/research/F02_validation_repair/F02_final_readiness.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `docs/research/F02_validation_repair/F02_guard_failure_analysis.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `docs/research/F02_validation_repair/F02_user_trial_guide.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `docs/research/F02_validation_repair/F02_validation_audit.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `docs/research/codehelper_deep_analysis.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/combination_validation/abc_feasibility_validation.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/combination_validation/architecture_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/combination_validation/final_combination_recommendation.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/combination_validation/innovation_overlap_audit.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/combination_validation/module_synergy_matrix.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/mechanism_prototype_validation/experiment_a_results.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/mechanism_prototype_validation/experiment_b_results.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/mechanism_prototype_validation/experiment_c_results.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/mechanism_prototype_validation/experiment_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/mechanism_prototype_validation/next_stage_decision.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/open_source_candidate_pool.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/project_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/project_opportunities.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/research_summary.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/reuse_strategy.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round4_validation/a_simple_vs_complex.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round4_validation/b_real_ai_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round4_validation/innovation_increment_review.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round4_validation/product_direction_decision.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round5_ai_judge_review/blind_judge_results.md` | `experiments/round5_ai_judge_review/completion_manifest.json`（共 4 处） |
| `docs/research/round5_ai_judge_review/final_innovation_reassessment.md` | `experiments/round5_ai_judge_review/completion_manifest.json`（共 4 处） |
| `docs/research/round5_ai_judge_review/judge_disagreements.md` | `experiments/round5_ai_judge_review/completion_manifest.json`（共 4 处） |
| `docs/research/round5_ai_judge_review/previous_scores_audit.md` | `experiments/round5_ai_judge_review/completion_manifest.json`（共 4 处） |
| `docs/research/round5_ai_judge_review/s0_s1_s2_reassessment.md` | `experiments/round5_ai_judge_review/completion_manifest.json`（共 4 处） |
| `docs/research/round5_real_ai_teaching/final_project_go_no_go.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round5_real_ai_teaching/real_ai_teaching_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round5_real_ai_teaching/teaching_question_quality.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round5_real_ai_teaching/user_value_validation.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 3 处） |
| `docs/research/round5_ui_model_validation/automated_codex_20261009T094819533718Z/automated_execution_report.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 4 处） |
| `docs/research/round5_ui_model_validation/automated_codex_20261009T094819533718Z/final_innovation_decision.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 4 处） |
| `docs/research/round5_ui_model_validation/automated_codex_20261009T094819533718Z/real_model_raw_results.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 4 处） |
| `docs/research/round5_ui_model_validation/automated_codex_20261009T094819533718Z/s0_s1_s2_comparison.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 4 处） |
| `docs/research/round5_ui_model_validation/automated_codex_20261009T094819533718Z/teaching_question_review.md` | `experiments/feature_validation/F01_response_adaptation/historical_manifest.json`（共 4 处） |
| `experiments/feature_validation/F01_F05_integration/F01_F05_integration_results.md` | `experiments/feature_validation/F01_F05_integration/delivery_manifest.json`（共 1 处） |
| `experiments/feature_validation/F01_F05_integration/F01_F05_product_assessment.md` | `experiments/feature_validation/F01_F05_integration/delivery_manifest.json`（共 1 处） |
| `experiments/feature_validation/F01_response_adaptation/F01_accuracy_report.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 4 处） |
| `experiments/feature_validation/F01_response_adaptation/F01_failure_cases.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 4 处） |
| `experiments/feature_validation/F01_response_adaptation/F01_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 4 处） |
| `experiments/feature_validation/F01_response_adaptation/F01_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 4 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/F01_failure_cases.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/F01_final_acceptance.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/S0plus_S1_comparison.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/execution_audit.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/individual_assessments.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/final_acceptance/reports/user_acceptance_status.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/F01_phase2_accuracy_report.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/F01_phase2_failure_cases.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/F01_phase2_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/F01_phase2_test_plan.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/F01_phase2_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/auxiliary_review_notes.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F01_response_adaptation/phase2/real_user_acceptance.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 3 处） |
| `experiments/feature_validation/F02_dynamic_questioning/F02_accuracy_report.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/F02_failure_cases.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/F02_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/F02_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/auxiliary_review_audit.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/reports_initial/F02_accuracy_report.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/reports_initial/F02_failure_cases.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/reports_initial/F02_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/reports_initial/F02_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F02_dynamic_questioning/reports_initial/auxiliary_review_audit.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 1 处） |
| `experiments/feature_validation/F03_evidence_verification/F03_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F03_evidence_verification/F03_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F04_self_modification/F04_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F04_self_modification/F04_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F05_independent_assessment/F05_next_step_decision.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
| `experiments/feature_validation/F05_independent_assessment/F05_test_results.md` | `experiments/feature_validation/F01_F05_integration/historical_manifest.json`（共 2 处） |
