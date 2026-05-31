"""
Behavioral tests for ProjectManager.

Covers project creation, switching, chat logging, context retrieval,
and CAD artifact saving.
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
    """Create a fresh ProjectManager rooted in a temp directory."""
    return ProjectManager(str(tmp_path))


class TestProjectCreation:
    def test_creates_temp_project_on_init(self, pm):
        projects = pm.list_projects()
        assert "temp" in projects

    def test_create_new_project(self, pm):
        ok, msg = pm.create_project("my-widget")
        assert ok is True
        assert "my-widget" in msg
        assert "my-widget" in pm.list_projects()

    def test_create_project_creates_subdirs(self, pm):
        pm.create_project("sub-test")
        project_path = pm.projects_dir / "sub-test"
        assert (project_path / "cad").is_dir()
        assert (project_path / "browser").is_dir()

    def test_create_duplicate_project_fails(self, pm):
        pm.create_project("dup")
        ok, msg = pm.create_project("dup")
        assert ok is False
        assert "already exists" in msg

    def test_create_project_sanitizes_name(self, pm):
        ok, _ = pm.create_project("bad/name!@#")
        assert ok is True
        assert "badname" in pm.list_projects()


class TestProjectSwitching:
    def test_switch_to_existing_project(self, pm):
        pm.create_project("target")
        ok, msg = pm.switch_project("target")
        assert ok is True
        assert pm.current_project == "target"

    def test_switch_to_nonexistent_fails(self, pm):
        ok, msg = pm.switch_project("ghost")
        assert ok is False
        assert "does not exist" in msg

    def test_current_project_path_updates(self, pm):
        pm.create_project("pathtest")
        pm.switch_project("pathtest")
        assert pm.get_current_project_path().name == "pathtest"


class TestChatLogging:
    def test_log_chat_creates_file(self, pm):
        pm.log_chat("User", "hello world")
        log_file = pm.get_current_project_path() / "chat_history.jsonl"
        assert log_file.exists()

    def test_log_chat_appends_jsonl(self, pm):
        pm.log_chat("User", "first")
        pm.log_chat("Sierra", "second")
        log_file = pm.get_current_project_path() / "chat_history.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2
        entry = json.loads(lines[0])
        assert entry["sender"] == "User"
        assert entry["text"] == "first"

    def test_get_recent_chat_history(self, pm):
        for i in range(15):
            pm.log_chat("User", f"msg-{i}")
        history = pm.get_recent_chat_history(limit=5)
        assert len(history) == 5
        assert history[0]["text"] == "msg-10"
        assert history[-1]["text"] == "msg-14"

    def test_get_chat_history_empty(self, pm):
        history = pm.get_recent_chat_history()
        assert history == []


class TestCadArtifact:
    def test_save_cad_artifact_copies_file(self, pm, tmp_path):
        stl = tmp_path / "model.stl"
        stl.write_text("solid test\nendsolid test")
        saved = pm.save_cad_artifact(str(stl), "test cube")
        assert saved is not None
        assert os.path.exists(saved)
        assert "test_cube" in os.path.basename(saved)

    def test_save_cad_artifact_missing_source(self, pm):
        result = pm.save_cad_artifact("/does/not/exist.stl", "nope")
        assert result is None


class TestProjectContext:
    def test_context_includes_files(self, pm):
        project_path = pm.get_current_project_path()
        (project_path / "readme.txt").write_text("Hello from project")
        ctx = pm.get_project_context()
        assert "readme.txt" in ctx
        assert "Hello from project" in ctx

    def test_context_skips_large_files(self, pm):
        project_path = pm.get_current_project_path()
        (project_path / "big.txt").write_text("x" * 20000)
        ctx = pm.get_project_context(max_file_size=100)
        assert "too large" in ctx

    def test_context_empty_project(self, pm):
        pm.create_project("empty")
        pm.switch_project("empty")
        ctx = pm.get_project_context()
        assert "No files in project yet" in ctx
