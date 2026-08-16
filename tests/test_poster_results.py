import pytest
from poster_results import classify_status, classify_guided, aggregate_llm, performance_success_flags, prompt_token_cost

@pytest.mark.parametrize("status,outcome", [
 ("candidate_compile_failed","compile_or_assemble_failure"), ("candidate_benchmark_failed","correctness_or_benchmark_failure"),
 ("context_insufficient","context_insufficient"), ("response_truncated","response_truncated")])
def test_failure_classification(status,outcome): assert classify_status(status)==outcome
def test_no_change_is_valid(): assert classify_status("no_change")=="valid"
def test_guided_fallback_is_not_valid(): assert classify_guided({"best_is_baseline":True,"iterations":[{"type":"optimization","success":False,"status":"compile_failed"}]})[:2]==("compile_or_assemble_failure",1)
def test_guided_one_completed_pass_is_valid(): assert classify_guided({"completed_optimization_passes":1,"iterations":[{"success":True}]})==("valid",1,1)
def test_guided_multiple_completed_passes_are_valid(): assert classify_guided({"completed_optimization_passes":3,"iterations":[{"success":True}]})==("valid",1,3)
def test_guided_iteration_success_without_completed_pass_is_invalid():
    outcome,_,_=classify_guided({"completed_optimization_passes":0,"stopped_reason":"repair_failed_pass_1","iterations":[{"success":True},{"success":False,"compile_result":{"returncode":1}}]})
    assert outcome=="compile_or_assemble_failure"
def test_guided_zero_pass_truncation():
    assert classify_guided({"completed_optimization_passes":0,"stopped_reason":"optimization_failed_pass_1","iterations":[{"success":False,"metadata":{"error":"response_truncated"}}]})[0]=="response_truncated"
def test_guided_zero_pass_fast_fallback_is_not_performance_success():
    outcome,_,_=classify_guided({"completed_optimization_passes":0,"stopped_reason":"repair_failed_pass_1","iterations":[{"success":True}]})
    assert outcome!="valid" and performance_success_flags(False,500)==(False,False)
def test_speedup_and_threshold_semantics():
    from poster_results import speedup_percent, is_meaningful_improvement
    speedup=speedup_percent(102,100); assert speedup==pytest.approx(2); assert not is_meaningful_improvement(speedup); assert is_meaningful_improvement(speedup_percent(103,100))
@pytest.mark.parametrize("speedup,expected",[(1.99,False),(2.00,False),(2.01,True)])
def test_performance_threshold(speedup,expected): assert performance_success_flags(True,speedup)==(expected,expected)
def test_invalid_fast_fallback_is_never_success(): assert performance_success_flags(False,500)==(False,False)
def test_guided_invalid_fast_fallback_is_never_success():
    outcome,_,_=classify_guided({"best_is_baseline":True,"iterations":[{"success":False,"metadata":{"error":"response_truncated"}}]})
    assert outcome!="valid" and performance_success_flags(False,50)==(False,False)
def test_prompt_cost_naive_single_request(): assert prompt_token_cost({"llm_result":{"prompt_tokens":10}})==(10,"actual")
def test_prompt_cost_naive_with_repair(): assert prompt_token_cost({"llm_result":{"prompt_tokens":10},"repair_result":{"prompt_tokens":7}})==(17,"actual")
def test_prompt_cost_guided_multiple_and_failed_iterations():
    data={"iterations":[{"success":True,"metadata":{"llm_result":{"prompt_tokens":10}}},{"success":False,"metadata":{"llm_result":{"prompt_tokens":8}}}]}
    assert prompt_token_cost(data,True)==(18,"actual")
def test_prompt_cost_ir_actual_wins_over_estimate(): assert prompt_token_cost({"llm_result":{"prompt_tokens":9},"estimated_prompt_tokens":99})==(9,"actual")
def test_prompt_cost_context_rejection_uses_estimate(): assert prompt_token_cost({"token_budget":{"prompt_tokens":120}})==(120,"estimated")
def test_context_percentage_can_exceed_100(): assert 100*120/100==120
def test_speedup_ratio_and_noise_boundaries():
    from poster_results import speedup_ratio
    assert speedup_ratio(100,100)==pytest.approx(1.0)
    assert speedup_ratio(98,100)==pytest.approx(.98)
    assert speedup_ratio(102,100)==pytest.approx(1.02)
    assert performance_success_flags(True,1.99)==(False,False)
    assert performance_success_flags(False,500)==(False,False)
@pytest.mark.parametrize("value,label",[(2.4,"2.4×"),(170,"170×"),(7800,"7.8k×"),(4_600_000,"4.6M×")])
def test_multiplier_format(value,label):
    from plot_results import format_multiplier
    assert format_multiplier(value)==label
def test_prompt_coverage_metadata():
    from plot_results import prompt_coverage
    rows=[{"technique":t,"total_prompt_tokens_processed":1} for t in ["naive_cpp","guided_cpp","full_ir","extracted_ir"]]
    rows.append({"technique":"guided_cpp","total_prompt_tokens_processed":None})
    assert prompt_coverage(rows)["guided_cpp"]==(1,2)

def _raw(path, prompt=11, completion=7, total=18, finish="length"):
    import json
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"usage":{"prompt_tokens":prompt,"completion_tokens":completion,"total_tokens":total},"choices":[{"finish_reason":finish}]}))

def test_guided_raw_response_fallback_recovers_usage(tmp_path):
    from poster_results import aggregate_llm, guided_llm_calls
    _raw(tmp_path/"artifacts"/"iteration-01"/"optimization_01_response.json")
    data={"iterations":[{"iteration":1,"metadata":{"raw_response_file":"optimization_01_response.json"}}]}
    assert aggregate_llm(data,True,tmp_path)[:3]==(11,7,18)
    calls,stats=guided_llm_calls(data,tmp_path); assert calls[0]["finish_reason"]=="length" and stats["raw_recovered_calls"]==1

def test_guided_raw_is_authoritative_without_double_counting(tmp_path):
    from poster_results import aggregate_llm, guided_llm_calls
    _raw(tmp_path/"optimization_01_response.json",prompt=999)
    data={"iterations":[{"iteration":1,"metadata":{"raw_response_file":"optimization_01_response.json","llm_result":{"prompt_tokens":5,"completion_tokens":2,"total_tokens":7,"finish_reason":"stop"}}}]}
    assert aggregate_llm(data,True,tmp_path)[:3]==(999,7,18)
    _,stats=guided_llm_calls(data,tmp_path); assert stats["structured_calls"]==0 and stats["raw_recovered_calls"]==1

def test_guided_multiple_structured_and_raw_calls_are_summed(tmp_path):
    from poster_results import aggregate_llm
    _raw(tmp_path/"iteration-02"/"optimization_02_response.json",prompt=13,completion=3,total=16)
    data={"iterations":[{"iteration":1,"metadata":{"llm_result":{"prompt_tokens":5,"completion_tokens":2,"total_tokens":7}}},{"iteration":2,"metadata":{"raw_response_file":"optimization_02_response.json"}}]}
    # Once an authoritative raw inventory exists, incomplete summary records
    # are not mixed in (which could count their represented call twice).
    assert aggregate_llm(data,True,tmp_path)[:3]==(13,3,16)

@pytest.mark.parametrize("kind",["missing","malformed"])
def test_guided_bad_raw_response_warns_without_crashing(tmp_path,kind):
    from poster_results import aggregate_llm
    if kind=="malformed": (tmp_path/"bad.json").write_text("{bad")
    with pytest.warns(UserWarning,match="guided token recovery failed"):
        assert aggregate_llm({"iterations":[{"iteration":1,"metadata":{"raw_response_file":"bad.json"}}]},True,tmp_path)[:3]==(None,None,None)

def test_recovered_guided_tokens_are_actual(tmp_path):
    _raw(tmp_path/"response.json")
    data={"iterations":[{"iteration":1,"metadata":{"raw_response_file":"response.json"}}],"estimated_prompt_tokens":999}
    assert prompt_token_cost(data,True,tmp_path)==(11,"actual")

def test_guided_discovers_omitted_optimization_and_repairs(tmp_path):
    from poster_results import aggregate_llm, guided_llm_calls
    _raw(tmp_path/"iteration-01"/"optimization_01_response.json",prompt=10)
    _raw(tmp_path/"iteration-02"/"optimization_02_response.json",prompt=20)
    _raw(tmp_path/"iteration-02"/"repair_02_response.json",prompt=30)
    data={"iterations":[{"iteration":1,"metadata":{"raw_response_file":"optimization_01_response.json"}}]}
    assert aggregate_llm(data,True,tmp_path)[0]==60
    _,stats=guided_llm_calls(data,tmp_path); assert stats["discovered_raw_files"]==3 and stats["unique_raw_files"]==3

def test_guided_duplicate_summary_references_count_file_once(tmp_path):
    from poster_results import aggregate_llm
    _raw(tmp_path/"iteration-01"/"optimization_01_response.json",prompt=12)
    data={"iterations":[{"iteration":1,"metadata":{"raw_response_file":"optimization_01_response.json"}},
                        {"iteration":1,"metadata":{"raw_response_file":"optimization_01_response.json"}}]}
    assert aggregate_llm(data,True,tmp_path)[0]==12

def test_distinct_raw_calls_with_identical_usage_both_count(tmp_path):
    from poster_results import aggregate_llm
    _raw(tmp_path/"iteration-01"/"optimization_01_response.json",prompt=12)
    _raw(tmp_path/"iteration-02"/"optimization_02_response.json",prompt=12)
    assert aggregate_llm({},True,tmp_path)[0]==24

def test_raw_response_without_usage_warns_and_is_unavailable(tmp_path):
    import json
    from poster_results import guided_llm_calls
    p=tmp_path/"optimization_01_response.json"; p.write_text(json.dumps({"choices":[]}))
    with pytest.warns(UserWarning,match="no usage object"):
        calls,stats=guided_llm_calls({},tmp_path)
    assert calls==[] and stats["unavailable_calls"]==1

@pytest.mark.parametrize("model,benchmark,expected",[
    ("devstral-small-2-24b-q4km","format_list",85387),
    ("ministral-3-14b-instruct-q4km","count_matches",79962),
    ("ministral-3-14b-instruct-q4km","format_list",83884),
    ("ministral-3-14b-instruct-q4km","repeated_sort",90200),
    ("qwen3-14b-q4km","count_matches",67447),
    ("qwen3-14b-q4km","repeated_sort",56324),
])
def test_current_guided_raw_totals(model,benchmark,expected):
    from pathlib import Path
    from poster_results import aggregate_llm
    task=Path(__file__).resolve().parents[1]/"results"/"guided-cpp"/"20260807_full_run-guided"/model/f"{benchmark}_cpp"
    if not task.is_dir(): pytest.skip("current full-run fixture is unavailable")
    assert aggregate_llm({},True,task)[0]==expected

def test_prompt_provenance_marker_styles_do_not_change_values():
    from plot_results import provenance_marker_style
    value=12345
    actual=provenance_marker_style("actual","red")
    estimated=provenance_marker_style("estimated","red")
    assert actual["facecolors"]=="red"
    assert estimated["facecolors"]=="none"
    assert value==12345
def test_missing_cost_fields(): assert aggregate_llm({})==(None,None,None,None)
def test_duplicate_detection(tmp_path):
    from poster_results import load_task_summaries
    import json
    for parent in ("a","b"):
      p=tmp_path/parent/"fibonacci_cpp"; p.mkdir(parents=True); (p/"summary.json").write_text(json.dumps({"model_id":"same","benchmark_name":"fibonacci"}))
    rows,duplicates=load_task_summaries(tmp_path); assert len(rows)==2 and duplicates==[("same","fibonacci")]
