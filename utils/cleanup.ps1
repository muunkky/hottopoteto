# PowerShell script to clean up unused files in the project

# Enable more detailed error reporting
$ErrorActionPreference = "Continue"
$VerbosePreference = "Continue"

# Color definitions
$HeaderColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"
$FilePathColor = "Magenta"
$SeparatorColor = "DarkGray"

# Function to write colored section header
function Write-SectionHeader {
    param (
        [string]$Text
    )
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $SeparatorColor
    Write-Host " $Text" -ForegroundColor $HeaderColor
    Write-Host ("=" * 60) -ForegroundColor $SeparatorColor
}

# Get the directory of the script and the project directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-SectionHeader "INITIALIZATION"
Write-Host "Script directory: " -NoNewline
Write-Host $ScriptDir -ForegroundColor $FilePathColor
Write-Host "Project directory: " -NoNewline
Write-Host $ProjectDir -ForegroundColor $FilePathColor

# Create backups directory
$BackupDir = Join-Path $ProjectDir "backup_unused"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: " -NoNewline
    Write-Host $BackupDir -ForegroundColor $FilePathColor
} else {
    Write-Host "Using existing backup directory: " -NoNewline
    Write-Host $BackupDir -ForegroundColor $FilePathColor
}

# Function to backup a file
function Backup-File {
    param (
        [string]$FilePath
    )
    
    # Get relative path from project directory
    $RelativePath = $FilePath.Substring($ProjectDir.Length + 1)
    $BackupPath = Join-Path $BackupDir $RelativePath
    
    # Create directory structure if it doesn't exist
    $BackupFolder = Split-Path -Parent $BackupPath
    if (-not (Test-Path $BackupFolder)) {
        New-Item -ItemType Directory -Path $BackupFolder -Force | Out-Null
    }
    
    # Copy the file to the backup location
    Copy-Item -Path $FilePath -Destination $BackupPath -Force
    Write-Host "[OK] Backed up: " -ForegroundColor $SuccessColor -NoNewline
    Write-Host $RelativePath -ForegroundColor $FilePathColor
}

# Function to delete a file
function Remove-ProjectFile {
    param (
        [string]$FilePath
    )
    
    # Get relative path for logging
    $RelativePath = $FilePath.Substring($ProjectDir.Length + 1)
    
    # Delete the file
    Remove-Item -Path $FilePath -Force
    Write-Host "[OK] Deleted: " -ForegroundColor $SuccessColor -NoNewline
    Write-Host $RelativePath -ForegroundColor $FilePathColor
}

# Check if Python is available
Write-SectionHeader "ENVIRONMENT CHECK"
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[OK] Found Python: " -ForegroundColor $SuccessColor -NoNewline
    Write-Host $pythonVersion
} 
catch {
    Write-Host "[ERROR] Python not found or not in PATH. " -ForegroundColor $ErrorColor -NoNewline
    Write-Host "Please install Python and make sure it's in your PATH."
    exit 1
}

# Check if the Python script exists
$PythonScript = Join-Path $ScriptDir "clean_unused_files.py"
if (-not (Test-Path $PythonScript)) {
    Write-Host "[ERROR] Python script not found: " -ForegroundColor $ErrorColor -NoNewline 
    Write-Host $PythonScript -ForegroundColor $FilePathColor
    Write-Host "Current directory contains: $((Get-ChildItem -Path $ScriptDir).Name -join ', ')"
    exit 1
} 
else {
    Write-Host "[OK] Found analysis script: " -ForegroundColor $SuccessColor -NoNewline
    Write-Host $PythonScript -ForegroundColor $FilePathColor
}

# Run the Python script to find unused files
Write-SectionHeader "FILE ANALYSIS"
Write-Host "Running: python $PythonScript $ProjectDir"

try {
    # Set environment to use UTF-8
    $env:PYTHONIOENCODING = "utf-8"
    
    # Capture all output from the Python script
    $Output = & python $PythonScript $ProjectDir 2>&1
    
    # Print Python script output with minimal formatting
    $Output | ForEach-Object { Write-Host $_ }
    
    # Extract unused files from the output
    Write-Host "Parsing output for unused files..." -ForegroundColor $HeaderColor
    $UnusedFilesLines = @($Output | Where-Object { $_ -match '^\s*-\s+(.+)$' })
    
    if ($UnusedFilesLines.Count -eq 0) {
        Write-Host "[WARNING] No matching unused files found in output." -ForegroundColor $WarningColor
        exit 0
    }
    
    $UnusedFiles = @()
    foreach ($line in $UnusedFilesLines) {
        if ($line -match '^\s*-\s+(.+)$') {
            $UnusedFiles += $matches[1]
        }
    }
    
    if ($UnusedFiles.Count -eq 0) {
        Write-Host "[WARNING] No unused files found!" -ForegroundColor $WarningColor
        exit 0
    }
    
    # Display the found files
    Write-Host "`nFound " -NoNewline
    Write-Host $UnusedFiles.Count -ForegroundColor $SuccessColor -NoNewline
    Write-Host " potentially unused files:"
    
    foreach ($file in $UnusedFiles) {
        Write-Host "  * " -NoNewline
        Write-Host $file -ForegroundColor $FilePathColor
    }
}
catch {
    Write-Host "[ERROR] Failed to analyze project: " -ForegroundColor $ErrorColor -NoNewline
    Write-Host $_.Exception.Message
    Write-Host $_.ScriptStackTrace
    exit 1
}

# Ask user what to do
Write-SectionHeader "ACTION SELECTION"
Write-Host "What would you like to do with these files?"
Write-Host "1) Backup all files" -ForegroundColor $SuccessColor
Write-Host "2) Delete all files" -ForegroundColor $WarningColor
Write-Host "3) Review files one by one" -ForegroundColor $HeaderColor
Write-Host "4) Exit without changes" -ForegroundColor $SeparatorColor

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-SectionHeader "BACKING UP FILES"
        foreach ($RelativePath in $UnusedFiles) {
            $FullPath = Join-Path $ProjectDir $RelativePath
            Write-Host "Processing: " -NoNewline
            Write-Host $RelativePath -ForegroundColor $FilePathColor
            if (Test-Path $FullPath) {
                Backup-File -FilePath $FullPath
            } else {
                Write-Host "[WARNING] File not found: " -ForegroundColor $WarningColor -NoNewline
                Write-Host $RelativePath -ForegroundColor $FilePathColor
            }
        }
    }
    
    "2" {
        Write-SectionHeader "DELETING FILES"
        Write-Host "Are you sure you want to delete ALL these files? This cannot be undone." -ForegroundColor $WarningColor
        $confirm = Read-Host "Type 'yes' to confirm"
        
        if ($confirm -eq "yes") {
            foreach ($RelativePath in $UnusedFiles) {
                $FullPath = Join-Path $ProjectDir $RelativePath
                Write-Host "Processing: " -NoNewline
                Write-Host $RelativePath -ForegroundColor $FilePathColor
                if (Test-Path $FullPath) {
                    Remove-ProjectFile -FilePath $FullPath
                } else {
                    Write-Host "[WARNING] File not found: " -ForegroundColor $WarningColor -NoNewline
                    Write-Host $RelativePath -ForegroundColor $FilePathColor
                }
            }
        } else {
            Write-Host "[WARNING] Delete operation cancelled" -ForegroundColor $WarningColor
        }
    }
    
    "3" {
        Write-SectionHeader "REVIEWING FILES"
        foreach ($RelativePath in $UnusedFiles) {
            $FullPath = Join-Path $ProjectDir $RelativePath
            
            Write-Host "`nProcessing: " -NoNewline
            Write-Host $RelativePath -ForegroundColor $FilePathColor
            
            if (-not (Test-Path $FullPath)) {
                Write-Host "[WARNING] File not found: " -ForegroundColor $WarningColor -NoNewline
                Write-Host $RelativePath -ForegroundColor $FilePathColor
                continue
            }
            
            # Display file info in colored box
            Write-Host ("`n" + "-" * 80) -ForegroundColor $SeparatorColor
            Write-Host "File: " -NoNewline 
            Write-Host $RelativePath -ForegroundColor $FilePathColor
            Write-Host "Path: " -NoNewline 
            Write-Host $FullPath -ForegroundColor $FilePathColor
            Write-Host ("-" * 80) -ForegroundColor $SeparatorColor
            
            # Display the first 20 lines of the file
            try {
                Get-Content -Path $FullPath -TotalCount 20
                Write-Host "..." -ForegroundColor $SeparatorColor
            } catch {
                Write-Host "[ERROR] Failed to read file: " -ForegroundColor $ErrorColor -NoNewline
                Write-Host $_.Exception.Message
            }
            Write-Host ("-" * 80) -ForegroundColor $SeparatorColor
            
            # Display options with colors
            Write-Host "`nWhat would you like to do with this file? " -ForegroundColor $HeaderColor
            Write-Host "Full path: " -NoNewline
            Write-Host $FullPath -ForegroundColor $FilePathColor
            Write-Host "b) Backup the file" -ForegroundColor $SuccessColor
            Write-Host "d) Delete the file" -ForegroundColor $WarningColor
            Write-Host "s) Skip this file" -ForegroundColor $SeparatorColor
            Write-Host "q) Quit the review" -ForegroundColor $ErrorColor
            
            $fileChoice = Read-Host "Enter your choice (b/d/s/q)"
            
            switch -Regex ($fileChoice) {
                "^[bB]$" {
                    Backup-File -FilePath $FullPath
                }
                
                "^[dD]$" {
                    Remove-ProjectFile -FilePath $FullPath
                }
                
                "^[sS]$" {
                    Write-Host "[INFO] Skipped: " -ForegroundColor $SeparatorColor -NoNewline
                    Write-Host $RelativePath -ForegroundColor $FilePathColor
                }
                
                "^[qQ]$" {
                    Write-Host "[WARNING] Review stopped" -ForegroundColor $WarningColor
                    break
                }
                
                default {
                    Write-Host "[WARNING] Invalid choice, skipping file" -ForegroundColor $WarningColor
                }
            }
        }
    }
    
    "4" {
        Write-Host "[INFO] Exiting without changes" -ForegroundColor $SeparatorColor
    }
    
    default {
        Write-Host "[WARNING] Invalid choice, exiting without changes" -ForegroundColor $WarningColor
    }
}

Write-SectionHeader "CLEANUP COMPLETE"
