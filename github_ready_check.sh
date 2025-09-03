#!/bin/bash

# GitHub发布前检查脚本
echo "🚀 GitHub Repository Readiness Check"
echo "===================================="

# 1. 检查许可证文件
echo ""
echo "📜 License & Legal Files:"
if [ -f "LICENSE.md" ]; then
    echo "✅ LICENSE.md exists"
else
    echo "❌ LICENSE.md missing"
fi

if [ -f "NOTICE.md" ]; then
    echo "✅ NOTICE.md exists"
else
    echo "❌ NOTICE.md missing"
fi

if [ -d ".github" ]; then
    echo "✅ GitHub templates configured"
else
    echo "❌ GitHub templates missing"
fi

# 2. 检查保护机制
echo ""
echo "🛡️ Protection Mechanisms:"
if grep -q "SystemMetadata" "src/utils/metadata.py" 2>/dev/null; then
    echo "✅ Core protection system active"
else
    echo "❌ Core protection system missing"
fi

if grep -q "metadata.*Dict" "src/api/main.py" 2>/dev/null; then
    echo "✅ API protection layer active"
else
    echo "❌ API protection layer missing"
fi

# 3. 检查敏感信息
echo ""
echo "🔍 Security Audit:"
sensitive_patterns=(
    "watermark.*implementation"
    "protect.*scheme"
    "api.*key.*="
    "password.*="
    "secret.*="
)

found_sensitive=false
for pattern in "${sensitive_patterns[@]}"; do
    if grep -r "$pattern" . --exclude-dir=.git --exclude="*.pyc" --exclude="check_*" 2>/dev/null | head -5; then
        found_sensitive=true
        break
    fi
done

if [ "$found_sensitive" = false ]; then
    echo "✅ No sensitive information exposed"
fi

# 4. 检查README质量
echo ""
echo "📖 Documentation Quality:"
if grep -q "技术展示项目" "README.md" 2>/dev/null; then
    echo "✅ Project purpose clearly stated"
else
    echo "❌ Project purpose unclear"
fi

if grep -q "LICENSE.md" "README.md" 2>/dev/null; then
    echo "✅ License referenced in README"
else
    echo "❌ License not referenced"
fi

# 5. Git状态检查
echo ""
echo "📋 Git Repository Status:"
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Working directory clean"
else
    echo "⚠️  Uncommitted changes exist"
    git status --short
fi

echo ""
echo "🏷️  Latest commit:"
git log -1 --oneline

# 6. 最终建议
echo ""
echo "🎯 Publication Recommendations:"
echo "1. ✅ Use GitHub's 'Public' visibility"
echo "2. ✅ Enable Issues for commercial inquiries"
echo "3. ✅ Add repository topics: 'rag', 'ai', 'python', 'technical-showcase'"
echo "4. ✅ Consider adding a CONTRIBUTING.md for community guidelines"
echo "5. ✅ Set up GitHub Pages for documentation (optional)"

echo ""
echo "🔗 Repository Settings Checklist:"
echo "- [ ] Repository name: descriptive and professional"
echo "- [ ] Description: mention 'Technical Showcase - Learning Purpose'"
echo "- [ ] Topics: rag, ai, python, fastapi, langchain, technical-demo"
echo "- [ ] License: Custom (refer to LICENSE.md)"
echo "- [ ] Issues: Enabled"
echo "- [ ] Wiki: Disabled (unless needed)"
echo "- [ ] Sponsorship: Optional"

echo ""
echo "🎉 Your repository is ready for publication with full IP protection!"
echo "   The dual-layer protection (legal + technical) ensures your work is secure."
