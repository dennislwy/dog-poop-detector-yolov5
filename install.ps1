# create virtual environment
echo "Creating virtual environment"
python -m venv venv

# activate virtual environment
echo "Activating virtual environment"
& "venv/Scripts/Activate.ps1"

# install packages
echo "Installing packages"
pip install -r requirements.txt
