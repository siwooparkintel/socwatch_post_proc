#!/usr/bin/env python3
"""
SocWatch Post-Processor (socwatch_pp)

A simple tool to batch process SocWatch .etl files using socwatch.exe.

Features:
- User-selectable SocWatch.exe versions from D:\socwatch
- Recursive folder scanning for .etl files (SocWatch 3 or 4)
- Automatic processing with file prefix as input parameter
- Output to same folder as source files
- Comprehensive processing report

Usage:
    python socwatch_pp.py <input_folder>
"""

import os
import sys
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple, Dict
import time
import tkinter as tk
from tkinter import filedialog, messagebox


class SocWatchProcessor:
    """Main class for SocWatch post-processing operations."""
    
    def __init__(self, socwatch_base_dir: str = r"D:\socwatch", use_gui: bool = True):
        """
        Initialize SocWatch processor.
        
        Args:
            socwatch_base_dir: Base directory containing SocWatch versions
            use_gui: Whether to use GUI for folder selection and dialogs
        """
        self.socwatch_base_dir = Path(socwatch_base_dir)
        self.available_versions = []
        self.selected_version = None
        self.processed_files = []
        self.failed_files = []
        self.start_time = None
        self.use_gui = use_gui
        self.root = None
        
    def discover_socwatch_versions(self) -> List[Path]:
        """
        Discover available SocWatch versions in the base directory.
        
        Returns:
            List of paths to socwatch.exe files
        """
        versions = []
        if not self.socwatch_base_dir.exists():
            print(f"❌ SocWatch base directory not found: {self.socwatch_base_dir}")
            return versions
            
        # Look for socwatch.exe in subdirectories
        for item in self.socwatch_base_dir.iterdir():
            if item.is_dir():
                socwatch_exe = item / "socwatch.exe"
                if socwatch_exe.exists():
                    versions.append(socwatch_exe)
                    
        # Also check the base directory itself
        base_socwatch = self.socwatch_base_dir / "socwatch.exe"
        if base_socwatch.exists():
            versions.append(base_socwatch)
            
        self.available_versions = sorted(versions)
        return self.available_versions
    
    def select_folder_gui(self) -> Path:
        """
        Show GUI folder selection dialog.
        
        Returns:
            Selected folder path, or None if cancelled
        """
        if not self.use_gui:
            return None
            
        # Create root window if it doesn't exist
        if not self.root:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
            
        # Show folder selection dialog
        folder_path = filedialog.askdirectory(
            title="Select folder containing SocWatch .etl files",
            mustexist=True
        )
        
        if folder_path:
            return Path(folder_path)
        else:
            return None
    
    def select_socwatch_version(self) -> bool:
        """
        Present available SocWatch versions to user for selection.
        Uses GUI if enabled, otherwise command line.
        
        Returns:
            True if version selected, False otherwise
        """
        print(f"🔧 Discovering SocWatch versions (GUI mode: {self.use_gui})...")
        versions = self.discover_socwatch_versions()
        
        if not versions:
            error_msg = f"No SocWatch installations found!\nPlease ensure socwatch.exe exists in or under: {self.socwatch_base_dir}"
            if self.use_gui:
                if not self.root:
                    self.root = tk.Tk()
                    self.root.withdraw()
                messagebox.showerror("SocWatch Not Found", error_msg)
            else:
                print("❌ " + error_msg.replace('\n', '\n   '))
            return False
        
        print(f"🔍 Found {len(versions)} SocWatch version(s)")
        
        # Always use console selection for now - GUI dialogs are having issues
        print("📝 Using console selection for SocWatch version...")
        return self._select_version_console(versions)
    
    def _select_version_gui(self, versions: List[Path]) -> bool:
        """GUI version of version selection."""
        if not self.root:
            self.root = tk.Tk()
            self.root.withdraw()
            
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select SocWatch Version")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        
        # Make dialog modal and bring to front
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.lift()
        dialog.focus_force()
        
        # Center the dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Variables
        selected_version = tk.StringVar()
        result = {'selected': False}
        
        # Main frame
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Available SocWatch Versions:", 
                              font=('Arial', 12, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Listbox with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                            font=('Consolas', 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for version_path in versions:
            listbox.insert(tk.END, str(version_path))
        
        # Select first item by default
        if versions:
            listbox.selection_set(0)
            
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                self.selected_version = versions[idx]
                result['selected'] = True
                dialog.destroy()
                
        def on_cancel():
            result['selected'] = False
            dialog.destroy()
            
        # Buttons
        select_btn = tk.Button(button_frame, text="Select", command=on_select,
                              bg='#0078d4', fg='white', font=('Arial', 10))
        select_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel,
                              font=('Arial', 10))
        cancel_btn.pack(side=tk.RIGHT)
        
        # Handle double-click
        def on_double_click(event):
            on_select()
        listbox.bind('<Double-Button-1>', on_double_click)
        
        # Handle Enter key
        def on_enter(event):
            on_select()
        dialog.bind('<Return>', on_enter)
        
        # Add timeout fallback - auto-select first version after 30 seconds
        def auto_select_timeout():
            if dialog.winfo_exists():
                print("⏰ Dialog timeout - auto-selecting first version...")
                if versions:
                    self.selected_version = versions[0]
                    result['selected'] = True
                dialog.destroy()
        
        dialog.after(30000, auto_select_timeout)  # 30 second timeout
        
        # Wait for dialog to close
        try:
            dialog.wait_window()
        except tk.TclError:
            # Dialog was destroyed
            pass
        
        if result['selected']:
            print(f"✅ Selected: {self.selected_version}")
            return True
        else:
            print("❌ Selection cancelled")
            return False
    
    def _select_version_console(self, versions: List[Path]) -> bool:
        """Console version of version selection."""
        print("🔍 Available SocWatch versions:")
        for i, version_path in enumerate(versions, 1):
            print(f"  {i}. {version_path}")
            
        while True:
            try:
                choice = input(f"\nSelect version (1-{len(versions)}): ").strip()
                if not choice:
                    continue
                    
                idx = int(choice) - 1
                if 0 <= idx < len(versions):
                    self.selected_version = versions[idx]
                    print(f"✅ Selected: {self.selected_version}")
                    return True
                else:
                    print(f"❌ Please enter a number between 1 and {len(versions)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n❌ Selection cancelled")
                return False
    
    def find_etl_files(self, input_folder: Path) -> List[Dict]:
        """
        Recursively find all .etl files and group them by SocWatch collections.
        
        Args:
            input_folder: Root folder to search
            
        Returns:
            List of collection info dicts
        """
        if not input_folder.exists():
            print(f"❌ Input folder not found: {input_folder}")
            return []
            
        print(f"🔍 Scanning for .etl files in: {input_folder}")
        
        # Use glob to recursively find .etl files
        try:
            pattern = str(input_folder / "**" / "*.etl")
            print(f"🔍 Search pattern: {pattern}")
            all_etl_files = [Path(f) for f in glob.glob(pattern, recursive=True)]
            print(f"🔍 Raw glob results: {len(all_etl_files)} files found")
        except Exception as e:
            print(f"❌ Error during file search: {e}")
            return []
        
        # Group files by directory and detect collections
        collections = {}
        
        for etl_file in all_etl_files:
            directory = etl_file.parent
            filename = etl_file.stem
            
            # Detect SocWatch session types
            session_types = ['_extraSession', '_hwSession', '_infoSession', '_osSession']
            base_name = filename
            is_session_file = False
            
            # Check if this is a session file and extract base name
            for session_type in session_types:
                if filename.endswith(session_type):
                    base_name = filename[:-len(session_type)]
                    is_session_file = True
                    break
            
            # Group by directory and base name
            collection_key = str(directory / base_name)
            
            if collection_key not in collections:
                collections[collection_key] = {
                    'directory': directory,
                    'base_name': base_name,
                    'files': [],
                    'total_size': 0,
                    'is_collection': False
                }
            
            # Add file info
            file_size = etl_file.stat().st_size / (1024 * 1024)  # Size in MB
            collections[collection_key]['files'].append({
                'path': etl_file,
                'filename': filename,
                'size': file_size
            })
            collections[collection_key]['total_size'] += file_size
            
            # Mark as collection if we found session files
            if is_session_file:
                collections[collection_key]['is_collection'] = True
        
        # Convert to processing list
        processing_list = []
        for collection_info in collections.values():
            # If multiple files with same base name, it's likely a collection
            if len(collection_info['files']) > 1:
                collection_info['is_collection'] = True
            
            processing_list.append(collection_info)
        
        print(f"🔍 Found {len(all_etl_files)} .etl files in {len(processing_list)} collection(s)")
        
        # Print detailed list of found collections
        if processing_list:
            print("\n📋 Detected SocWatch collections:")
            print("=" * 50)
            for i, collection in enumerate(processing_list, 1):
                try:
                    relative_path = collection['directory'].relative_to(input_folder)
                    if collection['is_collection']:
                        print(f"  {i:2d}. {collection['base_name']} (Collection)")
                        print(f"      📁 Location: {collection['directory']}")
                        print(f"      📏 Total size: {collection['total_size']:.1f} MB")
                        print(f"      🏷️  Base prefix: {collection['base_name']}")
                        print(f"      📚 Session files:")
                        for file_info in sorted(collection['files'], key=lambda x: x['filename']):
                            print(f"         - {file_info['filename']}.etl ({file_info['size']:.1f} MB)")
                    else:
                        file_info = collection['files'][0]
                        print(f"  {i:2d}. {relative_path / (file_info['filename'] + '.etl')}")
                        print(f"      📁 Location: {collection['directory']}")
                        print(f"      📏 Size: {file_info['size']:.1f} MB")
                        print(f"      🏷️  Prefix: {file_info['filename']}")
                except Exception as e:
                    print(f"  {i:2d}. {collection['base_name']} (Error reading details: {e})")
            print("=" * 50)
        else:
            print("❌ No .etl files found in the specified directory and its subdirectories")
            
        return processing_list
    

    def process_collection(self, collection: Dict) -> bool:
        """
        Process a SocWatch collection using socwatch.exe.
        
        Args:
            collection: Dictionary containing collection info
            
        Returns:
            True if processing successful, False otherwise
        """
        if not self.selected_version:
            print("❌ No SocWatch version selected")
            return False
            
        # Get collection info
        base_name = collection['base_name']
        collection_dir = collection['directory']
        
        # Check if already processed - look for {base_name}_summary.csv
        summary_csv = collection_dir / f"{base_name}_summary.csv"
        if summary_csv.exists():
            print(f"   ⏭️  Skipping - already processed (found {base_name}_summary.csv)")
            self.processed_files.append(collection)
            return True
        
        # Use full path to base name for input (directory + base_name)
        full_input_path = str(collection_dir / base_name)
        
        # Create output directory with base_name + _summary
        output_dir = str(collection_dir / f"{base_name}_summary")
        
        # Build socwatch command
        cmd = [
            str(self.selected_version),
            "-i", full_input_path,
            "-o", output_dir
        ]
        
        if collection['is_collection']:
            print(f"📊 Processing collection: {base_name}")
            print(f"   📚 Session files: {', '.join([f['filename'] + '.etl' for f in collection['files']])}")
        else:
            print(f"📊 Processing: {collection['files'][0]['filename']}.etl")
        
        print(f"   📁 Working directory: {collection_dir}")
        print(f"   🔧 SocWatch executable: {self.selected_version}")
        print(f"   📝 Input full path: {full_input_path}")
        print(f"   📤 Output directory: {output_dir}")
        print(f"   ⚡ Full command: {' '.join(cmd)}")
        
        try:
            # Change to the collection directory where .etl files are located
            original_cwd = os.getcwd()
            os.chdir(collection_dir)
            
            # Run socwatch.exe
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print(f"   ✅ Success")
                self.processed_files.append(collection)
                return True
            else:
                print(f"   ❌ Failed (exit code: {result.returncode})")
                print(f"   Error: {result.stderr}")
                self.failed_files.append((collection, result.stderr))
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout (>5 minutes)")
            self.failed_files.append((collection, "Timeout"))
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.failed_files.append((collection, str(e)))
            return False
        finally:
            # Ensure we're back in original directory
            os.chdir(original_cwd)
    
    def process_all_files(self, input_folder: Path) -> None:
        """
        Process all SocWatch collections in the input folder.
        
        Args:
            input_folder: Root folder to process
        """
        self.start_time = time.time()
        collections = self.find_etl_files(input_folder)
        
        if not collections:
            print("❌ No .etl files found to process")
            return
        
        # Show SocWatch command-line information
        print(f"\n🔧 SocWatch Command-Line Information:")
        print("=" * 60)
        print(f"📍 Selected SocWatch: {self.selected_version}")
        print(f"📋 Command pattern: socwatch.exe -i <base_prefix> -o <output_folder>")
        print(f"📖 Options explanation:")
        print(f"   -i <prefix>  : Input base prefix (for collections, use base name)")
        print(f"   -o <folder>  : Output directory (same as input file location)")
        print(f"💡 Working directory: Changes to each collection's folder before processing")
        print(f"🔍 Collection detection: Groups session files by base name (e.g., CataV3)")
        print("=" * 60)
            
        print(f"\n🚀 Starting batch processing of {len(collections)} collection(s)...")
        print("=" * 60)
        
        for i, collection in enumerate(collections, 1):
            if collection['is_collection']:
                print(f"\n[{i}/{len(collections)}] {collection['base_name']} (Collection)")
            else:
                relative_path = collection['directory'].relative_to(input_folder)
                filename = collection['files'][0]['filename']
                print(f"\n[{i}/{len(collections)}] {relative_path / (filename + '.etl')}")
            self.process_collection(collection)
            
        self.print_final_report()
    
    def print_final_report(self) -> None:
        """Print final processing report."""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        print("\n" + "=" * 60)
        print("📋 FINAL PROCESSING REPORT")
        print("=" * 60)
        
        total_collections = len(self.processed_files) + len(self.failed_files)
        success_rate = (len(self.processed_files) / total_collections * 100) if total_collections > 0 else 0
        
        print(f"📊 Total collections processed: {total_collections}")
        print(f"✅ Successfully processed: {len(self.processed_files)}")
        print(f"❌ Failed: {len(self.failed_files)}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        
        if self.processed_files:
            print(f"\n✅ Successfully processed collections:")
            for collection in self.processed_files:
                print(f"   ✓ {collection['base_name']}")
        
        if self.failed_files:
            print(f"\n❌ Failed collections:")
            for collection, error in self.failed_files:
                print(f"   ✗ {collection['base_name']}: {error}")
                
        print(f"\n🔧 SocWatch Configuration Used:")
        print(f"   📍 Executable: {self.selected_version}")
        print(f"   📋 Command pattern: socwatch.exe -i <prefix> -o <output_dir>")
        print("✨ Processing complete!")


def main():
    """Main entry point."""
    print("🔧 SocWatch Post-Processor (socwatch_pp)")
    print("=" * 40)
    
    # Determine if we should use GUI mode
    use_gui = True
    input_folder = None
    
    # Check command line arguments
    if len(sys.argv) == 1:
        # No arguments - use GUI mode
        print("🖥️  GUI Mode: Select folder using dialog")
        use_gui = True
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print("Usage:")
            print("  python socwatch_pp.py                    # GUI mode - select folder with dialog")
            print("  python socwatch_pp.py <input_folder>     # CLI mode - use specified folder")
            print("  python socwatch_pp.py --cli <folder>     # Force CLI mode")
            print("\nExamples:")
            print("  python socwatch_pp.py                              # Open folder selection dialog")
            print("  python socwatch_pp.py C:\\data\\socwatch_traces      # Use specified folder")
            print("  python socwatch_pp.py --cli C:\\data\\traces         # Use CLI mode")
            return
        elif sys.argv[1] == '--cli':
            print("❌ --cli flag requires a folder path")
            print("Usage: python socwatch_pp.py --cli <input_folder>")
            sys.exit(1)
        else:
            # CLI mode with folder argument
            input_folder = Path(sys.argv[1])
            use_gui = False
            print("💻 CLI Mode: Using specified folder")
    elif len(sys.argv) == 3 and sys.argv[1] == '--cli':
        # Force CLI mode
        input_folder = Path(sys.argv[2])
        use_gui = False
        print("💻 CLI Mode (forced): Using specified folder")
    else:
        print("❌ Invalid arguments")
        print("Usage: python socwatch_pp.py [<input_folder>] [--cli <input_folder>]")
        print("Run 'python socwatch_pp.py --help' for more information")
        sys.exit(1)
    
    # Initialize processor
    processor = SocWatchProcessor(use_gui=use_gui)
    
    # Get input folder
    if use_gui and input_folder is None:
        print("📂 Opening folder selection dialog...")
        input_folder = processor.select_folder_gui()
        if input_folder is None:
            print("❌ No folder selected. Exiting.")
            return
    
    # Validate input folder
    if not input_folder.exists():
        error_msg = f"Input folder does not exist: {input_folder}"
        if use_gui:
            if not processor.root:
                processor.root = tk.Tk()
                processor.root.withdraw()
            messagebox.showerror("Folder Not Found", error_msg)
        else:
            print(f"❌ {error_msg}")
        sys.exit(1)
        
    if not input_folder.is_dir():
        error_msg = f"Input path is not a directory: {input_folder}"
        if use_gui:
            if not processor.root:
                processor.root = tk.Tk()
                processor.root.withdraw()
            messagebox.showerror("Invalid Path", error_msg)
        else:
            print(f"❌ {error_msg}")
        sys.exit(1)
        
    print(f"📁 Input folder: {input_folder}")
    
    # Select SocWatch version
    if not processor.select_socwatch_version():
        print("❌ No SocWatch version selected. Exiting.")
        sys.exit(1)
        
    # Process all files
    try:
        print("🔍 Starting file detection and processing...")
        
        # Note: Removed GUI processing dialog due to hanging issues
        # Users will see progress in terminal window
        
        processor.process_all_files(input_folder)
        
        # Note: Removed GUI completion dialog due to hanging issues
        # Processing results are shown in console output above
        
        if use_gui:
            print("🖥️  GUI Mode: Processing completed - check results above")
            print("💡 You can now close this terminal window")
                
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        processor.print_final_report()
        sys.exit(1)
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"❌ {error_msg}")
        if use_gui:
            print("🖥️  GUI Mode: An error occurred - check error message above")
        sys.exit(1)


if __name__ == "__main__":
    main()