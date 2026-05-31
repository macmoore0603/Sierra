"""
Tests for ProjectManager.
"""
import json
import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from project_manager import ProjectManager


@pytest.fixture
def pm(tmp_path):
    """Create a ProjectManager rooted in a temp directory."""
    return ProjectManager(str(tmp_path))


class TestProjectCreation:
    def test_temp_project_exists_on_init(self, pm):
        assert "temp" in pm.list_projects()

    def test_create_new_project(self, pm):
        ok, msg = pm.create_project("alpha")
        assert ok is True
        assert "alpha" in pm.list_projects()

    def test_duplicate_project_returns_false(self, pm):
        pm.create_project("dup")
        ok, msg = pm.create_project("dup")
        assert ok is False
        assert "already exists" in msg

    def test_empty_name_after_sanitization(self, pm):
        ok, msg = pm.create_project("!!!")
        assert ok is False
        assert "empty" in msg.lower()

    def test_sanitization_strips_special_chars(self, pm):
        ok, _ = pm.create_project("hello/world<>")
        assert ok is True
        assert "helloworld" in pm.list_projects()

    def test_project_has_cad_and_browser_subdirs(self, pm):
        pm.create_project("dirs-test")
        project_path = pm.projects_dir / "dirs-test"
        assert (project_path / "cad").is_dir()
        assert (project_path / "browser").is_dir()


class TestProjectSwitching:
    def test_switch_to_existing_project(self, pm):
        pm.create_project("beta")
        ok, msg = pm.switch_project("beta")
        assert ok is True
        assert pm.current_project == "beta"

    def test_switch_to_nonexistent_project(self, pm):
        ok, msg = pm.switch_project("nope")
        assert ok is False
        assert "does not exist" in msg

    def test_switch_empty_name(self, pm):
        ok, msg = pm.switch_project("@@@")
        assert ok is False


class TestListProjects:
    def test_list_projects_sorted(self, pm):
        pm.create_project("charlie")
        pm.create_project("alpha")
        projects = pm.list_projects()
        assert projects == sorted(projects)


class TestChatLogging:
    def test_log_and_retrieve_chat(self, pm):
        pm.log_chat("User", "Hello")
        pm.log_chat("Sierra", "Hi there!")

        history = pm.get_recent_chat_history(limit=10)
        assert len(history) == 2
        assert history[0]["sender"] == "User"
        assert history[1]["text"] == "Hi there!"

    def test_empty_history(self, pm):
        assert pm.get_recent_chat_history() == []

    def test_limit_respected(self, pm):
        for i in range(20):
            pm.log_chat("User", f"msg {i}")
        history = pm.get_recent_chat_history(limit=5)
        assert len(history) == 5
        assert history[0]["text"] == "msg 15"


class TestCadArtifacts:
    def test_save_cad_artifact(self, pm, tmp_path):
        # Create a fake STL file
        stl_file = tmp_path / "source.stl"
        stl_file.write_text("solid test\nendsolid test")

        result = pm.save_cad_artifact(str(stl_file), "a cool bolt")
        assert result is not None
        assert os.path.exists(result)
        assert result.endswith(".stl")

    def test_save_missing_source_returns_none(self, pm):
        result = pm.save_cad_artifact("/nonexistent/file.stl", "nope")
        assert result is None


class TestProjectContext:
    def test_context_includes_files(self, pm):
        project_path = pm.get_current_project_path()
        (project_path / "notes.txt").write_text("hello world")

        ctx = pm.get_project_context()
        assert "notes.txt" in ctx
        assert "hello world" in ctx

    def test_context_skips_large_files(self, pm):
        project_path = pm.get_current_project_path()
        (project_path / "big.txt").write_text("x" * 20000)

        ctx = pm.get_project_context(max_file_size=100)
        assert "too large" in ctx

    def test_context_nonexistent_project(self, pm):
        pm.current_project = "nope"
        ctx = pm.get_project_context()
        assert "does not exist" in ctx
