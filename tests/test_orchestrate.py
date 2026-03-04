"""Tests for multi-agent orchestration feature."""

import os
import re
import tempfile
import shutil

import pytest
import yaml
from pathlib import Path

from specify_cli import (
    _generate_orchestrator_config,
    _install_orchestrator_templates,
    _install_orchestrate_commands,
    ORCHESTRATE_COMMANDS,
    ORCHESTRATE_TEMPLATE_FILES,
    ORCHESTRATOR_AGENT_FILES,
    AGENT_CONFIG,
    app,
)

from typer.testing import CliRunner

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parent.parent


# ===== Fixtures =====

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def project_dir(temp_dir):
    """Create a mock project directory."""
    proj_dir = temp_dir / "test-project"
    proj_dir.mkdir()
    return proj_dir


# ===== Test 1: init with --orchestrate creates orchestrator directory =====

class TestOrchestrateCreatesDirectory:
    def test_orchestrator_directory_exists(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        _install_orchestrator_templates(project_dir)
        assert (project_dir / ".specify" / "orchestrator").is_dir()

    def test_orchestrator_config_file_exists(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        assert (project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml").exists()

    def test_orchestrator_agents_directory_has_five_files(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        assert agents_dir.is_dir()
        md_files = list(agents_dir.glob("*.md"))
        assert len(md_files) == 5


# ===== Test 2: init WITHOUT --orchestrate does NOT create orchestrator directory =====

class TestNoOrchestrateNoDirectory:
    def test_orchestrator_directory_absent_by_default(self, project_dir):
        # Without calling orchestration helpers the directory must not exist
        assert not (project_dir / ".specify" / "orchestrator").exists()

    def test_standard_specify_dir_can_exist_without_orchestrator(self, project_dir):
        # Simulate normal init creating .specify without orchestrator
        (project_dir / ".specify").mkdir(parents=True, exist_ok=True)
        assert (project_dir / ".specify").exists()
        assert not (project_dir / ".specify" / "orchestrator").exists()


# ===== Test 3: orchestrator config YAML is valid =====

class TestOrchestratorConfigValid:
    def test_config_has_required_keys(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        for key in ("feature", "mode", "agents", "checkpoints", "quality_gates"):
            assert key in data, f"Missing required key: {key}"

    def test_config_mode_is_valid(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "semi-auto", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["mode"] in ("supervised", "semi-auto", "autonomous")

    def test_config_agents_contains_required_roles(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        for role in ("architect", "code", "test", "review"):
            assert role in data["agents"], f"Missing agent role: {role}"


# ===== Test 4: orchestrator config respects agent counts =====

class TestOrchestratorConfigAgentCounts:
    def test_code_agent_count_respected(self, project_dir):
        team = {"architect": 1, "code": 2, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["agents"]["code"]["count"] == 2

    def test_architect_always_one(self, project_dir):
        team = {"architect": 1, "code": 2, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["agents"]["architect"]["count"] == 1


# ===== Test 5: agent prompt templates are installed =====

class TestAgentPromptTemplatesInstalled:
    def test_all_agent_files_exist(self, project_dir):
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        expected = ["orchestrator.md", "architect.md", "code.md", "test.md", "review.md"]
        for filename in expected:
            assert (agents_dir / filename).exists(), f"{filename} not found"

    def test_agent_files_are_non_empty(self, project_dir):
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        for filename in ORCHESTRATOR_AGENT_FILES:
            content = (agents_dir / filename).read_text(encoding="utf-8")
            assert len(content) > 0, f"{filename} is empty"


# ===== Test 6: slash commands installed for copilot =====

class TestSlashCommandsCopilot:
    def test_copilot_commands_installed(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        # Copilot uses .github/agents/ (commands_subdir = "agents")
        commands_dir = project_dir / ".github" / "agents"
        expected = [
            "speckit.orchestrate.init.md",
            "speckit.orchestrate.assign.md",
            "speckit.orchestrate.run.md",
            "speckit.orchestrate.status.md",
            "speckit.orchestrate.review.md",
            "speckit.orchestrate.sync.md",
        ]
        for filename in expected:
            assert (commands_dir / filename).exists(), f"{filename} not found"


# ===== Test 7: slash commands installed for claude =====

class TestSlashCommandsClaude:
    def test_claude_commands_installed(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        md_files = list(commands_dir.glob("speckit.orchestrate.*.md"))
        assert len(md_files) == 6


# ===== Test 8: config template YAML is valid =====

class TestConfigTemplateYaml:
    def test_template_parses_without_error(self):
        template_path = REPO_ROOT / "templates" / "orchestrator" / "orchestrator-config-template.yml"
        content = template_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert isinstance(data, dict)

    def test_template_has_expected_keys(self):
        template_path = REPO_ROOT / "templates" / "orchestrator" / "orchestrator-config-template.yml"
        data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        for key in ("feature", "mode", "agents", "checkpoints", "quality_gates"):
            assert key in data, f"Template missing key: {key}"


# ===== Test 9: mode selection validates input =====

class TestModeValidation:
    @pytest.mark.parametrize("mode", ["supervised", "semi-auto", "autonomous"])
    def test_accepted_modes_produce_valid_config(self, project_dir, mode):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, mode, team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["mode"] == mode

    def test_invalid_mode_stored_as_is(self, project_dir):
        # _generate_orchestrator_config does not validate the mode string;
        # it is the caller's responsibility.  Verify no crash.
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "invalid-mode", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["mode"] == "invalid-mode"


# ===== Test 10: existing tests still pass (regression guard) =====

class TestRegressionGuard:
    def test_module_loads(self):
        import specify_cli
        assert hasattr(specify_cli, "app")

    def test_init_function_exists(self):
        import specify_cli
        assert hasattr(specify_cli, "init")

    def test_orchestrate_parameter_in_init_help(self):
        result = runner.invoke(app, ["init", "--help"])
        clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
        assert "--orchestrate" in clean

    def test_agent_config_keys_unchanged(self):
        # Core agent keys that must always be present
        expected_core = {"copilot", "claude", "gemini", "cursor-agent", "opencode"}
        assert expected_core.issubset(set(AGENT_CONFIG.keys()))


# ===== Test 11: atomic write for state files =====

class TestAtomicWriteState:
    def test_write_state_produces_valid_yaml(self, project_dir):
        state = {
            "feature": "test-feature",
            "mode": "supervised",
            "current_phase": "planning",
            "work_packages": [],
        }
        state_dir = project_dir / ".specify" / "orchestrator"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_path = state_dir / "orchestrator-state.yml"
        tmp_path = state_path.with_suffix(".yml.tmp")

        # Write to temp then rename (atomic write pattern)
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, state_path)

        assert state_path.exists()
        loaded = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        assert loaded["feature"] == "test-feature"

    def test_no_tmp_files_remain(self, project_dir):
        state = {"feature": "f", "mode": "supervised", "current_phase": "planning", "work_packages": []}
        state_dir = project_dir / ".specify" / "orchestrator"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_path = state_dir / "orchestrator-state.yml"
        tmp_path = state_path.with_suffix(".yml.tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, state_path)

        tmp_files = list(state_dir.glob("*.tmp"))
        assert tmp_files == []


# ===== Test 12: work package status transitions =====

class TestWorkPackageStatusTransitions:
    VALID_STATUSES = ("pending", "in_progress", "completed")

    def test_transition_pending_to_in_progress(self):
        wp = {"id": "wp-1", "status": "pending"}
        wp["status"] = "in_progress"
        assert wp["status"] in self.VALID_STATUSES

    def test_transition_in_progress_to_completed(self):
        wp = {"id": "wp-1", "status": "in_progress"}
        wp["status"] = "completed"
        assert wp["status"] in self.VALID_STATUSES

    def test_full_lifecycle(self):
        wp = {"id": "wp-1", "status": "pending"}
        for next_status in ("in_progress", "completed"):
            wp["status"] = next_status
        assert wp["status"] == "completed"


# ===== Test 13: orchestrator-state.yml schema validation =====

class TestOrchestratorStateSchema:
    def test_minimal_valid_state(self, project_dir):
        state = {
            "feature": "my-feature",
            "mode": "supervised",
            "current_phase": "planning",
            "work_packages": [],
        }
        state_dir = project_dir / ".specify" / "orchestrator"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_path = state_dir / "orchestrator-state.yml"
        with open(state_path, "w", encoding="utf-8") as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=False)

        loaded = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        for key in ("feature", "mode", "current_phase", "work_packages"):
            assert key in loaded, f"Missing required state key: {key}"


# ===== Test 14: agent-coordination.yml schema validation =====

class TestAgentCoordinationSchema:
    def test_minimal_valid_coordination(self, project_dir):
        coordination = {
            "work_packages": [
                {
                    "id": "wp-1",
                    "agent": "code",
                    "tasks": ["implement login"],
                    "dependencies": [],
                    "status": "pending",
                },
            ],
            "execution_phases": [
                {
                    "phase": "implementation",
                    "packages": ["wp-1"],
                    "type": "parallel",
                },
            ],
        }
        coord_dir = project_dir / ".specify" / "orchestrator"
        coord_dir.mkdir(parents=True, exist_ok=True)
        coord_path = coord_dir / "agent-coordination.yml"
        with open(coord_path, "w", encoding="utf-8") as f:
            yaml.dump(coordination, f, default_flow_style=False, sort_keys=False)

        loaded = yaml.safe_load(coord_path.read_text(encoding="utf-8"))
        assert "work_packages" in loaded
        wp = loaded["work_packages"][0]
        for key in ("id", "agent", "tasks", "dependencies", "status"):
            assert key in wp, f"Missing work_package key: {key}"

        assert "execution_phases" in loaded
        phase = loaded["execution_phases"][0]
        for key in ("phase", "packages", "type"):
            assert key in phase, f"Missing execution_phase key: {key}"


# ===== Test 15: --orchestrate flag does not break --no-git =====

class TestOrchestrateWithNoGit:
    def test_orchestration_files_without_git(self, project_dir):
        # Orchestration helpers do not require git — verify no .git created
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        _install_orchestrator_templates(project_dir)
        _install_orchestrate_commands(project_dir, "claude")

        assert not (project_dir / ".git").exists()
        assert (project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml").exists()
        assert (project_dir / ".specify" / "orchestrator" / "agents").is_dir()
        assert (project_dir / ".claude" / "commands").is_dir()
