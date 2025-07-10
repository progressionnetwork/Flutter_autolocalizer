#!/usr/bin/env python3
"""
Flutter Localization Issues Fix Tool

Fixes common issues that occur after applying localization:
- Missing AppLocalizations imports
- Const context issues
- Field initializer problems
- Static context errors

Author: Flutter Community
License: MIT
Version: 1.0.0
"""

import os
import re
import glob
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple


class LocalizationIssuesFixer:
    """Fixes common issues after localization"""
    
    def __init__(self, source_dir: str = 'lib', verbose: bool = False):
        self.source_dir = source_dir
        self.verbose = verbose
        self.setup_logging()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'imports_fixed': 0,
            'const_issues_fixed': 0,
            'context_issues_fixed': 0,
            'total_fixes': 0
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('localization_fixes.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def find_dart_files(self) -> List[str]:
        """Find all Dart files in the source directory"""
        pattern = os.path.join(self.source_dir, '**', '*.dart')
        return glob.glob(pattern, recursive=True)
        
    def calculate_import_path(self, file_path: str) -> str:
        """Calculate the relative import path for app_localizations.dart"""
        # Calculate depth from lib directory
        lib_index = file_path.replace('\\', '/').find('lib/')
        if lib_index == -1:
            return '../l10n/app_localizations.dart'
            
        # Count directory depth after lib/
        path_after_lib = file_path[lib_index + 4:]  # Remove 'lib/' part
        depth = path_after_lib.count('/')
        
        # Build relative path
        relative_path = '../' * depth + 'l10n/app_localizations.dart'
        return relative_path
        
    def fix_missing_imports(self, file_path: str) -> int:
        """Fix missing AppLocalizations imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return 0
            
        # Check if file uses AppLocalizations but doesn't import it
        if 'AppLocalizations.of(context)' not in content:
            return 0
            
        # Check if already imported
        if ("import '../l10n/app_localizations.dart'" in content or
            "import '../../l10n/app_localizations.dart'" in content or
            "import '../../../l10n/app_localizations.dart'" in content or
            "import '../../../../l10n/app_localizations.dart'" in content):
            return 0
            
        # Find import section
        lines = content.split('\n')
        import_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                import_index = i
                
        if import_index == -1:
            # No imports found, add after any copyright/comments
            import_index = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('//'):
                    import_index = i
                    break
                    
        # Calculate correct import path
        import_path = self.calculate_import_path(file_path)
        import_statement = f"import '{import_path}';"
        
        # Insert import
        lines.insert(import_index + 1, import_statement)
        
        # Write back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            self.logger.debug(f"Added import to {file_path}")
            return 1
        except Exception as e:
            self.logger.error(f"Error writing to {file_path}: {e}")
            return 0
            
    def fix_const_issues(self, file_path: str) -> int:
        """Fix const context issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return 0
            
        original_content = content
        fixes = 0
        
        # Fix const expressions with AppLocalizations
        const_patterns = [
            # const Text(AppLocalizations.of(context)?.key ?? 'fallback')
            (r'const\s+Text\s*\(\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*([\'"][^\'"]*[\'"])\s*\)',
             r'const Text(\2)'),
            
            # const declarations
            (r'const\s+([^=]+)=\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*([\'"][^\'"]*[\'"])\s*;',
             r'const \1= \3;'),
             
            # const constructors
            (r'const\s+(\w+)\s*\([^)]*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*([\'"][^\'"]*[\'"])[^)]*\)',
             lambda m: m.group(0).replace(f'AppLocalizations.of(context)?.{m.group(2)} ?? {m.group(3)}', m.group(3)))
        ]
        
        for pattern, replacement in const_patterns:
            if callable(replacement):
                # Custom replacement function
                def replace_func(match):
                    nonlocal fixes
                    fixes += 1
                    return replacement(match)
                content = re.sub(pattern, replace_func, content)
            else:
                # Simple string replacement
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    fixes += len(re.findall(pattern, content))
                    content = new_content
                    
        # Fix field initializers
        field_patterns = [
            # Remove AppLocalizations from field initializers
            (r'(\w+)\s*:\s*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*([\'"][^\'"]*[\'"])',
             r'\1: \3'),
        ]
        
        for pattern, replacement in field_patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                fixes += len(re.findall(pattern, content))
                content = new_content
                
        # Write back if changes were made
        if fixes > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.debug(f"Fixed {fixes} const issues in {file_path}")
            except Exception as e:
                self.logger.error(f"Error writing to {file_path}: {e}")
                return 0
                
        return fixes
        
    def fix_context_issues(self, file_path: str) -> int:
        """Fix context-related issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return 0
            
        original_content = content
        fixes = 0
        
        # Fix static context issues
        static_patterns = [
            # Static methods trying to use context
            (r'static\s+[^{]*\{[^}]*AppLocalizations\.of\(context\)\?\.(\w+)\s*\?\?\s*([\'"][^\'"]*[\'"])[^}]*\}',
             lambda m: m.group(0).replace(f'AppLocalizations.of(context)?.{m.group(1)} ?? {m.group(2)}', m.group(2)))
        ]
        
        for pattern, replacement in static_patterns:
            if callable(replacement):
                def replace_func(match):
                    nonlocal fixes
                    fixes += 1
                    return replacement(match)
                content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
            else:
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                if new_content != content:
                    fixes += len(re.findall(pattern, content, flags=re.DOTALL))
                    content = new_content
                    
        # Write back if changes were made
        if fixes > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.debug(f"Fixed {fixes} context issues in {file_path}")
            except Exception as e:
                self.logger.error(f"Error writing to {file_path}: {e}")
                return 0
                
        return fixes
        
    def fix_all_issues(self, fix_imports: bool = True, fix_const: bool = True, fix_context: bool = True):
        """Fix all localization issues"""
        self.logger.info("Starting localization issues fix...")
        
        dart_files = self.find_dart_files()
        self.logger.info(f"Found {len(dart_files)} Dart files to process")
        
        for file_path in dart_files:
            self.stats['files_processed'] += 1
            
            # Fix imports
            if fix_imports:
                imports_fixed = self.fix_missing_imports(file_path)
                self.stats['imports_fixed'] += imports_fixed
                self.stats['total_fixes'] += imports_fixed
                
            # Fix const issues
            if fix_const:
                const_fixes = self.fix_const_issues(file_path)
                self.stats['const_issues_fixed'] += const_fixes
                self.stats['total_fixes'] += const_fixes
                
            # Fix context issues
            if fix_context:
                context_fixes = self.fix_context_issues(file_path)
                self.stats['context_issues_fixed'] += context_fixes
                self.stats['total_fixes'] += context_fixes
                
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print fix summary"""
        self.logger.info("\nLocalization Issues Fix Summary:")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Import issues fixed: {self.stats['imports_fixed']}")
        self.logger.info(f"Const issues fixed: {self.stats['const_issues_fixed']}")
        self.logger.info(f"Context issues fixed: {self.stats['context_issues_fixed']}")
        self.logger.info(f"Total fixes applied: {self.stats['total_fixes']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Flutter Localization Issues Fix Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fix_localization_issues.py
  python fix_localization_issues.py --no-imports
  python fix_localization_issues.py --source-dir lib/custom
        """
    )
    
    parser.add_argument('--source-dir', default='lib',
                       help='Directory to scan for Dart files (default: lib)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--no-imports', action='store_true',
                       help='Skip fixing import issues')
    parser.add_argument('--no-const', action='store_true',
                       help='Skip fixing const issues')
    parser.add_argument('--no-context', action='store_true',
                       help='Skip fixing context issues')
    
    args = parser.parse_args()
    
    # Create fixer instance
    fixer = LocalizationIssuesFixer(
        source_dir=args.source_dir,
        verbose=args.verbose
    )
    
    # Fix issues
    fixer.fix_all_issues(
        fix_imports=not args.no_imports,
        fix_const=not args.no_const,
        fix_context=not args.no_context
    )


if __name__ == "__main__":
    main() 