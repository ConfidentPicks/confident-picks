#!/usr/bin/env node

const fs = require('fs');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));

const app = initializeApp({ credential: cert(credentials) });
const db = getFirestore(app);

async function checkTonightsGames() {
  console.log('\n🏈 TONIGHT\'S NFL GAMES\n');
  console.log('='  .repeat(70));
  
  // Get today's date
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0]; // YYYY-MM-DD
  
  console.log(`📅 Checking for games on: ${todayStr}\n`);
  
  // Check live_picks collection
  const liveSnapshot = await db.collection('live_picks').get();
  
  const tonightsGames = [];
  
  liveSnapshot.forEach(doc => {
    const pick = doc.data();
    
    // Check if gameTime matches today
    if (pick.gameTime && pick.gameTime.includes(todayStr)) {
      tonightsGames.push({
        id: doc.id,
        ...pick
      });
    }
  });
  
  if (tonightsGames.length === 0) {
    console.log('❌ No games found for tonight in live_picks\n');
    console.log('Let me check all collections...\n');
    
    // Check upcoming_picks
    const upcomingSnapshot = await db.collection('upcoming_picks').get();
    upcomingSnapshot.forEach(doc => {
      const pick = doc.data();
      if (pick.gameTime && pick.gameTime.includes(todayStr)) {
        tonightsGames.push({
          id: doc.id,
          collection: 'upcoming_picks',
          ...pick
        });
      }
    });
    
    if (tonightsGames.length === 0) {
      console.log('❌ No games found for tonight in any collection\n');
      return;
    }
  }
  
  // Group by game
  const gameMap = new Map();
  
  tonightsGames.forEach(pick => {
    if (!gameMap.has(pick.gameId)) {
      gameMap.set(pick.gameId, {
        gameId: pick.gameId,
        awayTeam: pick.awayTeam,
        homeTeam: pick.homeTeam,
        gameTime: pick.gameTime,
        picks: []
      });
    }
    
    gameMap.get(pick.gameId).picks.push(pick);
  });
  
  console.log(`✅ Found ${gameMap.size} game(s) for tonight:\n`);
  
  // Display each game
  gameMap.forEach((game, gameId) => {
    console.log('=' .repeat(70));
    console.log(`🏈 ${game.awayTeam} @ ${game.homeTeam}`);
    console.log(`📅 ${game.gameTime}`);
    console.log('-' .repeat(70));
    
    game.picks.forEach(pick => {
      console.log(`\n${pick.marketType.toUpperCase()}:`);
      console.log(`   Pick: ${pick.pick}`);
      console.log(`   Description: ${pick.pickDesc}`);
      console.log(`   Confidence: ${pick.modelConfidence}%`);
      console.log(`   Risk: ${pick.riskTag}`);
      console.log(`   Odds: ${pick.odds}`);
      if (pick.collection) {
        console.log(`   Collection: ${pick.collection}`);
      }
    });
    
    console.log();
  });
  
  console.log('=' .repeat(70) + '\n');
}

checkTonightsGames()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });


