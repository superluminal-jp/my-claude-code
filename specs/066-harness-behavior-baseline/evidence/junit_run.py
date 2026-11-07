"""Run tests/harness-eval's unit tests and write JUnit XML whose test names
carry the acceptance criterion each test shows (spec 066 evidence).

    python3 -B specs/066-harness-behavior-baseline/evidence/junit_run.py OUT.xml
"""
import subprocess
import sys
import unittest
from pathlib import Path
from xml.sax.saxutils import quoteattr

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests/harness-eval"))

# test method -> acceptance criterion; untagged tests are implementation details.
TAGS = {
    "test_a_consistent_map_and_suite_have_no_violation": "R-SPEC-A1",
    "test_a_harness_component_missing_from_the_map_is_reported": "R1-A1",
    "test_a_map_component_that_does_not_exist_is_reported": "R1-A1",
    "test_a_component_that_owns_no_stage_is_reported": "R1-A1",
    "test_a_stage_with_both_owners_and_gap_is_reported": "R1-A1",
    "test_a_stage_with_neither_owners_nor_gap_is_reported": "R1-A1",
    "test_a_basis_quote_absent_from_its_file_is_reported": "R1-A1",
    "test_declared_children_must_match_the_child_skills_section": "R1-A1",
    "test_an_unclassified_settings_key_is_reported": "R5-A1",
    "test_an_observable_stage_without_a_scenario_is_reported": "R-SPEC-A1",
    "test_an_unobservable_stage_needs_no_scenario": "R-SPEC-A1",
    "test_an_owned_stage_covered_only_by_observation_is_reported": "R-SPEC-A1",
    "test_a_gap_stage_covered_only_by_expectation_is_reported": "R-SPEC-A1",
    "test_a_scenario_that_names_an_unknown_stage_is_reported": "R-SPEC-A1",
    "test_expecting_a_group_member_requires_asserting_the_others_unused": "R-SPEC-A1",
    "test_children_of_an_expected_parent_are_exempt_from_the_group_rule": "R-SPEC-A1",
    "test_a_stage_that_requires_an_unused_skill_grader_is_enforced": "R-SPEC-A1",
    "test_fewer_than_three_compound_scenarios_is_reported": "R2-A1",
    "test_three_compound_scenarios_satisfy_the_rule": "R2-A1",
    "test_a_prompt_without_japanese_is_reported": "R2-A1",
    "test_a_basis_from_an_unrelated_component_is_reported": "R2-A1",
    "test_a_boundary_group_basis_may_justify_an_unused_member": "R2-A1",
    "test_a_probe_basis_must_be_an_always_on_file": "R2-A1",
    "test_a_match_example_the_pattern_misses_is_reported": "R2-A1",
    "test_a_no_match_example_the_pattern_matches_is_reported": "R2-A1",
    "test_a_regex_grader_without_examples_is_reported": "R2-A1",
    "test_a_missing_fixture_is_reported": "R2-A1",
    "test_matches_the_bare_and_the_namespaced_name": "R2-A1",
    "test_does_not_match_another_skill_that_contains_the_name": "R2-A1",
    "test_the_guard_stops_a_fixture_in_a_non_empty_directory": "R4-A1",
    "test_refs_resolve_to_commit_shas": "R3-A1",
    "test_a_working_tree_only_change_is_not_built": "R3-A1",
    "test_the_command_sets_model_runs_and_output_directory": "R3-A1",
    "test_the_record_names_both_commits_and_the_model": "R3-A1",
    "test_the_result_directory_name_contains_both_short_commits": "R3-A1",
    "test_each_always_on_file_is_injected_verbatim_by_its_own_session_start_hook": "R5-A1",
    "test_every_injected_chunk_is_under_the_hook_output_cap": "R5-A1",
    "test_an_always_on_file_over_the_cap_stops_the_build": "R5-A1",
    "test_an_import_line_in_the_apex_stops_the_build": "R5-A1",
    "test_a_rule_with_paths_frontmatter_stops_the_build": "R5-A1",
    "test_skills_are_copied_byte_for_byte": "R5-A1",
    "test_a_build_directory_inside_the_repository_is_refused": "R4-A1",
    "test_a_build_directory_inside_the_claude_config_is_refused": "R4-A1",
    "test_the_command_always_has_no_publish_and_a_cost_ceiling": "R4-A1",
    "test_the_command_grants_only_bash": "R4-A1",
    "test_the_command_never_reaches_real_servers_or_the_network": "R4-A1",
    "test_running_without_a_cost_ceiling_fails_before_any_work": "R4-A1",
    "test_a_non_positive_cost_ceiling_is_refused": "R4-A1",
    "test_reports_the_score_difference_per_case": "R6-A1",
    "test_flags_only_differences_at_or_above_the_threshold": "R6-A1",
    "test_lists_cases_present_on_only_one_side": "R6-A1",
    "test_an_allowlisted_fixture_has_no_violation": "R4-A1",
    "test_a_command_outside_the_allowlist_is_reported": "R4-A1",
    "test_a_git_subcommand_outside_the_allowlist_is_reported": "R4-A1",
    "test_command_substitution_and_pipes_are_reported": "R4-A1",
    "test_a_redirect_outside_the_workspace_is_reported": "R4-A1",
    "test_the_guard_must_come_before_any_other_command": "R4-A1",
    "test_the_command_grants_bash_and_nothing_else": "R4-A1",
    "test_the_map_must_flag_a_stage_for_over_application": "R-SPEC-A1",
    "test_a_rule_in_a_subdirectory_is_a_component": "R1-A1",
    "test_the_probe_must_check_every_always_on_file": "R2-A1",
    "test_a_tool_order_grader_is_checked_and_rendered": "R2-A1",
    "test_a_tool_order_side_whose_example_fails_is_reported": "R2-A1",
    "test_two_different_commits_build_harness_and_suite_separately": "R3-A1",
    "test_every_session_start_hook_runs_cat_and_prints_the_file_verbatim": "R5-A1",
    "test_a_run_builds_validates_evaluates_and_records_both_commits": "R-MEASURE-A1",
    "test_comparing_results_of_different_suites_is_refused": "R6-A1",
    "test_comparing_results_of_different_models_is_refused": "R6-A1",
    "test_a_partial_result_is_reported": "R6-A1",
    "test_matching_results_have_no_problem": "R6-A1",
    "test_compare_exits_non_zero_on_a_mismatch": "R6-A1",
    "test_a_skill_marked_out_of_the_eval_is_not_built": "R5-A1",
    "test_expecting_a_skill_left_out_of_the_eval_is_reported": "R2-A1",
    "test_leaving_a_skill_out_needs_a_reason": "R5-A1",
    "test_a_skill_whose_frontmatter_declares_hooks_stops_the_build": "R4-A1",
    "test_git_paths_are_refused_in_any_letter_case": "R4-A1",
    "test_every_git_command_in_the_scaffold_disables_hooks_and_templates": "R4-A1",
    "test_a_scenario_granting_a_tool_beyond_read_only_is_reported": "R4-A1",
    "test_a_skill_that_carries_its_own_hooks_stops_the_build": "R4-A1",
    "test_a_result_without_metadata_is_refused": "R6-A1",
    "test_metadata_missing_a_compared_key_is_refused": "R6-A1",
    "test_a_run_result_compares_cleanly_with_itself": "R6-A1",
    "test_a_different_run_count_is_a_problem": "R6-A1",
    "test_a_different_claude_version_is_a_problem": "R6-A1",
    "test_a_script_fixture_is_not_accepted": "R4-A1",
    "test_invalid_fixture_data_is_reported_by_check": "R4-A1",
    "test_an_unknown_key_is_reported": "R4-A1",
    "test_content_without_a_final_newline_is_reported": "R4-A1",
    "test_unsafe_paths_are_reported": "R4-A1",
    "test_the_generated_script_starts_with_the_guard_and_passes_the_allowlist": "R4-A1",
    "test_the_generated_script_disables_git_hooks_on_every_git_write": "R4-A1",
    "test_shell_syntax_in_file_content_is_written_not_run": "R4-A1",
    "test_the_generated_script_writes_files_commits_then_writes_the_rest": "R4-A1",
    "test_valid_data_has_no_violation": "R4-A1",
    "test_the_built_scaffold_is_generated_from_the_fixture_data": "R4-A1",
    # Round 5 (assurance review of 112db91).
    "test_a_suite_that_maps_a_component_the_older_harness_lacks_still_builds": "R3-A1",
    "test_a_quote_the_older_harness_lacks_is_recorded_not_fatal": "R3-A1",
    "test_the_same_commit_for_both_has_no_drift": "R3-A1",
    "test_a_harness_component_the_suite_does_not_map_stops_the_build": "R3-A1",
    "test_a_suite_inconsistent_with_its_own_commit_stops_a_cross_commit_build": "R3-A1",
    "test_the_drift_and_the_probe_cases_are_recorded_in_the_run_metadata": "R3-A1",
    "test_a_run_whose_cases_match_the_suite_succeeds": "R3-A1",
    "test_a_run_whose_result_has_a_case_outside_the_suite_fails": "R3-A1",
    "test_a_complete_run_that_lacks_a_suite_case_fails": "R3-A1",
    "test_a_skills_own_eval_suite_and_scaffold_are_not_built": "R4-A1",
    "test_a_skill_plugin_json_that_declares_hooks_stops_the_build": "R4-A1",
    "test_a_skill_plugin_json_without_hooks_builds": "R4-A1",
    "test_the_skill_files_outside_evals_are_still_copied": "R5-A1",
    "test_a_result_whose_probe_did_not_pass_in_every_run_is_refused": "R6-A1",
    "test_a_result_without_its_probe_case_is_refused": "R6-A1",
    "test_metadata_without_the_probe_cases_is_refused": "R6-A1",
    "test_a_suite_without_a_probe_is_refused": "R6-A1",
    "test_passing_probes_on_both_sides_are_no_problem": "R6-A1",
    "test_compare_refuses_a_result_whose_run_found_unexpected_cases": "R6-A1",
    "test_the_shallowest_aggregate_result_is_read": "R6-A1",
    "test_two_aggregate_results_at_the_same_depth_are_refused": "R6-A1",
    "test_compare_exits_2_on_an_ambiguous_result_directory": "R6-A1",
    # Round 6 (assurance review of 6897bff).
    "test_two_harness_commits_run_on_one_suite_and_compare_cleanly": "R-MEASURE-A1",
    "test_a_probe_grader_whose_phrase_the_older_harness_lacks_is_left_out_and_recorded": "R3-A1",
    "test_the_same_commit_leaves_no_probe_grader_out": "R3-A1",
    "test_a_build_where_no_probe_reach_grader_can_pass_stops": "R3-A1",
    "test_compare_notes_the_probe_graders_left_out_without_refusing": "R6-A1",
    "test_the_run_record_lists_the_built_skills": "R3-A1",
    "test_a_harness_settings_key_the_map_does_not_classify_stops_the_build": "R5-A1",
    "test_the_results_directory_is_ignored_by_git": "R4-A1",
    # Round 7 (assurance review of 0ac8e15).
    "test_an_agent_file_is_a_component_that_the_map_must_name": "R1-A1",
    "test_a_command_file_is_a_component_that_the_map_must_name": "R1-A1",
    "test_a_harness_with_a_mapped_agent_stops_the_build": "R5-A1",
    "test_a_harness_with_a_mapped_command_stops_the_build": "R5-A1",
    "test_a_non_reach_probe_grader_is_kept_when_its_phrase_is_gone": "R3-A1",
    "test_compare_refuses_a_complete_result_whose_run_missed_suite_cases": "R6-A1",
    "test_a_partial_run_that_lacks_cases_records_them_and_succeeds": "R3-A1",
    # Round 8 (assurance review of 4e6b18e).
    "test_fixture_paths_that_claude_code_reads_as_configuration_are_refused": "R4-A1",
    "test_ordinary_fixture_paths_are_still_accepted": "R4-A1",
    "test_a_case_yaml_elsewhere_in_a_skill_stops_the_build": "R4-A1",
    "test_a_build_directory_outside_the_temporary_directory_is_refused": "R4-A1",
    "test_a_scenario_without_graders_is_reported": "R2-A1",
    "test_a_non_probe_scenario_without_stages_is_reported": "R2-A1",
    "test_a_grader_without_basis_is_reported": "R2-A1",
    "test_a_basis_with_an_empty_quote_is_reported": "R2-A1",
    "test_a_stage_without_basis_is_reported": "R1-A1",
    "test_a_boundary_group_without_basis_is_reported": "R1-A1",
    "test_a_boundary_group_quote_absent_from_its_file_is_reported": "R1-A1",
    "test_a_boundary_group_with_one_member_is_reported": "R1-A1",
    "test_a_boundary_group_member_outside_the_map_is_reported": "R1-A1",
    "test_a_run_records_result_files_that_mention_the_real_home_directory": "R4-A1",
    "test_a_run_whose_results_do_not_mention_the_home_directory_records_none": "R4-A1",
    # What the first real run (24 cases x 1 at 2822abe) showed.
    "test_a_case_whose_run_ended_on_an_error_is_listed": "R6-A1",
    "test_compare_refuses_a_result_with_runs_that_ended_on_an_error": "R6-A1",
    "test_a_run_records_the_cases_whose_runs_ended_on_an_error_and_fails": "R3-A1",
}


class Recorder(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.cases = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.cases.append((test, None))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.cases.append((test, ("failure", self._exc_info_to_string(err, test))))

    def addError(self, test, err):
        super().addError(test, err)
        self.cases.append((test, ("error", self._exc_info_to_string(err, test))))


def main(out):
    suite = unittest.defaultTestLoader.discover(str(REPO / "tests/harness-eval"))
    result = unittest.TextTestRunner(resultclass=Recorder, verbosity=2).run(suite)
    names = {t._testMethodName for t, _ in result.cases}
    unknown = sorted(set(TAGS) - names)
    if unknown:
        print("tags name tests that do not exist:", unknown, file=sys.stderr)
        return 2
    rows = []
    for test, outcome in result.cases:
        method, cls = test._testMethodName, type(test).__name__
        tag = TAGS.get(method)
        name = f"{method}[{tag}]" if tag else method
        body = "" if outcome is None else f"<{outcome[0]} message=\"failed\">{quoteattr(outcome[1])[1:-1]}</{outcome[0]}>"
        rows.append(f'  <testcase classname={quoteattr(cls)} name={quoteattr(name)}>{body}</testcase>')
    failures = sum(1 for _, o in result.cases if o)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    # The records under specs/066 change after the commit they describe; this
    # script, which maps tests to criteria, must not.
    dirty = "".join(
        subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", *spec],
                       capture_output=True, text=True).stdout.strip()
        for spec in ((".", ":!specs/066-harness-behavior-baseline"), (str(Path(__file__).resolve()),)))
    print(f"commit: {head}\ncode paths clean: {not dirty}")
    props = (f'  <properties><property name="commit" value={quoteattr(head)}/>'
             f'<property name="code_paths_clean" value="{str(not dirty).lower()}"/></properties>')
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<testsuite name="harness-eval" tests="{len(rows)}" '
           f'failures="{failures}">\n' + props + "\n" + "\n".join(rows) + "\n</testsuite>\n")
    Path(out).write_text(xml, encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
