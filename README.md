# Flutter_autolocalizer
A powerful Python tool that automatically converts hardcoded English strings in your Flutter app to proper localization using existing ARB translation files

# Flutter Localization Automation Tool

🚀 **Automate Flutter app localization in minutes, not weeks!** 

A powerful Python tool that automatically converts hardcoded English strings in your Flutter app to proper localization using existing ARB translation files.

## ✨ Features

- 🔍 **Smart String Detection**: Finds hardcoded English strings across your entire Flutter project
- 🎯 **Automatic Localization**: Wraps strings with `AppLocalizations.of(context)?.key ?? 'fallback'`
- 📁 **Bulk Processing**: Processes hundreds of files simultaneously
- 🛠️ **Import Management**: Automatically adds missing localization imports
- 🔧 **Context Fixing**: Resolves const and context compilation issues
- 📊 **Detailed Reporting**: Comprehensive logs and statistics
- ⚡ **Fast & Efficient**: Processes large codebases in minutes

## 🎯 Results

In a real-world project, this tool:
- ✅ **Localized 1,803 strings** across 339 files
- ✅ **Modified 169 files** with proper localization
- ✅ **Reduced manual work** from weeks to minutes
- ✅ **Maintained code integrity** with comprehensive error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Flutter project with existing ARB files
- English (`app_en.arb`) and target language ARB files

### Installation

1. Clone this repository:
```bash
git clone https://github.com/YourUsername/flutter-localization-automation.git
cd flutter-localization-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Place the scripts** in your Flutter project root directory
2. **Ensure your ARB files** are in `lib/l10n/` directory
3. **Run the main localization script**:

```bash
# Process first 5 files (testing)
python localize_existing_strings.py --max-files 5

# Process entire project
python localize_existing_strings.py
```

4. **Fix any import issues**:
```bash
python fix_localization_imports.py
```

5. **Fix const context issues**:
```bash
python fix_const_context_issues.py
python fix_final_const_issues.py
```

6. **Run Flutter analyze** to check results:
```bash
flutter analyze
```

## 📋 Command Line Options

```bash
python localize_existing_strings.py [OPTIONS]

Options:
  --max-files INTEGER    Limit number of files to process (for testing)
  --dry-run             Show what would be changed without making changes
  --verbose             Enable detailed logging
  --help               Show help message
```

## 📁 Project Structure Requirements

Your Flutter project should have this structure:
```
your_flutter_project/
├── lib/
│   ├── l10n/
│   │   ├── app_en.arb          # English translations (required)
│   │   ├── app_ru.arb          # Target language translations
│   │   └── app_localizations.dart
│   ├── screens/
│   ├── widgets/
│   └── ... (other dart files)
└── localization scripts here
```

## 🎛️ Configuration

### ARB File Format

Your `app_en.arb` should contain English strings:
```json
{
  "appTitle": "MyApp",
  "welcome": "Welcome",
  "save": "Save",
  "cancel": "Cancel"
}
```

Your target language ARB (e.g., `app_ru.arb`):
```json
{
  "appTitle": "МоеПриложение",
  "welcome": "Добро пожаловать", 
  "save": "Сохранить",
  "cancel": "Отмена"
}
```

### Customization

Edit the script constants to match your project:

```python
# In localize_existing_strings.py
ARB_DIR = 'lib/l10n'  # Your ARB files directory
ENGLISH_ARB = 'app_en.arb'  # Your English ARB file
TARGET_ARB = 'app_ru.arb'   # Your target language ARB file
```

## 🔧 How It Works

### 1. String Detection
- Scans all `.dart` files in your project
- Uses smart regex patterns to find English strings
- Filters out URLs, numbers, constants, and template variables
- Matches strings against your English ARB file

### 2. Localization Application  
- Wraps found strings with `AppLocalizations.of(context)?.key ?? 'original_string'`
- Preserves original strings as fallbacks
- Maintains code formatting and structure

### 3. Import Management
- Automatically adds missing `AppLocalizations` imports
- Updates import paths relative to file location
- Handles different project structures

### 4. Error Fixing
- Resolves const context compilation issues
- Fixes field initializer problems
- Handles static context errors

## 📊 Output Files

The tool generates several useful files:

- `localization_analysis_report.txt` - Detailed analysis of all changes
- `strings_to_localize.json` - List of strings that were localized
- `localization_suggestions.dart` - Code suggestions for manual review

## ⚠️ Important Notes

### Before Running
1. **Backup your project** - Always commit your changes first
2. **Test on a subset** - Use `--max-files 5` for initial testing
3. **Review ARB files** - Ensure your English ARB contains the strings you want to localize

### After Running
1. **Run `flutter analyze`** - Check for compilation errors
2. **Test your app** - Verify localizations work correctly
3. **Manual cleanup** - Some complex strings may need manual adjustment

### Limitations
- Works best with simple string literals
- Complex string interpolations may need manual review
- Const contexts might require additional fixes
- Generated code should be reviewed before production

## 🛠️ Troubleshooting

### Common Issues

**"No strings found"**
- Check your ARB file paths
- Verify English ARB contains the strings in your code
- Ensure strings are properly quoted in Dart files

**Compilation errors after running**
- Run the fix scripts: `fix_localization_imports.py`, `fix_const_context_issues.py`
- Check for unterminated strings in the error output
- Some complex cases may need manual fixing

**Import errors**
- Verify your `app_localizations.dart` path
- Check that localization is properly set up in your app

### Getting Help

1. Check the generated log files for detailed error information
2. Run with `--verbose` flag for more detailed output
3. Open an issue on GitHub with your error logs

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for efficient Flutter localization
- Built for the Flutter community
- Tested on real-world projects with thousands of strings

## 📈 Roadmap

- [ ] Support for additional ARB file formats
- [ ] GUI interface for easier use
- [ ] Integration with popular IDEs
- [ ] Support for pluralization rules
- [ ] Batch processing of multiple projects

---

**Made with ❤️ for the Flutter community**

If this tool helped you, please ⭐ star the repository and share it with other developers!
