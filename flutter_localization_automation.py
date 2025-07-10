#!/usr/bin/env python3
"""
Flutter Localization Automation Tool

Automatically converts hardcoded English strings in Flutter apps to proper localization
using existing ARB translation files.

Author: Flutter Community
License: MIT
Version: 1.0.0
"""

import os
import re
import json
import glob
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set

class FlutterLocalizationAutomator:
    """Main class for automating Flutter localization"""
    
    def __init__(self, 
                 arb_dir: str = 'lib/l10n',
                 english_arb: str = 'app_en.arb',
                 target_arb: str = 'app_ru.arb',
                 source_dir: str = 'lib',
                 backup_enabled: bool = False,
                 verbose: bool = False):
        """
        Initialize the localization automator
        
        Args:
            arb_dir: Directory containing ARB files
            english_arb: Name of English ARB file
            target_arb: Name of target language ARB file  
            source_dir: Directory to scan for Dart files
            backup_enabled: Whether to create backups
            verbose: Enable verbose logging
        """
        self.arb_dir = arb_dir
        self.english_arb = english_arb
        self.target_arb = target_arb
        self.source_dir = source_dir
        self.backup_enabled = backup_enabled
        self.verbose = verbose
        
        # Setup logging
        self.setup_logging()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'strings_found': 0,
            'strings_localized': 0,
            'total_changes': 0
        }
        
        # Load translations
        self.english_translations = {}
        self.target_translations = {}
        self.load_translations()
        
    def setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('localization_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_translations(self):
        """Load English and target language translations from ARB files"""
        # Load English translations
        english_path = os.path.join(self.arb_dir, self.english_arb)
        if os.path.exists(english_path):
            try:
                with open(english_path, 'r', encoding='utf-8') as f:
                    self.english_translations = json.load(f)
                self.logger.info(f"Loaded {len(self.english_translations)} English translations")
            except Exception as e:
                self.logger.error(f"Error loading English ARB file: {e}")
                return False
        else:
            self.logger.error(f"English ARB file not found: {english_path}")
            return False
            
        # Load target language translations
        target_path = os.path.join(self.arb_dir, self.target_arb)
        if os.path.exists(target_path):
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    self.target_translations = json.load(f)
                self.logger.info(f"Loaded {len(self.target_translations)} target translations")
            except Exception as e:
                self.logger.error(f"Error loading target ARB file: {e}")
                return False
        else:
            self.logger.warning(f"Target ARB file not found: {target_path}")
            
        return True
        
    def create_english_to_key_mapping(self) -> Dict[str, str]:
        """Create mapping from English text to localization keys"""
        mapping = {}
        for key, value in self.english_translations.items():
            if isinstance(value, str) and not key.startswith('@'):
                # Clean the value for better matching
                clean_value = value.strip()
                if clean_value:
                    mapping[clean_value] = key
        return mapping
        
    def should_skip_string(self, text: str) -> bool:
        """Check if a string should be skipped (URLs, numbers, etc.)"""
        skip_patterns = [
            r'^https?://',  # URLs
            r'^\d+$',       # Pure numbers
            r'^[\d\s\-\+\(\)]+$',  # Phone numbers
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # Emails
            r'^\$\{.*\}$',  # Template variables
            r'^[A-Z_][A-Z0-9_]*$',  # Constants
            r'^[a-z][a-zA-Z0-9]*$',  # camelCase variables (single word)
        ]
        
        # Skip very short strings
        if len(text.strip()) < 2:
            return True
            
        # Skip strings that match skip patterns
        for pattern in skip_patterns:
            if re.match(pattern, text.strip()):
                return True
                
        return False
        
    def find_dart_files(self, max_files: int = None) -> List[str]:
        """Find all Dart files in the source directory"""
        pattern = os.path.join(self.source_dir, '**', '*.dart')
        dart_files = glob.glob(pattern, recursive=True)
        
        if max_files:
            dart_files = dart_files[:max_files]
            self.logger.info(f"Processing first {len(dart_files)} files only")
            
        return dart_files
        
    def extract_strings_from_file(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract hardcoded strings from a Dart file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return []
            
        strings_found = []
        
        # Regex patterns for finding strings
        patterns = [
            r"'([^'\\]*(?:\\.[^'\\]*)*)'",  # Single quoted strings
            r'"([^"\\]*(?:\\.[^"\\]*)*)"',  # Double quoted strings
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                text = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                # Skip if already localized
                if 'AppLocalizations.of(context)' in content[max(0, match.start()-100):match.start()]:
                    continue
                    
                # Skip unwanted strings
                if self.should_skip_string(text):
                    continue
                    
                strings_found.append((text, line_num))
                
        return strings_found
        
    def apply_localization_to_file(self, file_path: str, dry_run: bool = False) -> int:
        """Apply localization to a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return 0
            
        original_content = content
        english_to_key = self.create_english_to_key_mapping()
        changes = 0
        
        # Find and replace strings
        for english_text, key in english_to_key.items():
            # Create regex pattern for the exact string
            escaped_text = re.escape(english_text)
            patterns = [
                rf"'({escaped_text})'",
                rf'"({escaped_text})"',
            ]
            
            for pattern in patterns:
                def replace_func(match):
                    nonlocal changes
                    quote = match.group(0)[0]  # Get the quote type
                    replacement = f"AppLocalizations.of(context)?.{key} ?? {quote}{english_text}{quote}"
                    changes += 1
                    self.logger.debug(f"Localized '{english_text}' -> '{key}' in {file_path}")
                    return replacement
                    
                # Check if this string appears in the file and isn't already localized
                if re.search(pattern, content):
                    # Make sure it's not already localized
                    lines = content.split('\n')
                    new_lines = []
                    
                    for line in lines:
                        if re.search(pattern, line) and 'AppLocalizations.of(context)' not in line:
                            line = re.sub(pattern, replace_func, line)
                        new_lines.append(line)
                        
                    content = '\n'.join(new_lines)
        
        # Write back if changes were made and not dry run
        if changes > 0 and not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"Modified {file_path} with {changes} localizations")
            except Exception as e:
                self.logger.error(f"Error writing to {file_path}: {e}")
                return 0
        elif changes > 0 and dry_run:
            self.logger.info(f"[DRY RUN] Would modify {file_path} with {changes} localizations")
            
        return changes
        
    def run_localization(self, max_files: int = None, dry_run: bool = False):
        """Run the complete localization process"""
        self.logger.info("Starting Flutter localization automation...")
        
        if not self.english_translations:
            self.logger.error("No English translations loaded. Cannot proceed.")
            return
            
        # Find all Dart files
        dart_files = self.find_dart_files(max_files)
        self.logger.info(f"Found {len(dart_files)} Dart files to process")
        
        # Process each file
        for file_path in dart_files:
            self.stats['files_processed'] += 1
            changes = self.apply_localization_to_file(file_path, dry_run)
            
            if changes > 0:
                self.stats['files_modified'] += 1
                self.stats['total_changes'] += changes
                
        # Print summary
        self.print_summary(dry_run)
        
    def print_summary(self, dry_run: bool = False):
        """Print localization summary"""
        prefix = "[DRY RUN] " if dry_run else ""
        self.logger.info(f"\n{prefix}Localization Summary:")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files modified: {self.stats['files_modified']}")
        self.logger.info(f"Total changes: {self.stats['total_changes']}")
        self.logger.info(f"English translations available: {len(self.english_translations)}")
        self.logger.info(f"Target translations available: {len(self.target_translations)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Flutter Localization Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flutter_localization_automation.py --max-files 5
  python flutter_localization_automation.py --dry-run
  python flutter_localization_automation.py --arb-dir lib/i18n --english-arb en.arb
        """
    )
    
    parser.add_argument('--max-files', type=int, 
                       help='Limit number of files to process (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--arb-dir', default='lib/l10n',
                       help='Directory containing ARB files (default: lib/l10n)')
    parser.add_argument('--english-arb', default='app_en.arb',
                       help='English ARB file name (default: app_en.arb)')
    parser.add_argument('--target-arb', default='app_ru.arb',
                       help='Target language ARB file name (default: app_ru.arb)')
    parser.add_argument('--source-dir', default='lib',
                       help='Directory to scan for Dart files (default: lib)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Disable backup creation')
    
    args = parser.parse_args()
    
    # Create automator instance
    automator = FlutterLocalizationAutomator(
        arb_dir=args.arb_dir,
        english_arb=args.english_arb,
        target_arb=args.target_arb,
        source_dir=args.source_dir,
        backup_enabled=not args.no_backup,
        verbose=args.verbose
    )
    
    # Run localization
    automator.run_localization(
        max_files=args.max_files,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main() 