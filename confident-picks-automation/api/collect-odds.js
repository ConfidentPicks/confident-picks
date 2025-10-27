/**
 * Vercel Serverless Function: Collect Live Odds
 * 
 * POST /api/collect-odds
 * 
 * Automatically collects live betting odds and updates Google Sheets
 */

const { collectAndUpdateOdds } = require('../lib/odds-collector');

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const startTime = Date.now();
  
  try {
    console.log('🔄 Starting live odds collection...');
    
    // Validate environment variables
    if (!process.env.GOOGLE_SHEETS_SPREADSHEET_ID) {
      throw new Error('GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set');
    }
    
    // Collect and update odds
    const result = await collectAndUpdateOdds(
      process.env.GOOGLE_SHEETS_SPREADSHEET_ID,
      'Live_Odds'
    );
    
    const duration = Date.now() - startTime;
    
    console.log(`✅ Odds collection completed in ${duration}ms`);
    
    return res.status(200).json({
      success: true,
      message: 'Live odds collected and updated',
      rowCount: result.rowCount,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('❌ Odds collection failed:', error);
    
    const duration = Date.now() - startTime;
    
    return res.status(500).json({
      success: false,
      error: error.message,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
  }
};



