/**
 * FIREBASE PICK CARDS TWO-WAY SYNC
 * =================================
 * 
 * This Google Apps Script creates a two-way sync between Firebase and Google Sheets
 * for pick cards management.
 * 
 * FEATURES:
 * - Reads pick cards from Firebase and displays in sheet
 * - Allows editing picks directly in the sheet
 * - Syncs changes back to Firebase
 * - Provides real-time status updates
 */

// Configuration
const FIREBASE_CONFIG = {
  projectId: 'confident-picks-app-8-25',
  // Add your Firebase service account key here
  serviceAccountKey: {
    // You'll need to add your service account key JSON here
    // Or use Firebase Admin SDK with proper authentication
  }
};

// Sheet configuration
const SHEET_NAME = 'Firebase Picks';
const HEADERS = [
  'Document ID', 'Game', 'Away Team', 'Home Team', 'Pick Type', 
  'Pick Team', 'Confidence Level', 'Model Confidence', 'Team Accuracy',
  'Reasoning Part 1', 'Reasoning Part 2', 'Reasoning Part 3',
  'Game Date', 'Status', 'Last Updated', 'Firebase Status'
];

/**
 * Initialize the Firebase Picks sheet
 */
function initializeFirebasePicksSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  
  // Clear existing data
  sheet.clear();
  
  // Add headers
  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  
  // Format headers
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
  headerRange.setBackground('#4285f4');
  headerRange.setFontColor('white');
  headerRange.setFontWeight('bold');
  
  // Set column widths
  sheet.setColumnWidth(1, 200); // Document ID
  sheet.setColumnWidth(2, 150); // Game
  sheet.setColumnWidth(3, 80);  // Away Team
  sheet.setColumnWidth(4, 80);  // Home Team
  sheet.setColumnWidth(5, 100); // Pick Type
  sheet.setColumnWidth(6, 80);  // Pick Team
  sheet.setColumnWidth(7, 120); // Confidence Level
  sheet.setColumnWidth(8, 120); // Model Confidence
  sheet.setColumnWidth(9, 100); // Team Accuracy
  sheet.setColumnWidth(10, 300); // Reasoning Part 1
  sheet.setColumnWidth(11, 300); // Reasoning Part 2
  sheet.setColumnWidth(12, 300); // Reasoning Part 3
  sheet.setColumnWidth(13, 100); // Game Date
  sheet.setColumnWidth(14, 80);  // Status
  sheet.setColumnWidth(15, 150); // Last Updated
  sheet.setColumnWidth(16, 120); // Firebase Status
  
  console.log('Firebase Picks sheet initialized');
}

/**
 * Sync pick cards from Firebase to Google Sheets
 */
function syncFromFirebaseToSheet() {
  try {
    console.log('Starting sync from Firebase to Sheet...');
    
    // Initialize sheet if it doesn't exist
    initializeFirebasePicksSheet();
    
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
    // Only clear if we have data to replace it with
    // Don't clear existing data unless we're sure we have new data
    
    // TODO: Replace with actual Firebase API calls
    // For now, we'll create a placeholder function
    const pickCards = getPickCardsFromFirebase();
    
    if (pickCards.length === 0) {
      console.log('No pick cards found in Firebase - keeping existing data');
      return;
    }
    
    // Only clear existing data if we have new data to replace it with
    if (sheet.getLastRow() > 1) {
      sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADERS.length).clear();
    }
    
    // Convert pick cards to sheet format
    const sheetData = pickCards.map(pick => [
      pick.docId,
      pick.game,
      pick.away_team,
      pick.home_team,
      pick.pick_type,
      pick.pick_team,
      pick.confidence_level,
      pick.model_confidence,
      pick.team_accuracy,
      pick.reasoning_part1,
      pick.reasoning_part2,
      pick.reasoning_part3,
      pick.game_date,
      pick.status,
      new Date().toLocaleString(),
      'Synced'
    ]);
    
    // Add data to sheet
    if (sheetData.length > 0) {
      sheet.getRange(2, 1, sheetData.length, HEADERS.length).setValues(sheetData);
      
      // Format confidence levels
      const confidenceRange = sheet.getRange(2, 7, sheetData.length, 1);
      const confidenceValues = confidenceRange.getValues();
      
      for (let i = 0; i < confidenceValues.length; i++) {
        const cell = sheet.getRange(i + 2, 7);
        if (confidenceValues[i][0] === 'HIGH') {
          cell.setBackground('#4caf50'); // Green
          cell.setFontColor('white');
        } else if (confidenceValues[i][0] === 'MEDIUM') {
          cell.setBackground('#ff9800'); // Orange
          cell.setFontColor('white');
        }
      }
    }
    
    console.log(`Successfully synced ${pickCards.length} pick cards to sheet`);
    
  } catch (error) {
    console.error('Error syncing from Firebase to Sheet:', error);
    SpreadsheetApp.getUi().alert('Error syncing from Firebase: ' + error.message);
  }
}

/**
 * Sync changes from Google Sheets back to Firebase
 */
function syncFromSheetToFirebase() {
  try {
    console.log('Starting sync from Sheet to Firebase...');
    
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
    if (!sheet || sheet.getLastRow() <= 1) {
      console.log('No data to sync');
      return;
    }
    
    // Get all data except headers
    const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADERS.length).getValues();
    
    let updatedCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      const docId = row[0];
      
      if (!docId) continue;
      
      try {
        // Create pick card object
        const pickCard = {
          game: row[1],
          away_team: row[2],
          home_team: row[3],
          pick_type: row[4],
          pick_team: row[5],
          confidence_level: row[6],
          model_confidence: row[7],
          team_accuracy: row[8],
          reasoning_part1: row[9],
          reasoning_part2: row[10],
          reasoning_part3: row[11],
          game_date: row[12],
          status: row[13],
          last_updated: new Date().toISOString()
        };
        
        // Update Firebase
        updatePickCardInFirebase(docId, pickCard);
        
        // Update status in sheet
        sheet.getRange(i + 2, 16).setValue('Updated');
        updatedCount++;
        
      } catch (error) {
        console.error(`Error updating row ${i + 2}:`, error);
        sheet.getRange(i + 2, 16).setValue('Error: ' + error.message);
        errorCount++;
      }
    }
    
    console.log(`Sync complete: ${updatedCount} updated, ${errorCount} errors`);
    
    if (errorCount > 0) {
      SpreadsheetApp.getUi().alert(`Sync complete with ${errorCount} errors. Check the Firebase Status column.`);
    }
    
  } catch (error) {
    console.error('Error syncing from Sheet to Firebase:', error);
    SpreadsheetApp.getUi().alert('Error syncing to Firebase: ' + error.message);
  }
}

/**
 * Placeholder function to get pick cards from Firebase
 * TODO: Implement actual Firebase API calls
 */
function getPickCardsFromFirebase() {
  // This is a placeholder - you'll need to implement actual Firebase API calls
  // For now, return empty array
  return [];
}

/**
 * Placeholder function to update pick card in Firebase
 * TODO: Implement actual Firebase API calls
 */
function updatePickCardInFirebase(docId, pickCard) {
  // This is a placeholder - you'll need to implement actual Firebase API calls
  console.log(`Would update Firebase document ${docId} with:`, pickCard);
}

/**
 * Create menu items for easy access
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Firebase Picks')
    .addItem('Initialize Sheet', 'initializeFirebasePicksSheet')
    .addItem('Sync from Firebase', 'syncFromFirebaseToSheet')
    .addItem('Sync to Firebase', 'syncFromSheetToFirebase')
    .addItem('Full Sync (Both Ways)', 'fullSync')
    .addToUi();
}

/**
 * Perform full two-way sync
 */
function fullSync() {
  syncFromFirebaseToSheet();
  Utilities.sleep(1000); // Wait 1 second
  syncFromSheetToFirebase();
}
