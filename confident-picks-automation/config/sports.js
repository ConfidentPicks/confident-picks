// Sport-specific configuration
export const NFL_CONFIG = {
  enabled: true,
  confidence_threshold: 0.70,
  markets: ['spread', 'totals', 'props', 'player_props'],
  data_sources: [
    'draftkings',
    'espn_injuries',
    'nfl_injuries',
    'weather_api'
  ],
  update_frequency: '6h',
  auto_approve: true,
  max_picks_per_day: 50,
  markets_to_analyze: [
    'spread',
    'moneyline', 
    'total_points',
    'player_props',
    'team_props'
  ]
};

export const NHL_CONFIG = {
  enabled: false, // Will be enabled after NFL is working
  confidence_threshold: 0.70,
  markets: ['spread', 'totals', 'props'],
  data_sources: [
    'draftkings',
    'nhl_injuries',
    'weather_api'
  ],
  update_frequency: '6h',
  auto_approve: true,
  max_picks_per_day: 30
};

export const CBB_CONFIG = {
  enabled: false, // Will be enabled after NHL
  confidence_threshold: 0.70,
  markets: ['spread', 'totals', 'props'],
  data_sources: [
    'draftkings',
    'espn_injuries'
  ],
  update_frequency: '12h',
  auto_approve: true,
  max_picks_per_day: 40
};

export const CFB_CONFIG = {
  enabled: false, // Will be enabled after CBB
  confidence_threshold: 0.70,
  markets: ['spread', 'totals', 'props'],
  data_sources: [
    'draftkings',
    'espn_injuries',
    'weather_api'
  ],
  update_frequency: '12h',
  auto_approve: true,
  max_picks_per_day: 35
};

// Export all configs
export const SPORTS_CONFIG = {
  nfl: NFL_CONFIG,
  nhl: NHL_CONFIG,
  cbb: CBB_CONFIG,
  cfb: CFB_CONFIG
};

export default SPORTS_CONFIG;