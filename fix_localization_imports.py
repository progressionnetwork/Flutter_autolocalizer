#!/usr/bin/env python3
"""
Fix localization imports and context issues after applying localization
"""

import os
import re
import glob
from pathlib import Path

def fix_imports_and_context():
    """Fix missing imports and context issues in localized files"""
    
    # Files that need AppLocalizations import
    dart_files = glob.glob('lib/**/*.dart', recursive=True)
    
    for file_path in dart_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file uses AppLocalizations but doesn't import it
            if 'AppLocalizations.of(context)' in content:
                # Check if already imported
                if "import '../l10n/app_localizations.dart';" not in content and \
                   "import '../../l10n/app_localizations.dart';" not in content and \
                   "import 'package:lifecopilot/l10n/app_localizations.dart';" not in content:
                    
                    # Determine correct import path based on file location
                    file_dir = os.path.dirname(file_path)
                    relative_depth = file_dir.count(os.sep) - 1  # lib = 0, lib/screens = 1, lib/widgets = 1
                    
                    if relative_depth == 1:
                        import_line = "import '../l10n/app_localizations.dart';"
                    elif relative_depth == 2:
                        import_line = "import '../../l10n/app_localizations.dart';"
                    else:
                        import_line = "import '../l10n/app_localizations.dart';"
                    
                    # Add import after existing imports
                    import_pattern = r"(import\s+[^;]+;)\s*\n"
                    matches = list(re.finditer(import_pattern, content))
                    
                    if matches:
                        last_import_end = matches[-1].end()
                        content = content[:last_import_end] + import_line + '\n' + content[last_import_end:]
                    else:
                        # No imports found, add at the top
                        content = import_line + '\n' + content
            
            # Fix context issues in const constructors and static contexts
            # Pattern: const variables using AppLocalizations
            const_pattern = r'const\s+(\w+)\s*=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"];'
            
            def fix_const_usage(match):
                var_name = match.group(1)
                key = match.group(2)
                fallback = match.group(3)
                # Convert to a getter or regular variable
                return f'// const {var_name} = \'{fallback}\'; // TODO: Make this dynamic'
            
            content = re.sub(const_pattern, fix_const_usage, content)
            
            # Fix field initializers using AppLocalizations
            field_pattern = r'(\w+)\s*=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"];'
            
            def fix_field_usage(match):
                var_name = match.group(1)
                key = match.group(2)
                fallback = match.group(3)
                # Keep as fallback for now
                return f'{var_name} = \'{fallback}\'; // TODO: Localize dynamically'
            
            # Only replace if it's in a class field context (not in method bodies)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'AppLocalizations.of(context)' in line and ('=' in line) and not line.strip().startswith('return'):
                    # Check if this is a field initializer (not in a method)
                    indent = len(line) - len(line.lstrip())
                    if indent <= 4:  # Likely a field
                        match = re.search(field_pattern, line)
                        if match:
                            lines[i] = re.sub(field_pattern, fix_field_usage, line)
            
            content = '\n'.join(lines)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed imports and context issues in {file_path}")
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

if __name__ == "__main__":
    fix_imports_and_context()
    print("Import and context fixes completed!") 