#!/bin/bash

echo "🔧 Fixing all imports..."

# Fix tous les imports "from core." vers "from tachikoma.core."
find tachikoma/ -name "*.py" -type f -exec sed -i 's/^from core\./from tachikoma.core./g' {} +

# Fix tous les imports "from api." vers "from tachikoma.api."
find tachikoma/ -name "*.py" -type f -exec sed -i 's/^from api\./from tachikoma.api./g' {} +

# Fix tous les imports "from features." vers "from tachikoma.features."
find tachikoma/ -name "*.py" -type f -exec sed -i 's/^from features\./from tachikoma.features./g' {} +

# Fix aussi les imports "import core" (rare mais possible)
find tachikoma/ -name "*.py" -type f -exec sed -i 's/^import core$/import tachikoma.core/g' {} +

echo "✅ All imports fixed!"
echo ""
echo "📊 Summary:"
echo "- Fixed 'from core.' imports"
echo "- Fixed 'from api.' imports"  
echo "- Fixed 'from features.' imports"
echo ""
echo "🔍 Verification:"
grep -r "^from core\." tachikoma/ --include="*.py" | wc -l
grep -r "^from api\." tachikoma/ --include="*.py" | wc -l
grep -r "^from features\." tachikoma/ --include="*.py" | wc -l
