// Confidence thresholds and quality control settings
export const THRESHOLDS = {
  auto_approve_confidence: 0.70,
  manual_review_confidence: 0.60,
  reject_confidence: 0.50,
  outlier_std_dev: 2.0,
  max_picks_per_day: 100,
  min_confidence_for_analysis: 0.65
};

export const QUALITY_CONTROL = {
  enable_outlier_detection: true,
  enable_confidence_filtering: true,
  enable_data_validation: true,
  enable_duplicate_detection: true,
  max_picks_per_game: 5,
  max_same_market_picks: 2
};

export const COST_LIMITS = {
  max_openai_requests_per_day: 100,
  max_draftkings_requests_per_day: 1000,
  max_firebase_operations_per_day: 10000,
  estimated_monthly_cost_usd: 200
};

export default {
  THRESHOLDS,
  QUALITY_CONTROL,
  COST_LIMITS
};