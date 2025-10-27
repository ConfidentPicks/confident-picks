#!/usr/bin/env node

/**
 * NFLReadPy Odds Collector Script
 * 
 * Collects live NFL odds using nflreadpy and updates Google Sheets
 * Much better than external APIs since it's specifically designed for NFL
 */

const { collectLiveOdds } = require('./lib/nflreadpy-collector');

async function main() {
  console.log('\n🎯 Live NFL Odds Collection (nflreadpy)\n');
  
  try {
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Update the live_picks_sheets sheet with current odds
    // (using your existing sheet instead of creating a new one)
    const result = await collectLiveOdds(spreadsheetId, 'live_picks_sheets');
    
    if (result.success) {
      console.log('\n🎉 Odds collection completed successfully!');
      console.log(`📊 Updated ${result.rowCount} rows of odds data`);
      console.log('\n💡 Your Live_Odds sheet now has the most current NFL odds');
      console.log('   Use this data in other sheets for predictions and pick display');
    } else {
      console.log('\n⚠️ Odds collection completed with issues');
      console.log(`   Message: ${result.message}`);
    }
    
  } catch (error) {
    console.error('\n❌ Odds collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure Python is installed');
    console.log('2. Install nflreadpy: pip install nflreadpy');
    console.log('3. Check internet connection');
    console.log('4. Verify Google Sheets API is enabled');
    console.log('5. Check that the sheet is shared with service account');
  }
}

main();
