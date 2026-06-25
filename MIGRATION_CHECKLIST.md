# Project Reorganization Checklist

## Step-by-Step Migration Guide

### Phase 1: Prepare (Do First)
- [ ] Create a backup of the entire project
- [ ] Open terminal in project root: `C:\Users\Charanya\OneDrive\Desktop\api-doc-assistant`

### Phase 2: Move Files
Execute these PowerShell commands:
```powershell
# Move .env
Move-Item -Path "docs\.env" -Destination ".env" -Force

# Move .gitignore  
Move-Item -Path "docs\.gitignore" -Destination ".gitignore" -Force

# Move main.py
Move-Item -Path "docs\main.py" -Destination "main.py" -Force
```

### Phase 3: Verify Structure
After moving, your structure should be:
```
api-doc-assistant/
├── docs/
│   ├── api_guide.pdf
│   └── authentication.md
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── venv/ (will be created next)
```

### Phase 4: Set Up Virtual Environment
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Phase 5: Update main.py
Ensure your `main.py` uses correct paths:
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Example: Access docs folder
docs_path = os.path.join(os.path.dirname(__file__), 'docs')
api_guide_path = os.path.join(docs_path, 'api_guide.pdf')
auth_guide_path = os.path.join(docs_path, 'authentication.md')

# Your LangChain + Gemini code here
```

### Phase 6: Commit Changes
```powershell
git add .
git commit -m "refactor: reorganize project structure following Python best practices"
```

## File-by-File Breakdown

| File | Purpose | Auto-Generated | Committed to Git |
|------|---------|----------------|------------------|
| `.env` | Secrets & API keys | ❌ Manual | ❌ No (in .gitignore) |
| `.gitignore` | Git ignore rules | ❌ Manual | ✅ Yes |
| `main.py` | Entry point/logic | ❌ Manual | ✅ Yes |
| `requirements.txt` | Dependencies | ❌ Manual | ✅ Yes |
| `venv/` | Virtual environment | ✅ Auto | ❌ No (in .gitignore) |
| `docs/` | Static docs | ❌ Manual | ✅ Yes (pdfs/md files) |

## Why This Structure?

✅ **Separates concerns**: Code at root, documentation in docs/  
✅ **Virtual environment isolated**: venv/ keeps dependencies separate  
✅ **Security**: .env not committed, environment-specific configs safe  
✅ **Scalability**: Ready for src/ package structure as project grows  
✅ **Python conventions**: Follows PEP 8 and industry standards  
✅ **CI/CD friendly**: requirements.txt enables automated deployments  

## Next Steps

1. Run the migration commands above
2. Test that imports work: `python main.py`
3. Verify all dependencies load: `pip show langchain chromadb google-generativeai`
4. Create a `.env.example` template (without secrets) for team collaboration
5. Consider adding `src/` subfolder as your project grows

---
**Notes:**
- Keep `docs/` for non-code documentation only
- Consider adding `.github/workflows/` for CI/CD later
- Add `tests/` folder when you write unit tests
- Use `src/` folder for your LangChain modules as complexity increases
