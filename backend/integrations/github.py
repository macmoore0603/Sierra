"""
GitHubIntegration - Example personal integration for GitHub.

Demonstrates how to implement GitHub-related actions (list repos, create issues, etc.)
using the BaseIntegration pattern with proper safety and memory logging.

In production, this would use PyGithub or the GitHub REST API with a token.
"""

from typing import Dict, Any

from .base import BaseIntegration


class GitHubIntegration(BaseIntegration):
    def __init__(self):
        super().__init__(name="github")

    def can_handle(self, intent: str) -> bool:
        intent = intent.lower()
        return any(kw in intent for kw in ["github", "repo", "issue", "pull request", "pr", "commit"])

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        action = action.lower()

        if action in ["list_repos", "get_repos"]:
            return {
                "status": "success",
                "repos": ["Sierra", "personal-notes", "experiments"],
                "message": "Here are your repositories (stub data)"
            }

        if action == "create_issue":
            title = params.get("title", "New issue from Sierra")
            body = params.get("body", "")
            self.log_to_memory(f"Created GitHub issue: {title}", {"action": "create_issue"})
            return {
                "status": "success",
                "message": f"Issue '{title}' created (stub). Confirm to actually create on GitHub.",
                "requires_user_confirmation": True
            }

        return {
            "status": "error",
            "message": f"Unknown GitHub action: {action}"
        }
