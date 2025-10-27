#!/usr/bin/env node

const fs = require('fs');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));

const app = initializeApp({ credential: cert(credentials) });
const db = getFirestore(app);

async function showLiveGames() {
  console.log('\n🏈 LIVE GAMES WITH PREDICTIONS\n');
  console.log('='  .repeat(70));
  
  // Check live_picks collection
  const liveSnapshot = await db.collection('live_picks').get();
  
  const allPicks = [];
  
  liveSnapshot.forEach(doc => {
    const pick = doc.data();
    allPicks.push({
      id: doc.id,
      ...pick
    });
  });
  
  console.log(`✅ Found ${allPicks.length} total picks in live_picks\n`);
  
  // Group by game
  const gameMap = new Map();
  
  allPicks.forEach(pick => {
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
  
  // Sort games by date
  const sortedGames = Array.from(gameMap.values()).sort((a, b) => {
    return new Date(a.gameTime) - new Date(b.gameTime);
  });
  
  console.log(`📊 ${sortedGames.length} games in live_picks collection\n`);
  
  // Show first 5 games
  const gamesToShow = sortedGames.slice(0, 5);
  
  console.log('🔮 NEXT 5 GAMES WITH PREDICTIONS:\n');
  
  gamesToShow.forEach((game, idx) => {
    const gameDate = new Date(game.gameTime);
    const dateStr = gameDate.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
    
    console.log('=' .repeat(70));
    console.log(`${idx + 1}. ${game.awayTeam} @ ${game.homeTeam}`);
    console.log(`   📅 ${dateStr}`);
    console.log('-' .repeat(70));
    
    // Group picks by market type
    const moneyline = game.picks.find(p => p.marketType === 'moneyline');
    const spread = game.picks.find(p => p.marketType === 'spread');
    const total = game.picks.find(p => p.marketType === 'totals');
    
    if (moneyline) {
      console.log(`   💰 WINNER: ${moneyline.pick} (${moneyline.modelConfidence}% confidence)`);
    }
    
    if (spread) {
      console.log(`   📊 SPREAD: ${spread.pickDesc} (${spread.modelConfidence}% confidence)`);
    }
    
    if (total) {
      console.log(`   🎯 TOTAL: ${total.pickDesc} (${total.modelConfidence}% confidence)`);
    }
    
    console.log();
  });
  
  console.log('=' .repeat(70) + '\n');
}

showLiveGames()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });


