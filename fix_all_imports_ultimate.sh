#!/bin/bash

echo "🔧 ULTIMATE import fix (catches indented imports)..."

# Fix TOUS les fichiers .py dans tachikoma/
for file in $(find tachikoma/ -name "*.py" -type f); do
    # Remplace TOUTES les occurrences (avec ou sans indentation)
    sed -i 's/\([ ]*\)from core\./\1from tachikoma.core./g' "$file"
    sed -i 's/\([ ]*\)from api\./\1from tachikoma.api./g' "$file"
    sed -i 's/\([ ]*\)from features\./\1from tachikoma.features./g' "$file"
    sed -i 's/\([ ]*\)import core\./\1import tachikoma.core./g' "$file"
done

echo "✅ All imports fixed (ultimate mode)!"
echo ""
echo "🔍 Final verification:"
echo "Remaining 'from core.' imports:"
grep -rn "from core\." tachikoma/ --include="*.py" | wc -l
echo "Remaining 'import core.' imports:"
grep -rn "import core\." tachikoma/ --include="*.py" | wc -l
echo ""
echo "Files with 'core' imports:"
grep -rn "from core\." tachikoma/ --include="*.py"
grep -rn "import core\." tachikoma/ --include="*.py"
