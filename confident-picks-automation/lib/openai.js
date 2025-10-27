// OpenAI integration for bulk pick generation
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export const openaiClient = {
  // Generate picks in bulk for all NFL games
  async generatePicksBulk(games) {
    try {
      console.log(`🤖 Generating picks for ${games.length} NFL games...`);
      
      // Prepare the prompt with all games and data
      const prompt = this.buildBulkPrompt(games);
      
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `You are an expert NFL analyst. Analyze all provided games and generate betting picks with confidence scores. Only provide picks with 70%+ confidence.`
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 4000
      });
      
      const picks = this.parseAIResponse(response.choices[0].message.content);
      console.log(`✅ Generated ${picks.length} picks`);
      
      return picks;
    } catch (error) {
      console.error('❌ OpenAI pick generation failed:', error);
      throw error;
    }
  },

  // Build comprehensive prompt with all game data
  buildBulkPrompt(games) {
    let prompt = `Analyze these NFL games and generate betting picks with confidence scores (0-100%). Only provide picks with 70%+ confidence.\n\n`;
    
    games.forEach((game, index) => {
      prompt += `Game ${index + 1}: ${game.homeTeam} vs ${game.awayTeam}\n`;
      prompt += `Date: ${game.date}\n`;
      prompt += `Weather: ${game.weather || 'Unknown'}\n`;
      prompt += `Injuries: ${game.injuries || 'None reported'}\n`;
      prompt += `Markets:\n`;
      
      game.markets?.forEach(market => {
        prompt += `  ${market.type}: ${market.selection} (${market.odds})\n`;
      });
      
      prompt += `\n`;
    });
    
    prompt += `\nRespond in JSON format:
    {
      "picks": [
        {
          "game": "Game 1",
          "prediction": "Chiefs -3.5",
          "confidence": 78,
          "reasoning": {
            "primary": "Main analysis",
            "secondary": "Supporting factors",
            "risk_factors": ["Injury concerns"],
            "data_sources": ["DraftKings", "ESPN"]
          },
          "market": "spread",
          "auto_approve": true
        }
      ]
    }`;
    
    return prompt;
  },

  // Parse AI response into structured picks
  parseAIResponse(response) {
    try {
      const parsed = JSON.parse(response);
      return parsed.picks || [];
    } catch (error) {
      console.error('❌ Failed to parse AI response:', error);
      return [];
    }
  },

  // Calculate standard deviation for outlier detection
  calculateStdDev(picks) {
    const confidences = picks.map(pick => pick.confidence);
    const mean = confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length;
    const variance = confidences.reduce((sum, conf) => sum + Math.pow(conf - mean, 2), 0) / confidences.length;
    return Math.sqrt(variance);
  },

  // Flag outliers for manual review
  flagOutliers(picks, stdDevThreshold = 2.0) {
    const stdDev = this.calculateStdDev(picks);
    const mean = picks.reduce((sum, pick) => sum + pick.confidence, 0) / picks.length;
    
    return picks.map(pick => ({
      ...pick,
      isOutlier: Math.abs(pick.confidence - mean) > (stdDevThreshold * stdDev),
      auto_approve: pick.confidence >= 70 && !this.isOutlier(pick, mean, stdDev, stdDevThreshold)
    }));
  }
};

export default openaiClient;