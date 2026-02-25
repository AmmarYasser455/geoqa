# Contributing to GeoQA

Thank you for your interest in contributing to GeoQA! This document provides guidelines and instructions for contributing.

##  Getting Started

### Prerequisites

- Python 3.9+
- Git
- A code editor (VS Code recommended)

### Development Setup

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/geoqa.git
   cd geoqa
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests** to verify setup:
   ```bash
   pytest
   ```

##  Development Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below.

3. **Write tests** for new functionality.

4. **Run the test suite**:
   ```bash
   pytest
   ```

5. **Format your code**:
   ```bash
   black geoqa/ tests/
   isort geoqa/ tests/
   ```

6. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add new quality check for overlapping features"
   ```

7. **Push and create a Pull Request**.

##  Code Style

- **Formatter**: Black (line length = 100)
- **Import sorting**: isort (black profile)
- **Linter**: Ruff
- **Type hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all public modules, classes, and functions

### Example

```python
def check_validity(gdf: gpd.GeoDataFrame) -> dict[str, Any]:
    """Check geometry validity for all features.

    Args:
        gdf: The GeoDataFrame to validate.

    Returns:
        Dictionary with valid_count, invalid_count, and invalid_indices.

    Raises:
        ValueError: If the GeoDataFrame has no geometry column.
    """
    ...
```

##  Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `test:` — Test additions/modifications
- `refactor:` — Code refactoring
- `style:` — Formatting changes
- `chore:` — Build/CI changes

##  Testing

- Write tests in the `tests/` directory using pytest.
- Aim for comprehensive coverage of new functionality.
- Use fixtures for common test data.

##  Code of Conduct

Be respectful and constructive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

##  Questions?

Open an issue or start a discussion on GitHub. We're happy to help!
