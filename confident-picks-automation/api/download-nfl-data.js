/**
 * Vercel Serverless Function: Download NFL Historical Data
 * 
 * POST /api/download-nfl-data
 * 
 * Downloads historical NFL data for model building
 */

const { downloadHistoricalData } = require('../lib/nfl-data-collector');

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
    console.log('🔄 Starting NFL historical data download...');
    
    // Get years from request body or use default
    const years = req.body?.years || [2021, 2022, 2023, 2024];
    
    // Download historical data
    const result = await downloadHistoricalData(years);
    
    const duration = Date.now() - startTime;
    
    console.log(`✅ NFL data download completed in ${duration}ms`);
    
    return res.status(200).json({
      success: true,
      message: 'NFL historical data downloaded',
      yearsProcessed: result.yearsProcessed,
      years,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('❌ NFL data download failed:', error);
    
    const duration = Date.now() - startTime;
    
    return res.status(500).json({
      success: false,
      error: error.message,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
  }
};



