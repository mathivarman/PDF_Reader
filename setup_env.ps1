Write-Host "Setting up PDF Reader environment..." -ForegroundColor Green

# Activate virtual environment
& ".\pdf_reader_env\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt

Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "To activate the environment in the future, run: .\pdf_reader_env\Scripts\Activate.ps1" -ForegroundColor Yellow
Read-Host "Press Enter to continue"
