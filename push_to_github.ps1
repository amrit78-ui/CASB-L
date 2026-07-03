# Helper Script to Push your Project to GitHub
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Pushing Palwinder Mam Project to GitHub  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we are in a Git repo (initialized in previous steps)
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# Ask for the repository URL
$repoUrl = Read-Host "Please enter your GitHub Repository URL (e.g., https://github.com/username/repo-name.git)"
$repoUrl = $repoUrl.Trim()

if (-not $repoUrl) {
    Write-Host "Error: Repository URL cannot be empty." -ForegroundColor Red
    Exit
}

# Check if origin already exists
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "Origin already exists pointing to: $existingRemote" -ForegroundColor Yellow
    $confirm = Read-Host "Do you want to overwrite it? (y/n)"
    if ($confirm.ToLower() -eq 'y') {
        git remote remove origin
        git remote add origin $repoUrl
        Write-Host "Updated remote origin to: $repoUrl" -ForegroundColor Green
    }
} else {
    git remote add origin $repoUrl
    Write-Host "Added remote origin: $repoUrl" -ForegroundColor Green
}

# Stage all files
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

# Commit files
Write-Host "Committing files..." -ForegroundColor Yellow
git commit -m "Initial commit with Render config and requirements" 2>$null

# Rename branch to main
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "If prompted, please complete the login/authentication in the browser window." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "  SUCCESS: Project successfully pushed to GitHub!  " -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now follow the deployment instructions to link it to Render." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host "  FAILED: Push was unsuccessful.            " -ForegroundColor Red
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host "Please verify that the repository exists on GitHub, and that you have permissions to push." -ForegroundColor Yellow
}
