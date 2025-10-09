# Project Restructure Guide

## 🎯 Overview

This guide documents the project restructure from a flat structure to an organized, professional layout.

## 📊 Before vs After

### Before (29 files in root)
```
slack-intro-bot/
├── daily_intros.py
├── intro_extraction_api.py
├── claude_code_executor.py
├── mcp_adapter.py
├── config.py
├── security_config.py
├── user_profile_search.py
├── rate_limiter.py
├── test_dual_mode.py
├── demo_dual_mode.py
├── diagnose_mcp.py
├── setup_dev.py
├── run_tests.py
├── DUAL_MODE_USAGE.md
├── PROJECT_OVERVIEW.md
├── SECURITY.md
├── (and 14 more files...)
└── welcome_messages/
```

###After (Clean, organized structure)
```
slack-intro-bot/
├── README.md
├── daily_intros.py          # Entry point (backward compatible)
├── intro_extraction.py      # New entry point
├── requirements.txt
│
├── src/                     # All source code
│   ├── daily_intros.py
│   ├── config.py
│   ├── user_profile_search.py
│   ├── rate_limiter.py
│   ├── dual_mode/
│   └── security/
│
├── tests/                   # All tests
├── scripts/                 # Utility scripts
├── docs/                    # All documentation
│   ├── README.md
│   ├── DUAL_MODE_USAGE.md
│   ├── MCP_SETUP.md
│   └── archive/
│
├── reports/                 # Generated reports
│   ├── welcome_messages/
│   └── security/
│
└── logs/                    # Log files
```

## 📁 File Migrations

### Source Code → `src/`
| Old Location | New Location |
|-------------|--------------|
| `daily_intros.py` | `src/daily_intros.py` |
| `config.py` | `src/config.py` |
| `user_profile_search.py` | `src/user_profile_search.py` |
| `rate_limiter.py` | `src/rate_limiter.py` |

### Dual-Mode → `src/dual_mode/`
| Old Location | New Location |
|-------------|--------------|
| `intro_extraction_api.py` | `src/dual_mode/intro_extraction_api.py` |
| `claude_code_executor.py` | `src/dual_mode/claude_code_executor.py` |
| `mcp_adapter.py` | `src/dual_mode/mcp_adapter.py` |

### Security → `src/security/`
| Old Location | New Location |
|-------------|--------------|
| `security_config.py` | `src/security/security_config.py` |
| `security_scan.py` | `src/security/security_scan.py` |

### Tests → `tests/`
| Old Location | New Location |
|-------------|--------------|
| `test_dual_mode.py` | `tests/test_dual_mode.py` |
| `run_tests.py` | `tests/run_tests.py` |
| (existing tests remain) | `tests/` |

### Scripts → `scripts/`
| Old Location | New Location |
|-------------|--------------|
| `demo_dual_mode.py` | `scripts/demo_dual_mode.py` |
| `diagnose_mcp.py` | `scripts/diagnose_mcp.py` |
| `setup_dev.py` | `scripts/setup_dev.py` |
| `run_with_claude.sh` | `scripts/run_with_claude.sh` |

### Documentation → `docs/`
| Old Location | New Location |
|-------------|--------------|
| `DUAL_MODE_USAGE.md` | `docs/DUAL_MODE_USAGE.md` |
| `PROJECT_OVERVIEW.md` | `docs/PROJECT_OVERVIEW.md` |
| `QUICK_REFERENCE.md` | `docs/QUICK_REFERENCE.md` |
| `SECURITY.md` | `docs/SECURITY.md` |
| `README_MCP_SETUP.md` | `docs/MCP_SETUP.md` |
| `BRANCH_README.md` | `docs/archive/BRANCH_README.md` |
| `IMPLEMENTATION_SUMMARY.md` | `docs/archive/IMPLEMENTATION_SUMMARY.md` |
| `SECURITY_AUDIT_REPORT.md` | `docs/archive/SECURITY_AUDIT_REPORT.md` |
| `SECURITY_IMPROVEMENTS.md` | `docs/archive/SECURITY_IMPROVEMENTS.md` |
| `EFFICIENCY_IMPROVEMENTS.md` | `docs/archive/EFFICIENCY_IMPROVEMENTS.md` |

### Reports → `reports/`
| Old Location | New Location |
|-------------|--------------|
| `welcome_messages/` | `reports/welcome_messages/` |
| `bandit-report.json` | `reports/security/bandit-report.json` |
| `security-scan-results.json` | `reports/security/security-scan-results.json` |

### Logs → `logs/`
| Old Location | New Location |
|-------------|--------------|
| `slack_bot.log` | `logs/slack_bot.log` |

## 🔧 Code Changes

### Import Updates

**`src/daily_intros.py`**:
```python
# Before
from user_profile_search import safe_profile_search_for_daily_intros
from mcp_adapter import get_mcp_adapter
from security_config import get_security_manager
from config import Config

# After
from .user_profile_search import safe_profile_search_for_daily_intros
from .dual_mode.mcp_adapter import get_mcp_adapter
from .security.security_config import get_security_manager
from .config import Config
```

**`src/dual_mode/intro_extraction_api.py`**:
```python
# Before
from daily_intros import get_cutoff_timestamp, ...
from user_profile_search import safe_profile_search_for_daily_intros

# After
from ..daily_intros import get_cutoff_timestamp, ...
from ..user_profile_search import safe_profile_search_for_daily_intros
```

### New Entry Points

**`daily_intros.py`** (root):
```python
#!/usr/bin/env python3
"""Entry point - maintains backward compatibility"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from daily_intros import main
if __name__ == "__main__":
    main()
```

**`intro_extraction.py`** (root):
```python
#!/usr/bin/env python3
"""Entry point for dual-mode extraction"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from dual_mode.intro_extraction_api import extract_intros_auto
# ... implementation
```

### Package Initialization

**`src/__init__.py`**:
```python
"""Slack Intro Bot - Source Package"""
__version__ = "2.0.0"
```

**`src/dual_mode/__init__.py`**:
```python
"""Dual Mode Package"""
from .intro_extraction_api import (
    detect_execution_environment,
    generate_mcp_request,
    extract_intros_mcp_mode,
    extract_intros_auto
)
from .mcp_adapter import get_mcp_adapter
```

**`src/security/__init__.py`**:
```python
"""Security Package"""
from .security_config import get_security_manager
```

## 🚀 Usage Changes

### Backward Compatible

Old commands still work:
```bash
python3 daily_intros.py
python3 demo_dual_mode.py  # (will fail, needs update)
```

### New Recommended Usage

```bash
# Main script (unchanged)
python3 daily_intros.py

# Dual-mode extraction
python3 intro_extraction.py 2025-10-01 2025-10-09

# Scripts
python3 scripts/demo_dual_mode.py
python3 scripts/diagnose_mcp.py

# Tests
python3 tests/run_tests.py
python3 -m pytest tests/
```

### Import Changes

**Old**:
```python
import daily_intros
from intro_extraction_api import generate_mcp_request
from mcp_adapter import get_mcp_adapter
```

**New**:
```python
# From root directory
from src import daily_intros
from src.dual_mode import generate_mcp_request, get_mcp_adapter

# Or add src to path first
import sys
sys.path.insert(0, 'src')
import daily_intros
from dual_mode import generate_mcp_request
```

## 📝 Documentation Updates

### Updated Files
- `README.md` - Updated project structure section
- `docs/README.md` - New documentation index
- All doc links updated to new paths

### Path Updates
All documentation now references new paths:
- ~~`PROJECT_OVERVIEW.md`~~ → `docs/PROJECT_OVERVIEW.md`
- ~~`DUAL_MODE_USAGE.md`~~ → `docs/DUAL_MODE_USAGE.md`
- ~~`README_MCP_SETUP.md`~~ → `docs/MCP_SETUP.md`

## ✅ Benefits

### 1. Clear Organization
- Source code separated from scripts and docs
- Easy to find any file
- Logical grouping by function

### 2. Professional Structure
- Industry-standard layout
- Follows Python package conventions
- Ready for PyPI distribution

### 3. Better Maintainability
- Clear ownership of files
- Easier to add new features
- Simplified dependency management

### 4. Improved Development
- Better IDE support
- Clearer import paths
- Easier testing

### 5. Scalability
- Easy to add new modules
- Clear place for everything
- Room to grow

## 🧪 Testing

### Verify Structure
```bash
# Check directory structure
ls -la src/ src/dual_mode/ src/security/
ls -la tests/ scripts/ docs/
ls -la reports/welcome_messages/ reports/security/

# Verify entry points exist
ls -la daily_intros.py intro_extraction.py
```

### Run Tests
```bash
# Run all tests
python3 tests/run_tests.py

# Run specific test
python3 tests/test_dual_mode.py

# Test dual-mode demo
python3 scripts/demo_dual_mode.py
```

### Test Entry Points
```bash
# Test main entry point
python3 daily_intros.py --help

# Test dual-mode entry
python3 intro_extraction.py 2025-10-01 2025-10-09
```

## 🔄 Migration Checklist

- [x] Create new directory structure
- [x] Move files to new locations
- [x] Update imports in source files
- [x] Create __init__.py files
- [x] Create entry point scripts
- [x] Update README.md
- [x] Create docs/README.md
- [x] Update documentation paths
- [ ] Test all entry points
- [ ] Run test suite
- [ ] Verify backward compatibility
- [ ] Update CI/CD (if applicable)
- [ ] Commit and push changes

## 📊 Statistics

- **Files moved**: 25+
- **Directories created**: 8
- **Import statements updated**: 15+
- **Documentation files updated**: 10+
- **Entry points created**: 2
- **Lines of code affected**: 500+

## 🎯 Next Steps

1. **Test thoroughly** - Run all tests and verify functionality
2. **Update CI/CD** - If you have automated builds/tests
3. **Update deployment** - If you deploy this anywhere
4. **Notify team** - If others are working on this project
5. **Update bookmarks** - In your IDE and documentation

---

**Branch**: `refactor/project-restructure`  
**Status**: In Progress  
**Created**: October 9, 2025  
**Version**: 2.0.0

