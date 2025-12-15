# SocWatch Post-Processor (socwatch_pp)

A simple Python tool for batch processing SocWatch .etl files using socwatch.exe.

## Features

- 🖥️ **GUI Mode** - Easy folder selection with graphical interface
- 💻 **CLI Mode** - Command-line interface for automation/scripting
- 🔍 **Auto-discovery** of SocWatch installations with flexible directory support
- 📁 **Recursive scanning** for .etl files in input folders
- 🎯 **Automated processing** using file prefixes as input parameters
- 📊 **Comprehensive reporting** of processing results
- ✅ **Simple single-file solution** - no external dependencies
- 🛠️ **Flexible SocWatch location** - supports custom installation paths

## Requirements

- Python 3.6 or higher
- SocWatch installation (auto-detected or manually specified)
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
# GUI mode - select folder using dialog
python socwatch_pp.py

# CLI mode - use specified folder
python socwatch_pp.py C:\data\socwatch_traces

# CLI mode - process current directory
python socwatch_pp.py .

# Force CLI mode (useful for scripting)
python socwatch_pp.py --cli C:\data\socwatch_traces

# Use custom SocWatch installation directory
python socwatch_pp.py --socwatch-dir D:\MySocWatch C:\data\traces

# Use custom output directory (saves results to different location)
python socwatch_pp.py -o D:\results C:\data\traces
python socwatch_pp.py --output-dir D:\results C:\data\traces

# Combine options (CLI mode with custom SocWatch directory and output)
python socwatch_pp.py --cli --socwatch-dir C:\Intel\SocWatch -o D:\results C:\data\traces

# Show help
python socwatch_pp.py --help
```

## How It Works

1. **SocWatch Discovery**: The tool automatically locates SocWatch installations using:
   - Explicit `--socwatch-dir` argument
   - `SOCWATCH_DIR` environment variable  
   - Auto-detection in common locations (D:\socwatch, C:\Intel\SocWatch, etc.)
   - Fallback to default D:\socwatch

2. **Version Selection**: Scans the SocWatch directory for available socwatch.exe versions and lets you choose which one to use.

3. **File Discovery**: Recursively searches the input folder for all `.etl` files.

4. **Smart Skip Detection**: Before processing, checks if output already exists:
   - Looks for `{workload_name}.csv` summary file
   - Looks for `{workload_name}_WakeupAnalysis.csv` file
   - Skips already-processed collections to save time

5. **Batch Processing**: For each .etl file found:
   - Extracts the file prefix (filename without .etl extension)
   - Skips if already processed (summary or wakeup analysis files exist)
   - Runs: `socwatch.exe -i <prefix> -o <output_folder>`
   - Changes to the file's directory before processing

6. **Reporting**: Provides a comprehensive report showing:
   - Total files processed
   - Success/failure counts
   - Processing time
   - Details of any failures

## Configuration

### Output Directory

By default, processed results are saved in the same directory as the input .etl files. You can specify a custom output directory:

```bash
# Using shorthand -o option
python socwatch_pp.py -o D:\results C:\data\traces

# Using full --output-dir option
python socwatch_pp.py --output-dir D:\results C:\data\traces
```

When using a custom output directory:
- Results are organized with unique collection identifiers
- The tool creates subdirectories to prevent name conflicts
- Already-processed collections are automatically skipped

### SocWatch Installation Path

The tool supports multiple ways to specify your SocWatch installation location:

1. **Command-line argument** (highest priority):
   ```bash
   python socwatch_pp.py --socwatch-dir "C:\Intel\SocWatch" C:\data\traces
   ```

2. **Environment variable**:
   ```bash
   # Windows (PowerShell)
   $env:SOCWATCH_DIR="C:\Intel\SocWatch"
   python socwatch_pp.py C:\data\traces
   
   # Windows (Command Prompt)
   set SOCWATCH_DIR=C:\Intel\SocWatch
   python socwatch_pp.py C:\data\traces
   ```

3. **Auto-detection**: The tool will automatically search these common locations:
   - `D:\socwatch`
   - `C:\socwatch`
   - `D:\SocWatch`
   - `C:\SocWatch`
   - `D:\Intel\SocWatch`
   - `C:\Intel\SocWatch`
   - `C:\Program Files\Intel\SocWatch`
   - `C:\Program Files (x86)\Intel\SocWatch`

4. **Default fallback**: Falls back to `D:\socwatch` if no installation is found

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
- **Processing timeouts**: 30-minute timeout per file to prevent hanging
- **SocWatch errors**: Captures and reports socwatch.exe error output
- **File access issues**: Handles permission and path-related errors

## Troubleshooting

### Common Issues

1. **"No SocWatch installations found"**
   - Ensure socwatch.exe exists in `C:\socwatch` or use `--socwatch-dir` to specify location
   - Check file permissions

2. **"Processing timeout"**
   - Some .etl files may be very large and take >30 minutes to process
   - The tool will skip these and continue with other files

3. **"Permission denied"**
   - Run the script with administrator privileges if needed
   - Check write permissions in output directories

### Debug Mode

For more detailed output, you can modify the script to add verbose logging by uncommenting debug print statements.

## Customization

The script can be easily customized:

- **Change SocWatch base directory**: Use `--socwatch-dir` argument or set `SOCWATCH_DIR` environment variable
- **Adjust timeout**: Change the `timeout=1800` parameter in `subprocess.run()` (default: 30 minutes)
- **Add more SocWatch arguments**: Extend the `cmd` list in `process_collection()`

## License

This project is open source and available under the MIT License.