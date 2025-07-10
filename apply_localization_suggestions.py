#!/usr/bin/env python3
"""
Apply Localization Suggestions Script
Automatically applies high-confidence localization suggestions to the codebase
"""

import json
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('apply_localization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalizationApplier:
    """Class to apply localization suggestions to the codebase"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.lib_path = self.project_root / 'lib'
        self.l10n_path = self.lib_path / 'l10n'
        self.backup_path = self.project_root / 'backup_before_localization'
        
        # Load existing localization data
        self.existing_en_keys = self.load_existing_arb_keys('app_en.arb')
        self.existing_ru_keys = self.load_existing_arb_keys('app_ru.arb')
        
        # Statistics
        self.files_modified = 0
        self.strings_localized = 0
        self.keys_added = 0
        
    def load_existing_arb_keys(self, filename: str) -> Set[str]:
        """Load existing keys from ARB file"""
        try:
            arb_path = self.l10n_path / filename
            if not arb_path.exists():
                return set()
                
            with open(arb_path, 'r', encoding='utf-8') as f:
                arb_data = json.load(f)
                
            keys = set()
            for key in arb_data.keys():
                if not key.startswith('@@') and not key.startswith('@'):
                    keys.add(key)
                    
            logger.info(f"Loaded {len(keys)} existing keys from {filename}")
            return keys
            
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return set()
    
    def create_backup(self):
        """Create backup of the project before making changes"""
        try:
            if self.backup_path.exists():
                shutil.rmtree(self.backup_path)
                
            logger.info("Creating backup of project...")
            shutil.copytree(self.lib_path, self.backup_path / 'lib')
            logger.info(f"Backup created at {self.backup_path}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def load_suggestions(self) -> Dict:
        """Load localization suggestions from JSON file"""
        try:
            suggestions_path = self.project_root / 'strings_to_localize.json'
            
            if not suggestions_path.exists():
                logger.error("strings_to_localize.json not found. Run localization_analyzer.py first.")
                return {}
                
            with open(suggestions_path, 'r', encoding='utf-8') as f:
                suggestions = json.load(f)
                
            logger.info(f"Loaded {len(suggestions)} localization suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error loading suggestions: {e}")
            return {}
    
    def filter_high_confidence_suggestions(self, suggestions: Dict, min_confidence: float = 0.8) -> Dict:
        """Filter suggestions by confidence level"""
        filtered = {}
        
        for key, data in suggestions.items():
            confidence = data.get('confidence', 0.0)
            widget_type = data.get('widget_type', '')
            value = data.get('value', '')
            
            # Apply filters
            if confidence < min_confidence:
                continue
                
            # Skip template variables and complex expressions
            if '${' in value or '$' in value:
                continue
                
            # Skip very short strings unless they're common UI elements
            if len(value.strip()) < 3 and widget_type not in ['button', 'label']:
                continue
                
            # Skip strings that are likely constants or technical terms
            if value.isupper() and ' ' not in value:
                continue
                
            # Skip if key already exists
            if key in self.existing_en_keys:
                continue
                
            filtered[key] = data
            
        logger.info(f"Filtered to {len(filtered)} high-confidence suggestions")
        return filtered
    
    def apply_localization_to_file(self, file_path: Path, suggestions: Dict) -> int:
        """Apply localization suggestions to a specific file"""
        try:
            if not file_path.exists():
                return 0
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            changes_made = 0
            
            # Get suggestions for this file
            file_suggestions = {}
            relative_path = str(file_path.relative_to(self.project_root)).replace('\\', '/')
            
            for key, data in suggestions.items():
                description = data.get('description', '')
                if relative_path in description:
                    file_suggestions[key] = data
            
            if not file_suggestions:
                return 0
                
            # Apply replacements
            for key, data in file_suggestions.items():
                value = data['value']
                confidence = data['confidence']
                
                # Create the replacement pattern
                # Handle different quote styles
                patterns = [
                    re.escape(f"'{value}'"),
                    re.escape(f'"{value}"'),
                    re.escape(f"const Text('{value}'"),
                    re.escape(f'const Text("{value}"'),
                    re.escape(f"Text('{value}'"),
                    re.escape(f'Text("{value}"'),
                ]
                
                replacement = f"AppLocalizations.of(context)?.{key} ?? '{value}'"
                
                for pattern in patterns:
                    if pattern in content:
                        # Be more specific about the replacement
                        if "const Text(" in pattern:
                            new_pattern = pattern.replace("const Text(", "Text(")
                            content = content.replace(pattern, new_pattern.replace(f"'{value}'", replacement).replace(f'"{value}"', replacement))
                        else:
                            content = content.replace(pattern, replacement)
                        
                        changes_made += 1
                        self.strings_localized += 1
                        break
            
            # Write back if changes were made
            if changes_made > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Applied {changes_made} localizations to {file_path}")
                self.files_modified += 1
                
            return changes_made
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return 0
    
    def add_keys_to_arb(self, suggestions: Dict):
        """Add new localization keys to ARB files"""
        try:
            # Add to English ARB
            en_arb_path = self.l10n_path / 'app_en.arb'
            self.add_keys_to_arb_file(en_arb_path, suggestions, 'en')
            
            # Add to Russian ARB (with placeholder values)
            ru_arb_path = self.l10n_path / 'app_ru.arb'
            self.add_keys_to_arb_file(ru_arb_path, suggestions, 'ru')
            
        except Exception as e:
            logger.error(f"Error adding keys to ARB files: {e}")
    
    def add_keys_to_arb_file(self, arb_path: Path, suggestions: Dict, locale: str):
        """Add keys to a specific ARB file"""
        try:
            # Load existing ARB data
            if arb_path.exists():
                with open(arb_path, 'r', encoding='utf-8') as f:
                    arb_data = json.load(f)
            else:
                arb_data = {"@@locale": locale}
            
            # Add new keys
            keys_added = 0
            for key, data in suggestions.items():
                if key not in arb_data:
                    value = data['value']
                    description = data.get('description', '')
                    
                    # For Russian, use placeholder
                    if locale == 'ru':
                        value = f"[RU] {value}"
                    
                    arb_data[key] = value
                    arb_data[f"@{key}"] = {
                        "description": f"Auto-generated from {description}"
                    }
                    
                    keys_added += 1
                    self.keys_added += 1
            
            # Write back
            if keys_added > 0:
                with open(arb_path, 'w', encoding='utf-8') as f:
                    json.dump(arb_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Added {keys_added} keys to {arb_path}")
                
        except Exception as e:
            logger.error(f"Error adding keys to {arb_path}: {e}")
    
    def apply_suggestions(self, min_confidence: float = 0.8, max_changes: int = 50):
        """Apply localization suggestions to the codebase"""
        logger.info("Starting localization application...")
        
        # Create backup
        self.create_backup()
        
        # Load suggestions
        suggestions = self.load_suggestions()
        if not suggestions:
            logger.error("No suggestions to apply")
            return
        
        # Filter high-confidence suggestions
        filtered_suggestions = self.filter_high_confidence_suggestions(suggestions, min_confidence)
        
        # Limit the number of changes for safety
        if len(filtered_suggestions) > max_changes:
            logger.warning(f"Limiting changes to {max_changes} for safety")
            filtered_suggestions = dict(list(filtered_suggestions.items())[:max_changes])
        
        # Apply localizations to files
        dart_files = list(self.lib_path.rglob('*.dart'))
        
        for dart_file in dart_files:
            try:
                changes = self.apply_localization_to_file(dart_file, filtered_suggestions)
                if changes > 0:
                    logger.info(f"Applied {changes} changes to {dart_file}")
            except Exception as e:
                logger.error(f"Error processing {dart_file}: {e}")
        
        # Add keys to ARB files
        self.add_keys_to_arb(filtered_suggestions)
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("LOCALIZATION APPLICATION SUMMARY")
        logger.info("="*50)
        logger.info(f"Files modified: {self.files_modified}")
        logger.info(f"Strings localized: {self.strings_localized}")
        logger.info(f"Keys added to ARB files: {self.keys_added}")
        logger.info(f"Backup created at: {self.backup_path}")
        logger.info("="*50)
    
    def restore_backup(self):
        """Restore from backup if something went wrong"""
        try:
            if not self.backup_path.exists():
                logger.error("No backup found to restore")
                return
                
            logger.info("Restoring from backup...")
            
            # Remove current lib directory
            if self.lib_path.exists():
                shutil.rmtree(self.lib_path)
            
            # Restore from backup
            shutil.copytree(self.backup_path / 'lib', self.lib_path)
            
            logger.info("Backup restored successfully")
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply localization suggestions')
    parser.add_argument('--confidence', type=float, default=0.8, 
                       help='Minimum confidence level (0.0-1.0)')
    parser.add_argument('--max-changes', type=int, default=50,
                       help='Maximum number of changes to apply')
    parser.add_argument('--restore', action='store_true',
                       help='Restore from backup')
    
    args = parser.parse_args()
    
    try:
        applier = LocalizationApplier()
        
        if args.restore:
            applier.restore_backup()
        else:
            applier.apply_suggestions(args.confidence, args.max_changes)
            
            print("\n🎉 Localization application completed!")
            print(f"📊 Summary: {applier.files_modified} files modified, {applier.strings_localized} strings localized")
            print(f"💾 Backup available at: {applier.backup_path}")
            print("\nNext steps:")
            print("1. Run 'flutter analyze' to check for issues")
            print("2. Update Russian translations in lib/l10n/app_ru.arb")
            print("3. Run 'flutter pub get' to regenerate localizations")
            print("4. Test the app thoroughly")
            print("\nIf anything goes wrong, run with --restore flag to restore backup")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"❌ Application failed: {e}")

if __name__ == "__main__":
    main() 