# Confident Picks Automation System

Automated sports pick generation system for Confident Picks platform. This system collects data from DraftKings, processes it with OpenAI, and generates high-confidence picks for your existing Firebase/admin dashboard.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- Vercel account
- Firebase project with service account
- OpenAI API key
- DraftKings API access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd confident-picks-automation
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env.local
   
   # Edit with your values
   nano .env.local
   ```

4. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

## 📁 Project Structure

```
confident-picks-automation/
├── api/                    # Vercel serverless functions
│   ├── collect-data.js     # Data collection from DraftKings
│   ├── generate-picks.js   # AI pick generation
│   ├── score-games.js      # Auto-scoring completed games
│   ├── health-check.js     # System monitoring
│   ├── sync-to-sheets.js   # Sync Firebase → Google Sheets
│   └── import-from-sheets.js # Import Google Sheets → Firebase
├── lib/                    # Core libraries
│   ├── firebase.js         # Firebase integration
│   ├── openai.js           # OpenAI bulk processing
│   ├── draftkings.js       # DraftKings API wrapper
│   ├── google-sheets.js    # Google Sheets integration
│   └── utils.js            # Helper functions
├── config/                 # Configuration files
│   ├── sports.js           # Sport-specific settings
│   └── thresholds.js       # Global thresholds
├── docs/                   # Documentation
│   ├── API.md              # API documentation
│   ├── TROUBLESHOOTING.md  # Common issues & solutions
│   ├── DEPLOYMENT.md       # Deployment procedures
│   └── GOOGLE_SHEETS.md    # Google Sheets integration guide
├── vercel.json             # Vercel configuration
├── package.json            # Dependencies
├── QUICK_START.md          # Quick start guide
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file with the following variables:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Google Sheets Configuration
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_SHEETS_SHEET_NAME=Picks

# DraftKings Configuration (if needed)
DRAFTKINGS_API_KEY=your-draftkings-api-key

# Slack Notifications (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url

# Environment
NODE_ENV=production
```

### Sport Configuration

Edit `config/sports.js` to enable/disable sports and adjust settings:

```javascript
export const NFL_CONFIG = {
  enabled: true,                    // Enable/disable sport
  confidence_threshold: 0.70,       // Minimum confidence for picks
  markets: ['spread', 'totals'],    // Available markets
  auto_approve: true,               // Auto-approve high confidence picks
  max_picks_per_day: 50            // Daily pick limit
};
```

## 🔄 Automation Schedule

The system runs on the following schedule:

- **Data Collection**: Every 6 hours (`0 */6 * * *`)
- **Pick Generation**: 30 minutes after data collection (`30 */6 * * *`)
- **Auto-Scoring**: Every hour (`0 * * * *`)
- **Health Checks**: Every 30 minutes (`*/30 * * * *`)

## 📊 API Endpoints

### Data Collection
- **Endpoint**: `/api/collect-data`
- **Method**: POST
- **Purpose**: Collect fresh data from DraftKings and external sources
- **Schedule**: Every 6 hours

### Pick Generation
- **Endpoint**: `/api/generate-picks`
- **Method**: POST
- **Purpose**: Generate picks using AI analysis
- **Schedule**: 30 minutes after data collection

### Auto-Scoring
- **Endpoint**: `/api/score-games`
- **Method**: POST
- **Purpose**: Score completed games and mark picks as hit/miss
- **Schedule**: Every hour

### Health Check
- **Endpoint**: `/api/health-check`
- **Method**: GET/POST
- **Purpose**: Monitor system health and send alerts
- **Schedule**: Every 30 minutes

### Google Sheets Sync
- **Endpoint**: `/api/sync-to-sheets`
- **Method**: POST
- **Purpose**: Export Firebase picks to Google Sheets
- **Schedule**: On-demand or automated

### Google Sheets Import
- **Endpoint**: `/api/import-from-sheets`
- **Method**: POST
- **Purpose**: Import picks from Google Sheets to Firebase
- **Schedule**: On-demand

## 🎯 Pick Generation Process

1. **Data Collection**: Gather games, odds, and market data from DraftKings
2. **AI Analysis**: Process data with OpenAI GPT-4 to generate picks
3. **Quality Control**: Apply confidence thresholds and outlier detection
4. **Categorization**: Auto-approve high confidence picks, queue others for review
5. **Storage**: Store picks in Firebase collections (live_picks or qa_picks)

## 📈 Quality Control

The system includes several quality control measures:

- **Confidence Thresholds**: Only picks with 70%+ confidence are generated
- **Outlier Detection**: Statistical analysis to identify unusual picks
- **Data Validation**: Comprehensive validation of all pick data
- **Conflict Resolution**: Detection and handling of conflicting information
- **Cost Monitoring**: Real-time tracking of API usage and costs

## 🔍 Monitoring & Alerts

### Health Monitoring
- Firebase connection status
- OpenAI API availability
- DraftKings API health
- Data freshness checks
- Recent activity analysis
- Cost tracking

### Slack Alerts
Configure Slack webhook for real-time notifications:
- System errors and failures
- High error rates
- Cost threshold breaches
- Data freshness issues
- Daily performance summaries

## 💰 Cost Management

### Estimated Monthly Costs
- **OpenAI GPT-4**: ~$58.50/month (50 picks/day)
- **Vercel**: Free tier (sufficient for current usage)
- **Firebase**: Free tier (sufficient for current usage)

### Cost Controls
- Daily cost limits with automatic alerts
- Emergency stop at $60/day
- Cost tracking and reporting
- Optimized API usage patterns

## 🚨 Troubleshooting

### Common Issues

1. **Firebase Connection Errors**
   - Verify service account credentials
   - Check Firebase project ID
   - Ensure proper permissions

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check rate limits and quotas
   - Monitor token usage

3. **DraftKings API Issues**
   - Check API availability
   - Verify rate limiting
   - Monitor response times

4. **Data Freshness Issues**
   - Check cron job execution
   - Verify data collection logs
   - Monitor external API status

### Debug Mode

Enable debug logging by setting:
```bash
DEBUG=true
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Google Sheets Integration](docs/GOOGLE_SHEETS.md) - Complete Google Sheets guide
- [API Documentation](docs/API.md) - Detailed API reference
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Deployment Guide](docs/DEPLOYMENT.md) - Step-by-step deployment instructions

## 🔧 Development

### Local Development

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Start development server**
   ```bash
   vercel dev
   ```

3. **Test endpoints**
   ```bash
   curl -X POST http://localhost:3000/api/health-check
   ```

### Testing

Run the test suite:
```bash
npm test
```

### Code Quality

The project follows these standards:
- ESLint for code linting
- Prettier for code formatting
- Comprehensive error handling
- Detailed logging and monitoring

## 📝 Changelog

### Version 1.0.0
- Initial release
- NFL automation support
- OpenAI GPT-4 integration
- Firebase integration
- Auto-scoring system
- Health monitoring
- Slack notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review the [API Documentation](docs/API.md)
- Open an issue on GitHub
- Contact the development team

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ NFL automation
- ✅ Basic monitoring
- ✅ Auto-scoring

### Phase 2 (Next)
- 🔄 NHL automation
- 🔄 College Basketball automation
- 🔄 Enhanced monitoring dashboard

### Phase 3 (Future)
- 📋 College Football automation
- 📋 Advanced analytics
- 📋 Machine learning improvements
- 📋 Mobile app integration
#   U p d a t e d :   1 0 / 0 9 / 2 0 2 5   1 7 : 0 0 : 4 5 
 
 
