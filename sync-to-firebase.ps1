Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SYNCING SHEET CHANGES TO FIREBASE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\durel\Documents\confident-picks-restored"

Write-Host "Running Python sync script..." -ForegroundColor Yellow
python sync_sheet_to_firebase.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SYNC COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
