# SocWatch Post-Processor (socwatch_pp)

A simple Python tool for batch processing SocWatch .etl files using socwatch.exe.

## Features

- �️ **GUI Mode** - Easy folder selection with graphical interface
- 💻 **CLI Mode** - Command-line interface for automation/scripting
- �🔍 **Auto-discovery** of SocWatch versions from `D:\socwatch`
- 📁 **Recursive scanning** for .etl files in input folders
- 🎯 **Automated processing** using file prefixes as input parameters
- 📊 **Comprehensive reporting** of processing results
- ✅ **Simple single-file solution** - no external dependencies

## Requirements

- Python 3.6 or higher
- SocWatch installation(s) in `D:\socwatch` directory
- Windows environment (uses socwatch.exe)

## Installation

1. **Clone or download** the script:
   ```bash
   git clone <repository-url>
   cd socwatch_post_proc
   ```

2. **No additional dependencies** required - uses only Python standard library!

## Usage

### GUI Mode (Default)

Simply run without arguments to open folder selection dialog:

```bash
python socwatch_pp.py
```

This will:
1. 📂 Open a folder selection dialog
2. 🔍 Show SocWatch version selection dialog
3. 📊 Display progress in console
4. ✅ Show completion dialog with results

### CLI Mode

```bash
python socwatch_pp.py <input_folder>
```

### Examples

```bash
# GUI mode - opens folder selection dialog
python socwatch_pp.py

# CLI mode - process specified folder
python socwatch_pp.py C:\data\socwatch_traces

# CLI mode - process current directory
python socwatch_pp.py .

# Force CLI mode (useful for scripting)
python socwatch_pp.py --cli C:\data\socwatch_traces

# Show help
python socwatch_pp.py --help
```

## How It Works

1. **Version Selection**: The tool scans `D:\socwatch` for available socwatch.exe versions and lets you choose which one to use.

2. **File Discovery**: Recursively searches the input folder for all `.etl` files.

3. **Batch Processing**: For each .etl file found:
   - Extracts the file prefix (filename without .etl extension)
   - Runs: `socwatch.exe -i <prefix> -o <same_folder>`
   - Changes to the file's directory before processing

4. **Reporting**: Provides a comprehensive report showing:
   - Total files processed
   - Success/failure counts
   - Processing time
   - Details of any failures

## SocWatch Directory Structure

The tool expects SocWatch installations in this structure:

```
D:\socwatch\
├── version1\
│   └── socwatch.exe
├── version2\
│   └── socwatch.exe
└── socwatch.exe          # Also checks base directory
```

## GUI Interface

When running in GUI mode (`python socwatch_pp.py`), you'll see:

1. **📂 Folder Selection Dialog**: Browse and select the folder containing .etl files
2. **🔍 SocWatch Version Dialog**: Choose from available SocWatch installations  
3. **📊 Console Progress**: Real-time processing updates in the console window
4. **✅ Completion Dialog**: Summary of results with success/failure counts

The GUI makes it easy for non-technical users to process SocWatch files without needing to remember command-line syntax.

## Example Output

### CLI Mode Output:
```
🔧 SocWatch Post-Processor (socwatch_pp)
========================================
💻 CLI Mode: Using specified folder
📁 Input folder: C:\data\socwatch_traces

🔍 Available SocWatch versions:
  1. D:\socwatch\v2.1\socwatch.exe
  2. D:\socwatch\v2.2\socwatch.exe

Select version (1-2): 2
✅ Selected: D:\socwatch\v2.2\socwatch.exe

🔍 Found 5 .etl files

🚀 Starting batch processing of 5 files...
============================================================

[1/5] trace1.etl
📊 Processing: trace1.etl
   Command: D:\socwatch\v2.2\socwatch.exe -i trace1 -o C:\data\socwatch_traces
   ✅ Success

[2/5] subfolder\trace2.etl
📊 Processing: trace2.etl
   Command: D:\socwatch\v2.2\socwatch.exe -i trace2 -o C:\data\socwatch_traces\subfolder
   ✅ Success

============================================================
📋 FINAL PROCESSING REPORT
============================================================
📊 Total files processed: 5
✅ Successfully processed: 5
❌ Failed: 0
📈 Success rate: 100.0%
⏱️  Total time: 45.2 seconds
🔧 Used SocWatch: D:\socwatch\v2.2\socwatch.exe
✨ Processing complete!
```

## Error Handling

The tool handles various error conditions:

- **Missing SocWatch installations**: Clear error messages if no socwatch.exe found
- **Invalid input folders**: Validates folder existence before processing
- **Processing timeouts**: 5-minute timeout per file to prevent hanging
- **SocWatch errors**: Captures and reports socwatch.exe error output
- **File access issues**: Handles permission and path-related errors

## Troubleshooting

### Common Issues

1. **"No SocWatch installations found"**
   - Ensure socwatch.exe exists in `D:\socwatch` or its subdirectories
   - Check file permissions

2. **"Processing timeout"**
   - Some .etl files may be very large and take >5 minutes to process
   - The tool will skip these and continue with other files

3. **"Permission denied"**
   - Run the script with administrator privileges if needed
   - Check write permissions in output directories

### Debug Mode

For more detailed output, you can modify the script to add verbose logging by uncommenting debug print statements.

## Customization

The script can be easily customized:

- **Change SocWatch base directory**: Modify the `socwatch_base_dir` parameter
- **Adjust timeout**: Change the `timeout=300` parameter in `subprocess.run()`
- **Add more SocWatch arguments**: Extend the `cmd` list in `process_etl_file()`

## License

This project is open source and available under the MIT License.