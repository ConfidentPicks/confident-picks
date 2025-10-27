#!/usr/bin/env node

/**
 * NFL Historical Data Downloader
 * 
 * Downloads 3-5 years of NFL data (2021-2024) for model building
 * This creates separate sheets for each year and data type
 */

const { downloadHistoricalData } = require('./lib/nfl-data-collector');

async function main() {
  console.log('\n🏈 NFL Historical Data Download\n');
  
  try {
    // Download data for years 2021-2024
    const years = [2021, 2022, 2023, 2024];
    
    console.log(`📅 Downloading data for years: ${years.join(', ')}`);
    console.log('📊 This will create separate sheets for each year and data type');
    console.log('\n⏳ This may take several minutes...');
    
    const result = await downloadHistoricalData(years);
    
    if (result.success) {
      console.log('\n🎉 Historical data download completed successfully!');
      console.log(`📊 Processed ${result.yearsProcessed} years of data`);
      console.log('\n📋 Your Google Sheet now has:');
      console.log('   - NFL_Schedule_2021, NFL_Schedule_2022, etc.');
      console.log('   - NFL_TeamStats_2021, NFL_TeamStats_2022, etc.');
      console.log('\n💡 Use this data to:');
      console.log('   - Build prediction models');
      console.log('   - Analyze historical trends');
      console.log('   - Validate your picks against past performance');
      console.log('   - Create statistical models for betting');
    } else {
      console.log('\n⚠️ Historical data download completed with issues');
    }
    
  } catch (error) {
    console.error('\n❌ Historical data download failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check internet connection');
    console.log('2. Verify SportsData API key is set');
    console.log('3. Make sure Google Sheets API is enabled');
    console.log('4. Check that the sheet is shared with service account');
    console.log('5. Ensure you have sufficient API quota');
  }
}

main();



