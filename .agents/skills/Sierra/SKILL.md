```markdown
# Sierra Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the Sierra Python codebase. You'll learn how to structure files, write imports and exports, follow commit message standards, and organize tests. These patterns ensure consistency and maintainability across the project.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `user_profile.py`, `data_loader.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_config
    from ..models import User
    ```

### Export Style
- Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    __all__ = ['User', 'parse_config']
    ```

### Commit Messages
- Follow the **Conventional Commits** standard.
- Use the `feat` prefix for new features.
- Keep commit messages clear and descriptive (average length: 117 characters).
  - Example:
    ```
    feat: add user authentication module with JWT support and update documentation for setup instructions
    ```

## Workflows

### Adding a New Feature
**Trigger:** When developing a new feature for the codebase  
**Command:** `/add-feature`

1. Create a new Python file using snake_case naming.
2. Implement the feature using relative imports as needed.
3. Define named exports with `__all__`.
4. Write or update tests in a corresponding `*.test.*` file.
5. Commit your changes using the `feat` prefix and a descriptive message.
6. Push your branch and open a pull request.

### Writing and Running Tests
**Trigger:** When verifying code correctness  
**Command:** `/run-tests`

1. Locate or create a test file matching the pattern `*.test.*` (e.g., `user_profile.test.py`).
2. Write your test cases according to the project's style.
3. Use the project's preferred method to run tests (framework unknown; consult project docs or use standard Python test runners).
4. Review test results and fix any failures.

## Testing Patterns

- Test files follow the pattern: `*.test.*` (e.g., `module.test.py`).
- The specific test framework is not detected; use standard Python testing practices.
- Place tests alongside the code or in a dedicated tests directory.
- Example test file:
  ```python
  # user_profile.test.py
  import unittest
  from .user_profile import UserProfile

  class TestUserProfile(unittest.TestCase):
      def test_creation(self):
          user = UserProfile("alice")
          self.assertEqual(user.name, "alice")
  ```

## Commands
| Command      | Purpose                                      |
|--------------|----------------------------------------------|
| /add-feature | Start the process of adding a new feature    |
| /run-tests   | Run all tests in the codebase                |
```
