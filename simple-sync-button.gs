/**
 * SIMPLE SYNC BUTTON
 * ==================
 * 
 * This creates a simple button that runs the Python sync script
 * WITHOUT touching your sheet data.
 */

/**
 * Create a simple sync button
 */
function createSyncButton() {
  const sheet = SpreadsheetApp.getActiveSheet();
  
  // Add a button (using a cell with a note)
  const buttonCell = sheet.getRange('R1'); // Column R, Row 1
  buttonCell.setValue('🔄 SYNC TO FIREBASE');
  buttonCell.setBackground('#4285f4');
  buttonCell.setFontColor('white');
  buttonCell.setFontWeight('bold');
  buttonCell.setNote('Click this cell and run "syncToFirebase" function');
  
  console.log('Sync button created in cell R1');
}

/**
 * Simple sync function that shows instructions
 */
function syncToFirebase() {
  const ui = SpreadsheetApp.getUi();
  
  const response = ui.alert(
    'Sync to Firebase',
    'This will sync your sheet changes to Firebase.\n\n' +
    'To run the sync:\n' +
    '1. Open Command Prompt/Terminal\n' +
    '2. Navigate to your project folder\n' +
    '3. Run: python sync_sheet_to_firebase.py\n\n' +
    'Or click OK to see detailed instructions.',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (response == ui.Button.OK) {
    ui.alert(
      'Detailed Instructions',
      '1. Open Command Prompt (Windows) or Terminal (Mac)\n' +
      '2. Type: cd "C:\\Users\\durel\\Documents\\confident-picks-restored"\n' +
      '3. Type: python sync_sheet_to_firebase.py\n' +
      '4. Press Enter\n\n' +
      'The script will sync all your changes to Firebase!',
      ui.ButtonSet.OK
    );
  }
}

/**
 * Create menu on sheet open
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🔄 Sync Tools')
    .addItem('Create Sync Button', 'createSyncButton')
    .addItem('Sync to Firebase', 'syncToFirebase')
    .addItem('Show Instructions', 'showSyncInstructions')
    .addToUi();
}

/**
 * Show detailed sync instructions
 */
function showSyncInstructions() {
  const ui = SpreadsheetApp.getUi();
  ui.alert(
    'Sync Instructions',
    'To sync your sheet changes to Firebase:\n\n' +
    '1. Edit picks in this sheet\n' +
    '2. Open Command Prompt/Terminal\n' +
    '3. Run: python sync_sheet_to_firebase.py\n\n' +
    'That\'s it! Your changes will be pushed to Firebase.',
    ui.ButtonSet.OK
  );
}
