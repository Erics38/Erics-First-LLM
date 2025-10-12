#!/bin/bash
# Pre-Upload Security Check
# Run this before pushing to GitHub

echo "🔍 Running pre-upload security checks..."
echo ""

ERRORS=0

# Check 1: Verify .env is not tracked
echo "1. Checking .env is not in git..."
if git ls-files | grep -q "^\.env$"; then
    echo "   ❌ ERROR: .env is tracked by git!"
    echo "   Run: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .env is not tracked"
fi

# Check 2: Verify no database files
echo "2. Checking for database files..."
if git ls-files | grep -qE "\.db$|\.sqlite"; then
    echo "   ❌ ERROR: Database files found in git!"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ No database files tracked"
fi

# Check 3: Verify no log files
echo "3. Checking for log files..."
if git ls-files | grep -qE "\.log$"; then
    echo "   ❌ ERROR: Log files found in git!"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ No log files tracked"
fi

# Check 4: Verify no model files
echo "4. Checking for model files..."
if git ls-files | grep -qE "\.gguf$|\.bin$"; then
    echo "   ⚠️  WARNING: Large model files found in git!"
    echo "   Consider using Git LFS or .gitignore"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ No model files tracked"
fi

# Check 5: Check for secrets in staged files
echo "5. Checking for potential secrets..."
if git diff --staged | grep -qiE "password.*=.*['\"][^'\"]{8,}|api_key.*=.*['\"][^'\"]{8,}|token.*=.*['\"][^'\"]{8,}"; then
    echo "   ⚠️  WARNING: Potential secrets found in staged changes!"
    echo "   Review with: git diff --staged | grep -iE \"password|api_key|token\""
else
    echo "   ✅ No obvious secrets detected"
fi

# Check 6: Verify .gitignore exists
echo "6. Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    echo "   ❌ ERROR: .gitignore missing!"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .gitignore exists"
fi

# Check 7: Verify .env.example exists
echo "7. Checking .env.example..."
if [ ! -f ".env.example" ]; then
    echo "   ⚠️  WARNING: .env.example missing - others won't know what config is needed"
else
    echo "   ✅ .env.example exists"
fi

echo ""
echo "----------------------------------------"

if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Safe to upload to GitHub."
    echo ""
    echo "Next steps:"
    echo "  git add ."
    echo "  git commit -m \"Initial commit: Restaurant AI with Phi-2\""
    echo "  git push origin main"
    exit 0
else
    echo "❌ Found $ERRORS issue(s). Please fix before uploading."
    echo ""
    echo "See SECURITY.md for more details."
    exit 1
fi
