// Google Sheets Integration for Confident Picks
// Connects Firebase service account with Google Sheets API

const { google } = require('googleapis');

/**
 * Initialize Google Sheets API client using Firebase service account
 * @param {Object} credentials - Service account credentials from Firebase
 * @returns {Object} Google Sheets API client
 */
function initializeSheetsClient(credentials) {
  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        type: credentials.type,
        project_id: credentials.project_id,
        private_key_id: credentials.private_key_id,
        private_key: credentials.private_key,
        client_email: credentials.client_email,
        client_id: credentials.client_id,
        auth_uri: credentials.auth_uri,
        token_uri: credentials.token_uri,
        auth_provider_x509_cert_url: credentials.auth_provider_x509_cert_url,
        client_x509_cert_url: credentials.client_x509_cert_url,
      },
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
      ],
    });

    return google.sheets({ version: 'v4', auth });
  } catch (error) {
    console.error('Error initializing Google Sheets client:', error);
    throw error;
  }
}

/**
 * Read data from a Google Sheet
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} range - The A1 notation of the range to retrieve (e.g., 'Sheet1!A1:D10')
 * @returns {Array} Array of rows
 */
async function readSheet(sheetsClient, spreadsheetId, range) {
  try {
    // Escape sheet name if it contains special characters
    let escapedRange = range;
    if (range.includes('!')) {
      const [sheetName, cellRange] = range.split('!');
      // If sheet name contains special characters, wrap it in single quotes
      if (sheetName.includes('_') || sheetName.includes(' ') || sheetName.includes('-')) {
        escapedRange = `'${sheetName}'!${cellRange}`;
      }
    }
    
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId,
      range: escapedRange,
    });
    
    const rows = response.data.values;
    if (!rows || rows.length === 0) {
      console.log('No data found in sheet');
      return [];
    }
    
    console.log(`✅ Read ${rows.length} rows from Google Sheet`);
    return rows;
  } catch (error) {
    console.error('Error reading from Google Sheet:', error.message);
    throw error;
  }
}

/**
 * Write data to a Google Sheet
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} range - The A1 notation of the range to write (e.g., 'Sheet1!A1')
 * @param {Array} values - 2D array of values to write
 * @returns {Object} Update response
 */
async function writeSheet(sheetsClient, spreadsheetId, range, values) {
  try {
    // Escape sheet name if it contains special characters
    let escapedRange = range;
    if (range.includes('!')) {
      const [sheetName, cellRange] = range.split('!');
      // If sheet name contains special characters, wrap it in single quotes
      if (sheetName.includes('_') || sheetName.includes(' ') || sheetName.includes('-')) {
        escapedRange = `'${sheetName}'!${cellRange}`;
      }
    }
    
    const response = await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: escapedRange,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values,
      },
    });
    
    console.log(`✅ Updated ${response.data.updatedCells} cells in Google Sheet`);
    return response.data;
  } catch (error) {
    console.error('Error writing to Google Sheet:', error.message);
    throw error;
  }
}

/**
 * Append data to a Google Sheet
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} range - The A1 notation of the range to append (e.g., 'Sheet1!A1')
 * @param {Array} values - 2D array of values to append
 * @returns {Object} Append response
 */
async function appendSheet(sheetsClient, spreadsheetId, range, values) {
  try {
    const response = await sheetsClient.spreadsheets.values.append({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      insertDataOption: 'INSERT_ROWS',
      resource: {
        values,
      },
    });
    
    console.log(`✅ Appended ${response.data.updates.updatedRows} rows to Google Sheet`);
    return response.data;
  } catch (error) {
    console.error('Error appending to Google Sheet:', error.message);
    throw error;
  }
}

/**
 * Clear data in a Google Sheet range
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} range - The A1 notation of the range to clear (e.g., 'Sheet1!A1:D10')
 * @returns {Object} Clear response
 */
async function clearSheet(sheetsClient, spreadsheetId, range) {
  try {
    // Escape sheet name if it contains special characters
    let escapedRange = range;
    if (range.includes('!')) {
      const [sheetName, cellRange] = range.split('!');
      // If sheet name contains special characters, wrap it in single quotes
      if (sheetName.includes('_') || sheetName.includes(' ') || sheetName.includes('-')) {
        escapedRange = `'${sheetName}'!${cellRange}`;
      }
    }
    
    const response = await sheetsClient.spreadsheets.values.clear({
      spreadsheetId,
      range: escapedRange,
    });
    
    console.log(`✅ Cleared range ${escapedRange} in Google Sheet`);
    return response.data;
  } catch (error) {
    console.error('Error clearing Google Sheet:', error.message);
    throw error;
  }
}

/**
 * Create a new spreadsheet
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {string} title - Title of the new spreadsheet
 * @returns {Object} New spreadsheet metadata
 */
async function createSpreadsheet(sheetsClient, title) {
  try {
    const response = await sheetsClient.spreadsheets.create({
      resource: {
        properties: {
          title,
        },
      },
    });
    
    console.log(`✅ Created new spreadsheet: ${response.data.spreadsheetId}`);
    return response.data;
  } catch (error) {
    console.error('Error creating spreadsheet:', error.message);
    throw error;
  }
}

/**
 * Convert picks data to Google Sheets format
 * @param {Array} picks - Array of pick objects from Firebase
 * @returns {Array} 2D array formatted for Google Sheets
 */
function picksToSheetFormat(picks) {
  const headers = [
    'ID',
    'League',
    'Game',
    'Pick',
    'Market Type',
    'Odds',
    'Confidence',
    'Tier',
    'Status',
    'Result',
    'Commence Time',
    'Reasoning'
  ];
  
  const rows = picks.map(pick => [
    pick.id || '',
    pick.league || '',
    `${pick.homeTeam} vs ${pick.awayTeam}` || '',
    pick.pick || '',
    pick.marketType || '',
    pick.odds || '',
    pick.modelConfidence || '',
    pick.tier || '',
    pick.status || '',
    pick.result || '',
    pick.commenceTime ? new Date(pick.commenceTime).toLocaleString() : '',
    pick.reasoning || ''
  ]);
  
  return [headers, ...rows];
}

/**
 * Convert Google Sheets data to picks format
 * @param {Array} rows - 2D array from Google Sheets
 * @returns {Array} Array of pick objects
 */
function sheetFormatToPicks(rows) {
  if (!rows || rows.length < 2) {
    return [];
  }
  
  const headers = rows[0];
  const dataRows = rows.slice(1);
  
  return dataRows.map(row => {
    const pick = {};
    headers.forEach((header, index) => {
      const value = row[index] || '';
      
      // Map sheet columns to pick properties
      switch (header.toLowerCase()) {
        case 'id':
          pick.id = value;
          break;
        case 'league':
          pick.league = value;
          break;
        case 'pick':
          pick.pick = value;
          break;
        case 'market type':
          pick.marketType = value;
          break;
        case 'odds':
          pick.odds = parseFloat(value) || value;
          break;
        case 'confidence':
          pick.modelConfidence = parseFloat(value) || 0;
          break;
        case 'tier':
          pick.tier = value;
          break;
        case 'status':
          pick.status = value;
          break;
        case 'result':
          pick.result = value;
          break;
        case 'reasoning':
          pick.reasoning = value;
          break;
        default:
          pick[header] = value;
      }
    });
    
    return pick;
  });
}

/**
 * Sync Firebase picks to Google Sheets
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {Object} firebaseDb - Firebase Firestore instance
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} sheetName - Name of the sheet tab (default: 'Picks')
 */
async function syncFirebaseToSheets(sheetsClient, firebaseDb, spreadsheetId, sheetName = 'Picks') {
  try {
    console.log('🔄 Syncing Firebase picks to Google Sheets...');
    
    // Get picks from Firebase
    const picksSnapshot = await firebaseDb.collection('live_picks').get();
    const picks = [];
    picksSnapshot.forEach(doc => {
      picks.push({ id: doc.id, ...doc.data() });
    });
    
    console.log(`📊 Found ${picks.length} picks in Firebase`);
    
    // Convert to sheet format
    const sheetData = picksToSheetFormat(picks);
    
    // Calculate the range needed based on actual data
    const numRows = sheetData.length;
    const numCols = sheetData.length > 0 ? sheetData[0].length : 12;
    const endCol = String.fromCharCode(64 + numCols); // Convert to letter (A, B, C, etc.)
    const range = `${sheetName}!A1:${endCol}${Math.max(numRows, 100)}`;
    
    console.log(`📝 Writing ${numRows} rows x ${numCols} columns to range: ${range}`);
    
    // Clear existing data and write new data
    try {
      await clearSheet(sheetsClient, spreadsheetId, range);
    } catch (clearError) {
      console.log('⚠️ Could not clear sheet (might be empty), continuing...');
    }
    
    await writeSheet(sheetsClient, spreadsheetId, `${sheetName}!A1`, sheetData);
    
    console.log(`✅ Successfully synced ${picks.length} picks to Google Sheets`);
    return { success: true, pickCount: picks.length };
  } catch (error) {
    console.error('❌ Error syncing to Google Sheets:', error.message);
    throw error;
  }
}

/**
 * Import picks from Google Sheets to Firebase
 * @param {Object} sheetsClient - Google Sheets API client
 * @param {Object} firebaseDb - Firebase Firestore instance
 * @param {string} spreadsheetId - The ID of the spreadsheet
 * @param {string} sheetName - Name of the sheet tab
 * @param {string} collection - Firebase collection name (default: 'qa_picks')
 */
async function importSheetsToFirebase(sheetsClient, firebaseDb, spreadsheetId, sheetName = 'Picks', collection = 'qa_picks') {
  try {
    console.log('🔄 Importing picks from Google Sheets to Firebase...');
    
    // Read data from sheet
    const rows = await readSheet(sheetsClient, spreadsheetId, `${sheetName}!A:Z`);
    
    if (rows.length < 2) {
      console.log('⚠️ No data to import');
      return { success: false, message: 'No data found' };
    }
    
    // Convert to picks format
    const picks = sheetFormatToPicks(rows);
    
    console.log(`📊 Found ${picks.length} picks in Google Sheet`);
    
    // Upload to Firebase
    const batch = firebaseDb.batch();
    let uploadCount = 0;
    
    for (const pick of picks) {
      if (pick.id) {
        const docRef = firebaseDb.collection(collection).doc(pick.id);
        batch.set(docRef, {
          ...pick,
          updatedAt: new Date().toISOString(),
          source: 'google-sheets-import'
        }, { merge: true });
        uploadCount++;
      }
    }
    
    await batch.commit();
    
    console.log(`✅ Successfully imported ${uploadCount} picks to Firebase`);
    return { success: true, pickCount: uploadCount };
  } catch (error) {
    console.error('❌ Error importing from Google Sheets:', error.message);
    throw error;
  }
}

module.exports = {
  initializeSheetsClient,
  readSheet,
  writeSheet,
  appendSheet,
  clearSheet,
  createSpreadsheet,
  picksToSheetFormat,
  sheetFormatToPicks,
  syncFirebaseToSheets,
  importSheetsToFirebase,
};

