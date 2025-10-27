#!/usr/bin/env node

/**
 * Odds Collector Script
 * 
 * Collects live betting odds and updates Google Sheets
 * Run this regularly to keep odds data current
 */

const { collectAndUpdateOdds } = require('./lib/odds-collector');

async function main() {
  console.log('\n🎯 Live Odds Collection\n');
  
  try {
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Update the Live_Odds sheet with current odds
    const result = await collectAndUpdateOdds(spreadsheetId, 'Live_Odds');
    
    if (result.success) {
      console.log('\n🎉 Odds collection completed successfully!');
      console.log(`📊 Updated ${result.rowCount} rows of odds data`);
      console.log('\n💡 Your Live_Odds sheet now has the most current betting odds');
      console.log('   Use this data in other sheets for predictions and pick display');
    } else {
      console.log('\n⚠️ Odds collection completed with issues');
      console.log(`   Message: ${result.message}`);
    }
    
  } catch (error) {
    console.error('\n❌ Odds collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check internet connection');
    console.log('2. Verify API keys are set in environment variables');
    console.log('3. Make sure Google Sheets API is enabled');
    console.log('4. Check that the sheet is shared with service account');
  }
}

main();



