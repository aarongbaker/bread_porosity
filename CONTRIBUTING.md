# Contributing to Bread Porosity Analysis Tool

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.9 or newer
- Git installed on your machine
- Basic familiarity with GitHub workflow (fork, branch, pull request)

### Setup Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/bread_porosity.git
   cd bread_porosity
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies in development mode:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

5. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check the [Issues](https://github.com/aarongbaker/bread_porosity/issues) page to see if it's already reported
- Verify you're using the latest version
- Test with different images or parameters if applicable

**When submitting a bug report, include:**
- Clear title and description
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version)
- Sample image if image-related (if possible)
- Error message or traceback
- Any relevant screenshots

### Suggesting Enhancements

**Before suggesting an enhancement:**
- Check if it's already in the [Issues](https://github.com/aarongbaker/bread_porosity/issues) or [Changelog](CHANGELOG.md)
- Consider the scope and impact on existing users

**When suggesting an enhancement, include:**
- Clear, descriptive title
- Detailed description of the desired feature
- Use cases and examples
- Possible implementation approach (optional)
- Screenshots or mockups (if applicable)

### Pull Requests

**Process:**

1. **Keep your branch updated:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes:**
   - Follow the code style (see below)
   - Keep commits atomic and focused
   - Write clear commit messages

3. **Test thoroughly:**
   ```bash
   python gui.py  # Test GUI
   python -m pytest  # If tests exist
   ```

4. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request:**
   - Reference any related issues
   - Describe what changes you made and why
   - Include screenshots for UI changes
   - Be open to feedback and iteration

**PR Requirements:**
- Code should follow existing style conventions
- All imports should be properly organized
- No breaking changes without discussion
- Documentation should be updated if needed
- Changes should be tested on your system

---

## Code Style Guidelines

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions
- Use 4 spaces for indentation (never tabs)
- Maximum line length: 100 characters (comments/docstrings can be 88)
- Use meaningful variable and function names
- Add docstrings to classes and functions

### Example:
```python
def calculate_porosity(image_array: np.ndarray, min_hole_size: int = 10) -> float:
    """
    Calculate bread porosity percentage from image array.
    
    Args:
        image_array: Processed binary image as numpy array
        min_hole_size: Minimum hole area in pixels to count
        
    Returns:
        Porosity percentage (0-100)
    """
    # Implementation here
    pass
```

### Comments
- Use comments to explain WHY, not WHAT
- Keep comments up-to-date with code changes
- Avoid redundant comments

```python
# GOOD: Explains the reason
# Use CLAHE for local contrast enhancement to handle uneven lighting
enhanced = cv2.createCLAHE(clipLimit=2.0).apply(gray)

# AVOID: Redundant comment
# Create CLAHE
enhanced = cv2.createCLAHE(clipLimit=2.0).apply(gray)
```

### Imports
- Organize imports in three groups (stdlib, third-party, local)
- One import per line (except `from x import a, b`)
- Sort alphabetically within groups

```python
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from analyze import analyze_bread_image
from shared_utils import encode_vessel_openness
```

---

## Areas for Contribution

### High Priority
- Bug fixes for reported issues
- Documentation improvements
- Performance optimizations
- Test coverage expansion

### Medium Priority
- New bread type profiles
- Additional export formats
- UI/UX improvements
- Localization support

### Low Priority
- Code refactoring (unless addressing issues)
- Style-only changes
- Experimental features

### Areas for Advanced Contributors
- ML model improvements
- GPU acceleration support
- Web interface development
- Advanced statistical features

---

## Documentation

### When to Update Docs
- New features added
- Behavior changes
- Bug fixes affecting users
- API changes

### What to Update
- Inline code comments (if logic changed)
- DOCUMENTATION.md (if user-facing)
- CHANGELOG.md (in your PR description)
- Code docstrings (if function signatures changed)

### Documentation Style
- Use clear, concise language
- Include examples where helpful
- Keep consistency with existing docs
- Link to related sections

---

## Commit Message Guidelines

Write clear, descriptive commit messages:

```
[SHORT SUMMARY - 50 chars max]

[OPTIONAL LONGER DESCRIPTION]
- More detailed explanation if needed
- Multiple bullet points for clarity
- Explains what and why, not how

Fixes #123
```

### Good Examples
```
Add vessel openness encoding to shared_utils

Move duplicate vessel encoding logic from recipe_predictor.py and 
recipe_ml_advanced.py into shared_utils.py to eliminate redundancy.

Fixes #45
```

```
Fix status label text cutoff in GUI

Increase wraplength from 290 to 300 pixels and reduce padding
in status section to prevent text from being cut off.

Fixes #12
```

### Types of Commits
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring without behavior change
- `docs:` Documentation updates
- `perf:` Performance improvements
- `test:` Test additions/modifications
- `chore:` Build, dependency, or tooling changes

---

## Testing

### Manual Testing Checklist
- [ ] GUI launches without errors
- [ ] Can load and analyze images
- [ ] Multi-slice loaf analysis works
- [ ] Recipes can be added/modified
- [ ] Export functionality works
- [ ] Quality control profiles load correctly
- [ ] No console errors or warnings

### Testing Your Changes
```bash
# Test imports
python -c "from bread_porosity import *; print('OK')"

# Test GUI
python gui.py

# Test specific module
python -c "from recipe_predictor import RecipePredictor; print('OK')"
```

---

## Release Process

The maintainer will handle releases, but if you're helping:

1. **Version updates** follow [Semantic Versioning](https://semver.org/)
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Update CHANGELOG.md** with release notes
3. **Tag the commit** with version number
4. **Create GitHub Release** with changelog

---

## Community Guidelines

### Be Respectful
- Treat all contributors with respect
- Accept constructive criticism gracefully
- Help others learn and grow
- No harassment, discrimination, or hostility

### Be Professional
- Keep discussions focused and on-topic
- Avoid excessive self-promotion
- Provide helpful, actionable feedback
- Give credit where due

### Be Collaborative
- Assume good intentions
- Ask clarifying questions
- Offer help to other contributors
- Share knowledge generously

---

## Questions?

- Check [DOCUMENTATION.md](DOCUMENTATION.md) first
- Review existing [Issues](https://github.com/aarongbaker/bread_porosity/issues)
- Look at closed issues for similar questions
- Open a new discussion issue if needed

---

## Recognition

Contributors will be recognized in:
- Pull request discussions
- Release notes (if requested)
- Contributors section (if applicable)

**Thank you for contributing to make bread analysis better! 🍞**
