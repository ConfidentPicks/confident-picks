// DraftKings API wrapper
import axios from 'axios';

const DRAFTKINGS_BASE_URL = 'https://sportsbook.draftkings.com/api/v2';

export const draftkings = {
  // Fetch all NFL games
  async fetchNFLGames() {
    try {
      console.log('🏈 Fetching NFL games from DraftKings...');
      
      const response = await axios.get(`${DRAFTKINGS_BASE_URL}/sports/nfl/events`);
      const games = response.data.events || [];
      
      console.log(`✅ Found ${games.length} NFL games`);
      return games;
    } catch (error) {
      console.error('❌ Failed to fetch NFL games:', error);
      throw error;
    }
  },

  // Fetch all markets for a specific game
  async fetchNFLMarkets(gameId) {
    try {
      console.log(`📊 Fetching markets for game ${gameId}...`);
      
      const response = await axios.get(`${DRAFTKINGS_BASE_URL}/events/${gameId}/markets`);
      const markets = response.data.markets || [];
      
      console.log(`✅ Found ${markets.length} markets for game ${gameId}`);
      return markets;
    } catch (error) {
      console.error(`❌ Failed to fetch markets for game ${gameId}:`, error);
      throw error;
    }
  },

  // Fetch current odds for a market
  async fetchOdds(marketId) {
    try {
      const response = await axios.get(`${DRAFTKINGS_BASE_URL}/markets/${marketId}`);
      return response.data;
    } catch (error) {
      console.error(`❌ Failed to fetch odds for market ${marketId}:`, error);
      throw error;
    }
  },

  // Get ALL available NFL props and markets
  async getAllNFLProps() {
    try {
      console.log('🎯 Fetching all NFL props from DraftKings...');
      
      const games = await this.fetchNFLGames();
      const allProps = [];
      
      for (const game of games) {
        try {
          const markets = await this.fetchNFLMarkets(game.id);
          
          markets.forEach(market => {
            allProps.push({
              gameId: game.id,
              gameName: `${game.awayTeam} vs ${game.homeTeam}`,
              marketType: market.type,
              marketName: market.name,
              selections: market.selections || [],
              odds: market.odds || {},
              startTime: game.startTime
            });
          });
        } catch (error) {
          console.warn(`⚠️ Failed to fetch markets for game ${game.id}:`, error.message);
        }
      }
      
      console.log(`✅ Collected ${allProps.length} total props`);
      return allProps;
    } catch (error) {
      console.error('❌ Failed to fetch all NFL props:', error);
      throw error;
    }
  },

  // Get injury reports from multiple sources
  async fetchInjuryReports() {
    try {
      console.log('🏥 Fetching injury reports...');
      
      // TODO: Implement injury report scraping from:
      // - ESPN NFL injuries
      // - NFL.com injury reports
      // - Team official websites
      
      const mockInjuries = [
        {
          team: 'Chiefs',
          player: 'Travis Kelce',
          injury: 'Ankle',
          status: 'Questionable',
          impact: 'Medium'
        }
      ];
      
      console.log(`✅ Found ${mockInjuries.length} injury reports`);
      return mockInjuries;
    } catch (error) {
      console.error('❌ Failed to fetch injury reports:', error);
      return [];
    }
  },

  // Get weather data for outdoor games
  async fetchWeatherData(games) {
    try {
      console.log('🌤️ Fetching weather data...');
      
      // TODO: Implement weather API integration
      // - OpenWeatherMap API
      // - Weather.gov API
      // Focus on outdoor stadiums
      
      const mockWeather = games.map(game => ({
        gameId: game.id,
        temperature: 65,
        conditions: 'Partly Cloudy',
        windSpeed: 8,
        precipitation: 0,
        impact: 'Low'
      }));
      
      console.log(`✅ Weather data collected for ${mockWeather.length} games`);
      return mockWeather;
    } catch (error) {
      console.error('❌ Failed to fetch weather data:', error);
      return [];
    }
  }
};

export default draftkings;