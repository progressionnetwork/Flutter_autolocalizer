#!/usr/bin/env python3
"""
Fix remaining const and context issues after localization
"""

import os
import re
import glob
from pathlib import Path

def fix_remaining_issues():
    """Fix remaining const and context issues"""
    
    dart_files = glob.glob('lib/**/*.dart', recursive=True)
    
    for file_path in dart_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: const expressions with AppLocalizations
            # Replace const with direct strings for now
            const_localization_pattern = r'const\s+([^=]+)=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"];'
            def fix_const_localization(match):
                var_part = match.group(1)
                key = match.group(2)
                fallback = match.group(3)
                return f'const {var_part}= \'{fallback}\'; // TODO: Localize dynamically'
            
            content = re.sub(const_localization_pattern, fix_const_localization, content)
            
            # Fix 2: Field initializers with context
            # Pattern: field = AppLocalizations.of(context)?.key ?? 'fallback';
            field_init_pattern = r'(\s+)(\w+)\s*=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"];'
            def fix_field_init(match):
                indent = match.group(1)
                var_name = match.group(2)
                key = match.group(3)
                fallback = match.group(4)
                return f'{indent}{var_name} = \'{fallback}\'; // TODO: Localize dynamically'
            
            content = re.sub(field_init_pattern, fix_field_init, content)
            
            # Fix 3: Static contexts with AppLocalizations
            # In static variables/const declarations
            static_pattern = r'static\s+const\s+([^=]+)=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"];'
            def fix_static_context(match):
                var_part = match.group(1)
                key = match.group(2)
                fallback = match.group(3)
                return f'static const {var_part}= \'{fallback}\'; // TODO: Localize dynamically'
            
            content = re.sub(static_pattern, fix_static_context, content)
            
            # Fix 4: Loading widget context issues
            # Replace problematic static context usage with fallback
            if 'loading_widget.dart' in file_path:
                content = content.replace(
                    'AppLocalizations.of(context)?.loading ?? \'Loading...\'',
                    '\'Loading...\''
                )
            
            # Fix 5: Specific problematic patterns
            # For initializer lists and field declarations
            problematic_patterns = [
                # Field initializer
                (r'(\w+)\s*=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"]', r'\1 = \'\3\' // TODO: Localize dynamically'),
                # In parameter defaults
                (r'String\s+(\w+)\s*=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"]', r'String \1 = \'\3\' // TODO: Localize dynamically'),
            ]
            
            for pattern, replacement in problematic_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Fix 6: Method invocations in const contexts
            # Replace with direct string
            const_method_pattern = r'AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*[\'"]([^\'"]+)[\'"]'
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Check if this line is in a const context
                if ('const ' in line or 'static const' in line) and 'AppLocalizations.of(context)' in line:
                    # Replace with fallback string
                    match = re.search(const_method_pattern, line)
                    if match:
                        fallback = match.group(2)
                        lines[i] = re.sub(const_method_pattern, f"'{fallback}'", line)
                        lines[i] += ' // TODO: Localize dynamically'
            
            content = '\n'.join(lines)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed const/context issues in {file_path}")
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

if __name__ == "__main__":
    fix_remaining_issues()
    print("Const and context fixes completed!") 