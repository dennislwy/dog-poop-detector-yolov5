<#
.SYNOPSIS
Starts the labelImg tool for labeling images.

.DESCRIPTION
This script activates the virtual environment and checks if the labelImg tool is installed. If not, it installs it using pip. Then, it starts the labelImg tool for labeling images.

.PARAMETER None

.EXAMPLE
./label-images.ps1
#>

# Activate the virtual environment
& "./.venv/Scripts/Activate.ps1"

# Check if labelImg is installed, if not install it
$labelImgInstalled = python -c "import pkg_resources; print('labelimg' in [d.key for d in pkg_resources.working_set])"

if ($labelImgInstalled -eq 'False') {
    Write-Host "labelImg not found. Installing..."
    pip install labelImg
}

Write-Host "Starting labelmg..."
labelImg
