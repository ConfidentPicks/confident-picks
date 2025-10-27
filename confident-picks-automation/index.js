// Simple index file for Vercel
module.exports = (req, res) => {
  res.status(200).json({
    message: 'Confident Picks Automation API',
    endpoints: [
      '/api/test',
      '/api/health-check',
      '/api/collect-data',
      '/api/generate-picks',
      '/api/score-games'
    ],
    timestamp: new Date().toISOString()
  });
};




