/**
 * ULTRA SIMPLE SYNC BUTTON
 * ========================
 * 
 * This is the simplest possible script that just shows instructions
 * without trying to do anything complex that might cause errors.
 */

/**
 * Show sync instructions
 */
function syncToFirebase() {
  const ui = SpreadsheetApp.getUi();
  
  ui.alert(
    'Sync to Firebase',
    'To sync your sheet changes to Firebase:\n\n' +
    'EASIEST METHOD:\n' +
    '1. Go to your project folder\n' +
    '2. Double-click "sync-to-firebase.bat"\n' +
    '3. That\'s it!\n\n' +
    'COMMAND LINE METHOD:\n' +
    '1. Open Command Prompt\n' +
    '2. Type: cd "C:\\Users\\durel\\Documents\\confident-picks-restored"\n' +
    '3. Type: python confident-picks-automation\\sync_sheet_to_firebase.py\n' +
    '4. Press Enter\n\n' +
    'Your changes will be pushed to Firebase!',
    ui.ButtonSet.OK
  );
}

/**
 * Create menu on sheet open
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🔄 Sync Tools')
    .addItem('Sync to Firebase', 'syncToFirebase')
    .addToUi();
}
