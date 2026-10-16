"""1.6.25 replacements for eight archived 1.5 distribution-contract checks.

These inspect contemporary invariants; they do not replace domain A/B/C regression.
"""
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
PROJECT=yaml.safe_load((ROOT/'gpt-project.yaml').read_text())
TARGETS={'chat','plugin','claude_project','claude_skills','opencode'}

def test_a34_ci_keeps_read_only_and_canonical_builder():
    ci=(ROOT/'.github/workflows/ci.yml').read_text()
    assert 'contents: read' in ci and 'contents: write' not in ci
    assert 'scripts/build_distributions.py' in ci and 'scripts/validate_distributions.py' in ci

def test_a39_release_environment_does_not_override_test_gate():
    release=(ROOT/'.github/workflows/release.yml').read_text()
    assert 'bash scripts/test.sh' in release
    assert release.index('bash scripts/test.sh') < release.index('gh release upload')

def test_b12_five_non_retired_distribution_targets():
    targets=set(PROJECT['build_system']['targets'])-{'project'}
    assert targets==TARGETS
    assert 'custom_gpt' not in targets

def test_c1_mutating_tools_require_approval():
    tools=PROJECT['tools']['tools']
    mutating=[t for t in tools if t.get('mutates_workspace')]
    assert tools and mutating
    assert all(t.get('approval_required') is True for t in mutating)

def test_c2_parity_covers_five_distribution_targets():
    targets=set(PROJECT['build_system']['runtime_targets'])
    assert targets==TARGETS
    assert PROJECT.get('runtime_parity')

def test_c5_canonical_build_and_validation_present():
    for key in ('build_script','validation_script'):
        assert (ROOT/PROJECT['build_system'][key]).is_file()
    assert len(PROJECT['build_system']['targets'])==6

def test_c6_release_permission_and_upload_guard():
    ci=(ROOT/'.github/workflows/ci.yml').read_text()
    release=(ROOT/'.github/workflows/release.yml').read_text()
    assert 'contents: write' not in ci
    assert 'contents: write' in release
    assert 'validate_distributions.py' in release
    assert 'test "${#assets[@]}" -eq 6' in release

def test_c7_release_only_after_regression_and_validation():
    release=(ROOT/'.github/workflows/release.yml').read_text()
    for term in ('scripts/test.sh','lint_gpt_project.py','build_distributions.py','validate_distributions.py','gh release upload'):
        assert term in release
    assert all(release.index(a)<release.index(b) for a,b in zip(('scripts/test.sh','lint_gpt_project.py','build_distributions.py','validate_distributions.py'),('lint_gpt_project.py','build_distributions.py','validate_distributions.py','gh release upload')))
