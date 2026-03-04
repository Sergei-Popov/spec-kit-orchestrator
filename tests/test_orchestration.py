"""
Unit tests for multi-agent orchestration scaffolding.

Tests cover:
- Orchestrator config generation (_generate_orchestrator_config)
- Agent prompt template installation (_install_orchestrator_templates)
- Orchestrate slash command installation (_install_orchestrate_commands)
- ORCHESTRATE_COMMANDS constant completeness
- CLI --orchestrate flag appears in help text
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path

from specify_cli import (
    _generate_orchestrator_config,
    _install_orchestrator_templates,
    _install_orchestrate_commands,
    ORCHESTRATE_COMMANDS,
    ORCHESTRATE_TEMPLATE_FILES,
    ORCH_PROMPT_INIT,
    app,
)

from typer.testing import CliRunner

runner = CliRunner()


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


# ===== Config generation =====

class TestGenerateOrchestratorConfig:
    def test_config_file_created(self, project_dir):
        team = {"architect": 1, "code": 2, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        assert config_path.exists()

    def test_config_is_valid_yaml(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "semi-auto", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_config_mode_field(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "autonomous", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["mode"] == "autonomous"

    def test_config_code_agent_count(self, project_dir):
        team = {"architect": 1, "code": 3, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["agents"]["code"]["count"] == 3

    def test_config_has_quality_gates(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["quality_gates"]["min_test_coverage"] == 80
        assert data["quality_gates"]["require_review_approval"] is True
        assert data["quality_gates"]["max_review_rounds"] == 3

    def test_config_has_checkpoints(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["checkpoints"]["after_phase"] is True
        assert data["checkpoints"]["before_merge"] is True
        assert data["checkpoints"]["after_work_package"] is False

    def test_config_feature_defaults_empty(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["feature"] == "" or data["feature"] is None

    def test_config_code_agent_parallel(self, project_dir):
        team = {"architect": 1, "code": 2, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        config_path = project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data["agents"]["code"]["parallel"] is True


# ===== Agent templates =====

class TestInstallOrchestratorTemplates:
    def test_creates_agent_prompt_files(self, project_dir):
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        from specify_cli import ORCHESTRATOR_AGENT_CONTENT
        for filename in ORCHESTRATOR_AGENT_CONTENT:
            assert (agents_dir / filename).exists(), f"{filename} not found"

    def test_prompt_files_contain_role(self, project_dir):
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        content = (agents_dir / "architect.md").read_text(encoding="utf-8")
        assert "Architect" in content

    def test_copies_five_agent_files(self, project_dir):
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        md_files = list(agents_dir.glob("*.md"))
        assert len(md_files) == 5


# ===== Slash commands =====

class TestInstallOrchestrateCommands:
    def test_creates_no_agent_files_for_claude(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        md_files = list(commands_dir.glob("speckit.orchestrate.*.agent.md"))
        assert len(md_files) == 0

    def test_creates_three_prompt_files_for_claude(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        md_files = list(commands_dir.glob("speckit.orchestrate-*.prompt.md"))
        assert len(md_files) == 3

    def test_prompt_files_have_content(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        for cmd_file in commands_dir.glob("speckit.orchestrate-*.prompt.md"):
            content = cmd_file.read_text(encoding="utf-8")
            command_name = cmd_file.name.replace(".prompt.md", "")
            agent_line = next(line for line in content.splitlines() if line.startswith("agent: "))
            name_line = next(line for line in content.splitlines() if line.startswith("name: "))
            assert len(content) > 0
            assert "$ARGUMENTS" in content
            assert f"agent: {command_name}" in content
            assert "name:" in content
            assert name_line == f"name: '{command_name}'"
            assert agent_line.removeprefix("agent: ") == name_line.removeprefix("name: '").removesuffix("'")
            assert "description:" in content

    def test_prompt_names_match_template_list(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        expected = set(ORCHESTRATE_TEMPLATE_FILES)
        actual = {f.name for f in commands_dir.glob("speckit.orchestrate-*.prompt.md")}
        assert actual == expected

    def test_no_orchestrate_agent_files_created_for_claude(self, project_dir):
        _install_orchestrate_commands(project_dir, "claude")
        commands_dir = project_dir / ".claude" / "commands"
        assert not list(commands_dir.glob("speckit.orchestrate.*.agent.md"))

    def test_copilot_orchestrate_agent_roles_in_agents_dir(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        agents_dir = project_dir / ".github" / "agents"
        agent_files = list(agents_dir.glob("speckit.orchestrate-*.agent.md"))
        assert len(agent_files) == 3

    def test_copilot_action_prompts_in_prompts_dir(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        prompts_dir = project_dir / ".github" / "prompts"
        prompt_files = list(prompts_dir.glob("speckit.orchestrate-*.prompt.md"))
        assert len(prompt_files) == 3

    def test_copilot_agent_frontmatter_includes_mode(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        agent_path = project_dir / ".github" / "agents" / "speckit.orchestrate-init.agent.md"
        content = agent_path.read_text(encoding="utf-8")
        assert "mode: speckit.orchestrate-init" in content

    def test_gemini_uses_commands_subdir(self, project_dir):
        _install_orchestrate_commands(project_dir, "gemini")
        commands_dir = project_dir / ".gemini" / "commands"
        agent_files = list(commands_dir.glob("speckit.orchestrate.*.agent.md"))
        prompt_files = list(commands_dir.glob("speckit.orchestrate-*.prompt.md"))
        assert len(agent_files) == 0
        assert len(prompt_files) == 3


# ===== ORCHESTRATE_COMMANDS constant =====

class TestOrchestrateCommandsConstant:
    def test_has_three_commands(self):
        assert len(ORCHESTRATE_COMMANDS) == 3

    def test_all_keys_start_with_orchestrate(self):
        for key in ORCHESTRATE_COMMANDS:
            assert key.startswith("orchestrate."), f"{key} does not start with 'orchestrate.'"

    def test_all_values_are_nonempty_strings(self):
        for key, value in ORCHESTRATE_COMMANDS.items():
            assert isinstance(value, str) and len(value) > 0, f"Bad description for {key}"


# ===== CLI integration =====

class TestOrchestrateCliFlag:
    def test_orchestrate_flag_in_help(self):
        result = runner.invoke(app, ["init", "--help"])
        # Strip ANSI escape codes before checking
        import re
        clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
        assert "--orchestrate" in clean


# ===== Embedded content =====

class TestEmbeddedContentWrittenWithoutTemplateFiles:
    """Verify files are written from embedded constants, not copied from disk."""

    def test_agent_templates_written_in_empty_project(self, project_dir):
        # project_dir has no .specify/templates/ — embedded constants must suffice
        _install_orchestrator_templates(project_dir)
        agents_dir = project_dir / ".specify" / "orchestrator" / "agents"
        from specify_cli import ORCHESTRATOR_AGENT_CONTENT
        for filename in ORCHESTRATOR_AGENT_CONTENT:
            path = agents_dir / filename
            assert path.exists(), f"{filename} missing"
            assert len(path.read_text(encoding="utf-8")) > 50, f"{filename} too short"

    def test_no_agent_files_written_in_empty_project(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        agents_dir = project_dir / ".github" / "agents"
        assert len(list(agents_dir.glob("speckit.orchestrate-*.agent.md"))) == 3

    def test_prompt_files_written_in_empty_project(self, project_dir):
        _install_orchestrate_commands(project_dir, "copilot")
        # Copilot: action prompts in .github/prompts/
        prompts_dir = project_dir / ".github" / "prompts"
        for stem in ("init", "run", "status"):
            path = prompts_dir / f"speckit.orchestrate-{stem}.prompt.md"
            assert path.exists(), f"{path.name} missing"
            content = path.read_text(encoding="utf-8")
            assert "$ARGUMENTS" in content, f"{path.name} missing $ARGUMENTS"

    def test_all_three_artifacts_produced(self, project_dir):
        team = {"architect": 1, "code": 1, "test": 1, "review": 1}
        _generate_orchestrator_config(project_dir, "supervised", team)
        _install_orchestrator_templates(project_dir)
        _install_orchestrate_commands(project_dir, "copilot")

        assert (project_dir / ".specify" / "orchestrator" / "orchestrator-config.yml").exists()
        assert len(list((project_dir / ".specify" / "orchestrator" / "agents").glob("*.md"))) == 5
        assert len(list((project_dir / ".github" / "agents").glob("speckit.orchestrate-*.agent.md"))) == 3
        assert len(list((project_dir / ".github" / "prompts").glob("speckit.orchestrate-*.prompt.md"))) == 3


class TestOrchestrateInitDynamicAgentInstructions:
    def test_prompt_includes_dynamic_agent_handoff_requirements(self):
        assert 'label: "↩ Return to Orchestrator"' in ORCH_PROMPT_INIT
        assert 'label: "🧪 Run Tests"' in ORCH_PROMPT_INIT
        assert 'label: "🔍 Request Review"' in ORCH_PROMPT_INIT
        assert 'label: "⚙ Send Fixes to Code Backend"' in ORCH_PROMPT_INIT
