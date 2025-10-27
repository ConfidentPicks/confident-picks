/**
 * Vercel Serverless Function: Auto Sync Google Sheets to Firebase
 * 
 * This runs automatically on a schedule via Vercel cron jobs
 * 
 * Schedule: Every 6 hours (0 */6 * * *)
 */

const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { google } = require('googleapis');

// Initialize Firebase Admin (singleton)
let app;
let db;

function initializeFirebase() {
  if (app) return db;
  
  const credentials = {
    type: 'service_account',
    project_id: process.env.FIREBASE_PROJECT_ID,
    private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
    private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    client_email: process.env.FIREBASE_CLIENT_EMAIL,
    client_id: process.env.FIREBASE_CLIENT_ID,
    auth_uri: 'https://accounts.google.com/o/oauth2/auth',
    token_uri: 'https://oauth2.googleapis.com/token',
    auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
    client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${encodeURIComponent(process.env.FIREBASE_CLIENT_EMAIL)}`,
  };
  
  app = initializeApp({
    credential: cert(credentials),
  });
  
  db = getFirestore(app);
  return db;
}

module.exports = async (req, res) => {
  const startTime = Date.now();
  
  try {
    console.log('🔄 Starting automatic Google Sheets → Firebase sync...');
    
    // Validate environment variables
    if (!process.env.GOOGLE_SHEETS_SPREADSHEET_ID) {
      throw new Error('GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set');
    }
    
    if (!process.env.FIREBASE_PROJECT_ID || !process.env.FIREBASE_PRIVATE_KEY) {
      throw new Error('Firebase credentials not properly configured');
    }
    
    // Initialize services
    const db = initializeFirebase();
    
    const credentials = {
      type: 'service_account',
      project_id: process.env.FIREBASE_PROJECT_ID,
      private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
      client_id: process.env.FIREBASE_CLIENT_ID,
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
      client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${encodeURIComponent(process.env.FIREBASE_CLIENT_EMAIL)}`,
    };
    
    const auth = new google.auth.GoogleAuth({
      credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });
    
    const sheetsClient = google.sheets({ version: 'v4', auth });
    
    // Read data from Google Sheet
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: process.env.GOOGLE_SHEETS_SPREADSHEET_ID,
      range: 'A1:Z100',
    });
    
    const rows = response.data.values;
    if (!rows || rows.length < 2) {
      return res.status(200).json({
        success: true,
        message: 'No data to sync',
        pickCount: 0,
        duration: `${Date.now() - startTime}ms`,
        timestamp: new Date().toISOString(),
      });
    }
    
    // Process rows
    const headers = rows[0];
    const dataRows = rows.slice(1);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (const row of dataRows) {
      try {
        const pick = {};
        headers.forEach((header, index) => {
          const value = row[index] || '';
          
          switch (header.toLowerCase()) {
            case 'id':
              pick.id = value;
              break;
            case 'league':
              pick.league = value;
              break;
            case 'game':
              pick.game = value;
              if (value.includes(' vs ')) {
                const [home, away] = value.split(' vs ');
                pick.homeTeam = home.trim();
                pick.awayTeam = away.trim();
              }
              break;
            case 'pick':
              pick.pick = value;
              break;
            case 'market type':
              pick.marketType = value;
              break;
            case 'odds':
              pick.odds = value ? parseFloat(value) || value : '';
              break;
            case 'confidence':
              pick.modelConfidence = value ? parseFloat(value) || 0 : 0;
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
        
        pick.updatedAt = new Date().toISOString();
        pick.source = 'auto-sync';
        
        if (pick.id) {
          await db.collection('live_picks').doc(pick.id).set(pick, { merge: true });
          successCount++;
        }
        
      } catch (error) {
        console.error('Error processing row:', error);
        errorCount++;
      }
    }
    
    const duration = Date.now() - startTime;
    
    console.log(`✅ Auto-sync completed: ${successCount} updated, ${errorCount} errors`);
    
    return res.status(200).json({
      success: true,
      message: 'Automatic sync completed',
      pickCount: successCount,
      errorCount,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('❌ Auto-sync failed:', error);
    
    const duration = Date.now() - startTime;
    
    return res.status(500).json({
      success: false,
      error: error.message,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
  }
};



