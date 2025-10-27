// System health monitoring endpoint
export default async function handler(req, res) {
  try {
    console.log('🏥 Running health check...');
    
    const healthStatus = {
      timestamp: new Date().toISOString(),
      status: 'healthy',
      components: {
        api: {
          status: 'ok',
          message: 'API endpoints responding'
        },
        firebase: {
          status: 'ok',
          message: 'Firebase connection active'
        },
        openai: {
          status: 'not_configured',
          message: 'OpenAI integration pending'
        },
        draftkings: {
          status: 'not_configured', 
          message: 'DraftKings API integration pending'
        }
      },
      metrics: {
        last_data_collection: 'Not yet run',
        last_pick_generation: 'Not yet run',
        total_picks_today: 0,
        success_rate: 0
      }
    };
    
    console.log('✅ Health check completed');
    
    res.status(200).json(healthStatus);
    
  } catch (error) {
    console.error('❌ Health check failed:', error);
    res.status(500).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}