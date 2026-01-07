"""
Comprehensive Logging Update Script for scripts_ui.py
This script automatically updates all run_* functions to match workflows.py logging pattern

Usage: python apply_comprehensive_logging.py
"""

import re
import shutil
from datetime import datetime

# Backup the original file
def backup_file():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'scripts_ui_backup_{timestamp}.py'
    shutil.copy('scripts_ui.py', backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def update_run_dataturn():
    """Update run_dataturn function"""
    
    old_code = """def run_dataturn(expfd_name, config):
    \"\"\"Run the DataTurn script functionality\"\"\"
    logger.info(f"DataTurn operation started - EXPFD: {expfd_name}")
    try:
        output = []
        output.append("="*60)
        output.append("DATATURN OPERATION STARTED")
        output.append("="*60)
        output.append(f"EXPFD File Name: {expfd_name}")
        output.append("")
        
        # Get paths from config
        dataturn_exe = config.get('DATATURN_EXE', '')
        expfd_path = config.get('EXPFD_PATH', '')
        input_path = config.get('INPUT_PATH', '')
        output_path = config.get('OUTPUT_PATH', '')
        
        if not dataturn_exe or not os.path.exists(dataturn_exe):
            return '\\n'.join(output) + f"\\n❌ ERROR: DataTurn executable not found: {dataturn_exe}"
        
        if not expfd_path or not os.path.exists(expfd_path):
            return '\\n'.join(output) + f"\\n❌ ERROR: EXPFD path not found: {expfd_path}"
        
        if not input_path or not os.path.exists(input_path):
            return '\\n'.join(output) + f"\\n❌ ERROR: Input path not found: {input_path}"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            output.append(f"✅ Created output directory: {output_path}")
        
        # Construct full paths
        expfd_file = os.path.join(expfd_path, f"{expfd_name}.expfd")
        input_file = os.path.join(input_path, f"{expfd_name}.txt")
        output_file = os.path.join(output_path, f"{expfd_name}.txt")
        
        # Check if EXPFD file exists
        if not os.path.exists(expfd_file):
            return '\\n'.join(output) + f"\\n❌ ERROR: EXPFD file not found: {expfd_file}"
        
        # Check if input file exists
        if not os.path.exists(input_file):
            return '\\n'.join(output) + f"\\n❌ ERROR: Input file not found: {input_file}"
        
        output.append(f"EXPFD File: {expfd_file}")
        output.append(f"Input File: {input_file}")
        output.append(f"Output File: {output_file}")
        output.append("")
        output.append("Running DataTurn conversion...")
        output.append("")
        
        # Run dataturn command
        cmd = [dataturn_exe, expfd_file, input_file, output_file]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Display command output
            if result.stdout:
                output.append("DataTurn Output:")
                output.append(result.stdout)
            
            if result.stderr:
                output.append("DataTurn Errors:")
                output.append(result.stderr)
            
            # Check if output file was created
            if os.path.exists(output_file):
                output.append("")
                output.append("="*60)
                output.append("✅ DataTurn conversion completed successfully!")
                output.append(f"Output file created: {output_file}")
                output.append("="*60)
                logger.info(f"DataTurn completed successfully for {expfd_name}")
            else:
                output.append("")
                output.append("="*60)
                output.append("❌ DataTurn conversion failed!")
                output.append("Output file was not created.")
                output.append("="*60)
                logger.error(f"DataTurn failed for {expfd_name} - output file not created")
            
        except subprocess.TimeoutExpired:
            output.append("❌ ERROR: DataTurn process timed out (exceeded 5 minutes)")
            logger.error(f"DataTurn timeout for {expfd_name}")
        except Exception as e:
            output.append(f"❌ ERROR: Failed to run DataTurn: {str(e)}")
            logger.error(f"DataTurn execution error for {expfd_name}: {str(e)}")
        
        return '\\n'.join(output)
        
    except Exception as e:
        logger.error(f"DataTurn operation failed: {str(e)}", exc_info=True)
        return f'Error running dataturn: {e}\\n\\nTraceback:\\n{traceback.format_exc()}'"""
    
    new_code = """def run_dataturn(expfd_name, config):
    \"\"\"Run the DataTurn script functionality\"\"\"
    try:
        output = []
        output.append("="*60)
        output.append("DATATURN OPERATION STARTED")
        output.append("="*60)
        output.append(f"EXPFD File Name: {expfd_name}")
        output.append("")
        
        # Get paths from config
        dataturn_exe = config.get('DATATURN_EXE', '')
        expfd_path = config.get('EXPFD_PATH', '')
        input_path = config.get('INPUT_PATH', '')
        output_path = config.get('OUTPUT_PATH', '')
        
        if not dataturn_exe or not os.path.exists(dataturn_exe):
            error_output = '\\n'.join(output) + f"\\n❌ ERROR: DataTurn executable not found: {dataturn_exe}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
            return error_output, False
        
        if not expfd_path or not os.path.exists(expfd_path):
            error_output = '\\n'.join(output) + f"\\n❌ ERROR: EXPFD path not found: {expfd_path}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
            return error_output, False
        
        if not input_path or not os.path.exists(input_path):
            error_output = '\\n'.join(output) + f"\\n❌ ERROR: Input path not found: {input_path}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
            return error_output, False
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            output.append(f"✅ Created output directory: {output_path}")
        
        # Construct full paths
        expfd_file = os.path.join(expfd_path, f"{expfd_name}.expfd")
        input_file = os.path.join(input_path, f"{expfd_name}.txt")
        output_file = os.path.join(output_path, f"{expfd_name}.txt")
        
        # Check if EXPFD file exists
        if not os.path.exists(expfd_file):
            error_output = '\\n'.join(output) + f"\\n❌ ERROR: EXPFD file not found: {expfd_file}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
            return error_output, False
        
        # Check if input file exists
        if not os.path.exists(input_file):
            error_output = '\\n'.join(output) + f"\\n❌ ERROR: Input file not found: {input_file}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
            return error_output, False
        
        output.append(f"EXPFD File: {expfd_file}")
        output.append(f"Input File: {input_file}")
        output.append(f"Output File: {output_file}")
        output.append("")
        output.append("Running DataTurn conversion...")
        output.append("")
        
        # Run dataturn command
        cmd = [dataturn_exe, expfd_file, input_file, output_file]
        command_str = ' '.join(cmd)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Display command output
            if result.stdout:
                output.append("DataTurn Output:")
                output.append(result.stdout)
            
            if result.stderr:
                output.append("DataTurn Errors:")
                output.append(result.stderr)
            
            # Check if output file was created
            if os.path.exists(output_file):
                output.append("")
                output.append("="*60)
                output.append("✅ DataTurn conversion completed successfully!")
                output.append(f"Output file created: {output_file}")
                output.append("="*60)
                success = True
            else:
                output.append("")
                output.append("="*60)
                output.append("❌ DataTurn conversion failed!")
                output.append("Output file was not created.")
                output.append("="*60)
                success = False
            
        except subprocess.TimeoutExpired:
            output.append("❌ ERROR: DataTurn process timed out (exceeded 5 minutes)")
            success = False
        except Exception as e:
            output.append(f"❌ ERROR: Failed to run DataTurn: {str(e)}")
            success = False
        
        result_output = '\\n'.join(output)
        log_command_output("DATATURN", command_str, result_output, success)
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_dataturn: {str(e)}\\n{traceback.format_exc()}"
        log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_output, False)
        return error_output, False"""
    
    return old_code, new_code

def update_run_expfd_creation():
    """Update run_expfd_creation function"""
    
    old_code = """def run_expfd_creation(copybook_names, expfd_path, copybook_path):
    \"\"\"Run the EXPFD creation script functionality\"\"\"
    logger.info(f"EXPFD Creation started - Copybooks: {copybook_names}")
    try:"""
    
    # This function is too long, we'll handle it separately
    return None, None

def update_route_handlers():
    """Returns list of route handler updates"""
    
    updates = []
    
    # dataturn_page
    updates.append({
        'old': """        if expfd_name:
            output = run_dataturn(expfd_name, config)
            success = '✅ DataTurn conversion completed successfully!' in output""",
        'new': """        if expfd_name:
            output, success = run_dataturn(expfd_name, config)"""
    })
    
    return updates

def main():
    print("="*80)
    print("COMPREHENSIVE LOGGING UPDATE SCRIPT")
    print("="*80)
    print()
    
    # Backup first
    backup_path = backup_file()
    print()
    
    # Read the file
    with open('scripts_ui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Updating functions...")
    print()
    
    # Update run_dataturn
    old_dataturn, new_dataturn = update_run_dataturn()
    if old_dataturn and new_dataturn:
        if old_dataturn in content:
            content = content.replace(old_dataturn, new_dataturn)
            print("✅ Updated run_dataturn")
        else:
            print("⚠️  Could not find run_dataturn pattern")
    
    # Update route handlers
    print()
    print("Updating route handlers...")
    route_updates = update_route_handlers()
    for update in route_updates:
        if update['old'] in content:
            content = content.replace(update['old'], update['new'])
            print("✅ Updated route handler")
        else:
            print("⚠️  Could not find route handler pattern")
    
    # Write back
    with open('scripts_ui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("="*80)
    print("UPDATE COMPLETE!")
    print("="*80)
    print()
    print(f"Backup saved to: {backup_path}")
    print()
    print("IMPORTANT: Some functions are too complex for automated update.")
    print("Please review the changes and manually update remaining functions using this pattern:")
    print()
    print("""
def run_function(...):
    try:
        output = []
        # ... build output ...
        
        # On error:
        error_output = '\\n'.join(output) + error_message
        log_command_output("OPERATION", "command", error_output, False)
        return error_output, False
        
        # On success:
        result_output = '\\n'.join(output)
        success = (check condition)
        log_command_output("OPERATION", "command", result_output, success)
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error: {str(e)}\\n{traceback.format_exc()}"
        log_command_output("OPERATION", "command", error_output, False)
        return error_output, False

# Route handler:
output, success = run_function(...)
""")

if __name__ == '__main__':
    main()
