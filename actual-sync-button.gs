/**
 * ACTUAL SYNC BUTTON
 * ==================
 * 
 * This creates a button that actually syncs to Firebase by calling
 * a local web service that runs the Python script.
 */

/**
 * Actually sync to Firebase by calling local web service
 */
function syncToFirebase() {
  const ui = SpreadsheetApp.getUi();
  
  try {
    // Show loading message
    ui.alert('Syncing...', 'Please wait while we sync your changes to Firebase...', ui.ButtonSet.OK);
    
    // Call the local web service
    const response = UrlFetchApp.fetch('http://localhost:5000/sync-to-firebase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const result = JSON.parse(response.getContentText());
    
    if (result.success) {
      ui.alert(
        'Sync Successful!', 
        'Your changes have been synced to Firebase successfully!\n\n' +
        'Updated picks: ' + (result.output.match(/Updated Firebase:/g) || []).length,
        ui.ButtonSet.OK
      );
    } else {
      ui.alert(
        'Sync Failed', 
        'There was an error syncing to Firebase:\n\n' + result.message,
        ui.ButtonSet.OK
      );
    }
    
  } catch (error) {
    ui.alert(
      'Connection Error', 
      'Could not connect to sync service. Make sure the web service is running.\n\n' +
      'To start the web service:\n' +
      '1. Open Command Prompt\n' +
      '2. Run: python sync-web-service.py\n' +
      '3. Then try the sync button again',
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
    .addItem('Sync to Firebase', 'syncToFirebase')
    .addItem('Start Web Service', 'showWebServiceInstructions')
    .addToUi();
}

/**
 * Show instructions for starting the web service
 */
function showWebServiceInstructions() {
  const ui = SpreadsheetApp.getUi();
  ui.alert(
    'Start Web Service',
    'To use the sync button, you need to start the web service first:\n\n' +
    '1. Open Command Prompt\n' +
    '2. Navigate to your project folder\n' +
    '3. Run: python sync-web-service.py\n' +
    '4. Keep the window open\n' +
    '5. Then use the sync button\n\n' +
    'The web service will run on http://localhost:5000',
    ui.ButtonSet.OK
  );
}
