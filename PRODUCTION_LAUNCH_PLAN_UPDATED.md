# 🚀 Confident Picks - Production Launch Plan

**Goal:** Launch production-ready platform with NFL, NHL, NBA, NCAAB  
**Timeline:** 4 weeks to public launch  
**Current Status:** ~30% complete

---

## 📊 **Task Legend**

- 🔴 **Critical Path** - Blocks launch
- 🟡 **High Priority** - Needed soon after launch
- 🟢 **Medium Priority** - Nice to have
- ⚡ **Can Run in Parallel** - Do simultaneously
- 🔄 **Automated/Background** - Set and forget

---

# **PHASE 1: Core Infrastructure (Days 1-7)**

## 🔐 Security & Authentication

### Task 1.1: Firebase Security Rules 🔴
- [ ] Write Firestore security rules to prevent role modification
- [ ] Prevent users from editing their own `role` field
- [ ] Allow users to read their own data
- [ ] Allow admins to read/write all data
- [ ] Test rules with Firebase emulator
- [ ] Deploy rules to production
- [ ] Document rules in `ADMIN_SETUP.md`

**Files:** Firebase Console → Firestore → Rules  
**Time:** 2 hours  
**Dependencies:** None

---

### Task 1.2: Email System (Real) 🔴
- [ ] Choose email provider (SendGrid, AWS SES, or Mailgun)
- [ ] Set up email templates for:
  - [ ] Email verification
  - [ ] Password reset
  - [ ] Welcome email
  - [ ] Subscription confirmation
  - [ ] Payment receipt
- [ ] Replace mock email functions in `index.html`
- [ ] Test email delivery
- [ ] Set up SPF/DKIM records for domain
- [ ] Add unsubscribe functionality

**Files:** `index.html` (lines 7200-7300), new `email_service.js`  
**Time:** 4 hours  
**Dependencies:** Domain name (Task 2.1)

---

### Task 1.3: Password Reset Flow 🔴
- [ ] Create password reset request endpoint
- [ ] Generate secure reset tokens
- [ ] Send reset email with link
- [ ] Create reset password page
- [ ] Validate token expiration (24 hours)
- [ ] Update password in Firebase Auth
- [ ] Test full flow

**Files:** `index.html`, Firebase Functions  
**Time:** 3 hours  
**Dependencies:** Task 1.2 (Email System)

---

## 💳 Payment System

### Task 1.4: Stripe Live Mode 🔴
- [ ] Get Stripe live publishable key
- [ ] Get Stripe live secret key
- [ ] Update `stripeConfig` in `index.html` (line 7331)
- [ ] Change `mode: 'sandbox'` to `mode: 'production'`
- [ ] Remove "(Sandbox)" labels from upgrade buttons
- [ ] Test with real credit card (use your own)
- [ ] Verify payment appears in Stripe dashboard

**Files:** `index.html` (lines 7310-7335)  
**Time:** 1 hour  
**Dependencies:** Stripe account approval

---

### Task 1.5: Stripe Webhooks 🔴
- [ ] Create backend endpoint (Firebase Function or Node.js server)
- [ ] Handle `checkout.session.completed` event
- [ ] Handle `customer.subscription.created` event
- [ ] Handle `customer.subscription.updated` event
- [ ] Handle `customer.subscription.deleted` event
- [ ] Handle `invoice.payment_failed` event
- [ ] Update user subscription status in Firestore
- [ ] Verify webhook signature for security
- [ ] Test with Stripe CLI
- [ ] Deploy webhook endpoint
- [ ] Register webhook URL in Stripe dashboard

**Files:** New `firebase/functions/stripe-webhook.js`  
**Time:** 6 hours  
**Dependencies:** Task 1.4 (Stripe Live Mode)

---

### Task 1.6: Subscription Management 🟡
- [ ] Create "Manage Subscription" page
- [ ] Add "Cancel Subscription" button
- [ ] Add "Update Payment Method" button
- [ ] Integrate Stripe Customer Portal
- [ ] Handle subscription cancellation
- [ ] Downgrade user to free tier on cancel
- [ ] Send cancellation confirmation email
- [ ] Add "Reactivate Subscription" option

**Files:** `index.html` (new section in Account page)  
**Time:** 4 hours  
**Dependencies:** Task 1.5 (Webhooks)

---

## 🌐 Hosting & Domain

### Task 2.1: Domain Setup 🔴
- [ ] Purchase domain (e.g., confidentpicks.com)
- [ ] Configure DNS settings
- [ ] Point domain to hosting provider
- [ ] Set up www redirect
- [ ] Verify domain ownership

**Platform:** Namecheap, GoDaddy, or Google Domains  
**Time:** 1 hour  
**Dependencies:** None  
**Cost:** ~$15/year

---

### Task 2.2: Hosting Setup 🔴
- [ ] Choose hosting platform:
  - Option A: Firebase Hosting (recommended)
  - Option B: Vercel
  - Option C: Netlify
- [ ] Create production project
- [ ] Configure build settings
- [ ] Set up custom domain
- [ ] Enable HTTPS/SSL (automatic on most platforms)
- [ ] Test deployment
- [ ] Set up staging environment

**Platform:** Firebase Hosting  
**Time:** 2 hours  
**Dependencies:** Task 2.1 (Domain)  
**Cost:** Free tier sufficient initially

---

### Task 2.3: CI/CD Pipeline 🟡
- [ ] Create GitHub repository (if not already)
- [ ] Set up GitHub Actions or similar
- [ ] Create deployment workflow:
  - [ ] Run on push to `main` branch
  - [ ] Run tests (when added)
  - [ ] Deploy to staging first
  - [ ] Deploy to production after approval
- [ ] Set up environment variables
- [ ] Test automated deployment

**Files:** `.github/workflows/deploy.yml`  
**Time:** 3 hours  
**Dependencies:** Task 2.2 (Hosting)

---

## 📝 Legal & Compliance

### Task 3.1: Terms of Service 🔴
- [ ] Hire lawyer or use legal template service (Termly, Iubenda)
- [ ] Customize for your business
- [ ] Include:
  - [ ] Service description
  - [ ] User responsibilities
  - [ ] Disclaimer (not gambling advice)
  - [ ] Age restriction (21+)
  - [ ] Refund policy
  - [ ] Limitation of liability
  - [ ] Dispute resolution
- [ ] Replace placeholder in `index.html`
- [ ] Add "Last Updated" date

**Files:** `index.html` (lines 1900-1950)  
**Time:** 4 hours (with template) or 2 weeks (with lawyer)  
**Dependencies:** None  
**Cost:** $50-500 (template) or $1,000-3,000 (lawyer)

---

### Task 3.2: Privacy Policy 🔴
- [ ] Create privacy policy covering:
  - [ ] Data collection (email, payment info, usage data)
  - [ ] Data usage (service provision, analytics, marketing)
  - [ ] Data sharing (Stripe, Firebase, analytics)
  - [ ] User rights (access, deletion, export)
  - [ ] Cookie usage
  - [ ] GDPR compliance (if serving EU)
  - [ ] CCPA compliance (if serving California)
- [ ] Replace placeholder in `index.html`
- [ ] Add "Last Updated" date

**Files:** `index.html` (lines 1950-2000)  
**Time:** 4 hours (with template)  
**Dependencies:** None  
**Cost:** $50-500 (template)

---

### Task 3.3: Cookie Consent 🟡
- [ ] Add cookie consent banner
- [ ] Categorize cookies (necessary, analytics, marketing)
- [ ] Allow users to opt-out of non-essential cookies
- [ ] Store consent preference
- [ ] Update privacy policy with cookie details

**Files:** `index.html` (new banner component)  
**Time:** 2 hours  
**Dependencies:** Task 3.2 (Privacy Policy)

---

### Task 3.4: Age Verification 🟡
- [ ] Add age gate on first visit
- [ ] Require users to confirm 21+ years old
- [ ] Store confirmation in localStorage
- [ ] Add to sign-up flow
- [ ] Block access if declined

**Files:** `index.html` (new modal)  
**Time:** 2 hours  
**Dependencies:** None

---

## 🔍 Monitoring & Analytics

### Task 4.1: Error Monitoring 🔴
- [ ] Sign up for Sentry (or similar)
- [ ] Add Sentry SDK to `index.html`
- [ ] Configure error tracking
- [ ] Set up email alerts for critical errors
- [ ] Test error reporting
- [ ] Add custom error boundaries

**Files:** `index.html` (add Sentry script)  
**Time:** 2 hours  
**Dependencies:** None  
**Cost:** Free tier sufficient initially

---

### Task 4.2: Analytics Setup 🟡
- [ ] Choose analytics platform:
  - Option A: Google Analytics 4
  - Option B: Mixpanel
  - Option C: Plausible (privacy-focused)
- [ ] Add tracking code to `index.html`
- [ ] Set up custom events:
  - [ ] Sign up
  - [ ] Sign in
  - [ ] Upgrade to paid
  - [ ] View pick
  - [ ] Favorite pick
  - [ ] Cancel subscription
- [ ] Set up conversion tracking
- [ ] Create dashboard

**Files:** `index.html` (add analytics script)  
**Time:** 3 hours  
**Dependencies:** None  
**Cost:** Free tier sufficient

---

### Task 4.3: Automated Backups 🔴
- [ ] Set up daily Firebase Firestore backups
- [ ] Export to Google Cloud Storage
- [ ] Set up Google Sheets backup (export to CSV)
- [ ] Store backups in separate project
- [ ] Test restore process
- [ ] Document backup/restore procedure
- [ ] Set up backup monitoring/alerts

**Platform:** Firebase Console → Backups  
**Time:** 3 hours  
**Dependencies:** None  
**Cost:** ~$5/month for storage

---

## 🏗️ System Architecture

### Task 5.1: League Config System 🔴 ⚡
- [ ] Create `league_configs.py`
- [ ] Define `LeagueConfig` class
- [ ] Add configs for NFL, NHL, NBA, NCAAB
- [ ] Include:
  - [ ] League name
  - [ ] Google Sheet ID
  - [ ] API endpoints
  - [ ] Team abbreviation mappings
  - [ ] Season start/end dates
  - [ ] Odds API sport key
- [ ] Test config loading

**Files:** New `confident-picks-automation/league_configs.py`  
**Time:** 2 hours  
**Dependencies:** None

---

### Task 5.2: Refactor Pick Generator 🔴 ⚡
- [ ] Update `unified_pick_generator.py` to use league configs
- [ ] Make `get_upcoming_games()` league-agnostic
- [ ] Make `generate_picks()` league-agnostic
- [ ] Add league loop to process all active leagues
- [ ] Test with NFL and NHL
- [ ] Verify picks are generated correctly

**Files:** `confident-picks-automation/unified_pick_generator.py`  
**Time:** 4 hours  
**Dependencies:** Task 5.1 (League Config)

---

### Task 5.3: Standardize Firebase Structure 🔴 ⚡
- [ ] Create `leagues` collection in Firebase
- [ ] Add league metadata (active status, available props)
- [ ] Update `approved_models` to include league field
- [ ] Ensure all picks have consistent structure
- [ ] Add league filter to app UI
- [ ] Test cross-league functionality

**Platform:** Firebase Console  
**Time:** 2 hours  
**Dependencies:** None

---

# **PHASE 2: League Expansion (Days 8-14)**

## 🏀 NBA Setup

### Task 6.1: NBA Data Collection 🔄 ⚡
- [ ] Create NBA Google Sheet (copy NFL structure)
- [ ] Find NBA API source (ESPN, NBA.com, or similar)
- [ ] Write data fetching script
- [ ] Fetch historical data (2021-2024):
  - [ ] Game results
  - [ ] Team stats
  - [ ] Box scores
  - [ ] Advanced metrics
- [ ] Populate historical data sheet
- [ ] Set up current season data fetching
- [ ] Test data quality

**Files:** New Google Sheet, new `nba_data_fetcher.py`  
**Time:** 6 hours  
**Dependencies:** None  
**Can run in parallel with NHL training**

---

### Task 6.2: NBA Team Mappings ⚡
- [ ] Create NBA team abbreviation mapping
- [ ] Map full names to abbreviations
- [ ] Handle team relocations/name changes
- [ ] Add to league config

**Files:** `league_configs.py`  
**Time:** 1 hour  
**Dependencies:** Task 6.1

---

### Task 6.3: NBA Model Training 🔄 ⚡
- [ ] Copy NHL model training pipeline
- [ ] Adapt for NBA features:
  - [ ] Points per game
  - [ ] Field goal percentage
  - [ ] Three-point percentage
  - [ ] Rebounds, assists, steals
  - [ ] Pace of play
  - [ ] Rest days
  - [ ] Home/away splits
- [ ] Run exhaustive model testing
- [ ] Target: 60%+ overall, 70%+ per team
- [ ] Save best models to Firebase
- [ ] Test on current season data

**Files:** New `nba_exhaustive_test.py`  
**Time:** 12-24 hours (automated)  
**Dependencies:** Task 6.1 (NBA Data)  
**Can run in parallel with other tasks**

---

### Task 6.4: NBA Odds Integration ⚡
- [ ] Add NBA to Odds API configuration
- [ ] Sport key: `basketball_nba`
- [ ] Test odds fetching
- [ ] Add to pick generator

**Files:** `unified_pick_generator.py`, `league_configs.py`  
**Time:** 1 hour  
**Dependencies:** Task 6.1

---

## ⚾ NCAAB Setup

### Task 7.1: NCAAB Data Collection 🔄 ⚡
- [ ] Create NCAAB Google Sheet
- [ ] Find NCAAB API source (NCAAB Stats API)
- [ ] Write data fetching script
- [ ] Fetch historical data (2021-2024):
  - [ ] Game results
  - [ ] Pitching stats
  - [ ] Batting stats
  - [ ] Team stats
- [ ] Populate historical data sheet
- [ ] Set up current season data fetching
- [ ] Test data quality

**Files:** New Google Sheet, new `NCAAB_data_fetcher.py`  
**Time:** 6 hours  
**Dependencies:** None  
**Can run in parallel with NBA setup**

---

### Task 7.2: NCAAB Team Mappings ⚡
- [ ] Create NCAAB team abbreviation mapping
- [ ] Map full names to abbreviations
- [ ] Add to league config

**Files:** `league_configs.py`  
**Time:** 1 hour  
**Dependencies:** Task 7.1

---

### Task 7.3: NCAAB Model Training 🔄 ⚡
- [ ] Copy model training pipeline
- [ ] Adapt for NCAAB features:
  - [ ] Starting pitcher ERA
  - [ ] Bullpen ERA
  - [ ] Team batting average
  - [ ] Home runs per game
  - [ ] Runs per game
  - [ ] Home/away splits
  - [ ] Day/night game
  - [ ] Weather (wind, temperature)
- [ ] Run exhaustive model testing
- [ ] Target: 60%+ overall, 70%+ per team
- [ ] Save best models to Firebase
- [ ] Test on current season data

**Files:** New `NCAAB_exhaustive_test.py`  
**Time:** 12-24 hours (automated)  
**Dependencies:** Task 7.1 (NCAAB Data)  
**Can run in parallel**

---

### Task 7.4: NCAAB Odds Integration ⚡
- [ ] Add NCAAB to Odds API configuration
- [ ] Sport key: `baseball_NCAAB`
- [ ] Test odds fetching
- [ ] Add to pick generator

**Files:** `unified_pick_generator.py`, `league_configs.py`  
**Time:** 1 hour  
**Dependencies:** Task 7.1

---

## 🏒 NHL Model Completion

### Task 8.1: NHL Model Finalization 🔄
- [ ] Wait for exhaustive testing to complete
- [ ] Verify 15+ teams at 70%+ accuracy
- [ ] If not achieved, adjust features and rerun
- [ ] Save final models to Firebase
- [ ] Document model performance
- [ ] Test on upcoming games

**Files:** `nhl_exhaustive_test.py`, Firebase  
**Time:** Ongoing (background process)  
**Dependencies:** None  
**Status:** Currently at 8 teams, need 15+

---

# **PHASE 3: Feature Completion (Days 15-21)**

## 🎯 Pick Generation & Display

### Task 9.1: Multi-League Pick Generation 🔴
- [ ] Update `unified_pick_generator.py` to handle 4 leagues
- [ ] Test pick generation for all leagues
- [ ] Verify confidence calculations
- [ ] Verify odds mapping
- [ ] Test Firebase storage
- [ ] Verify no duplicate picks

**Files:** `unified_pick_generator.py`  
**Time:** 2 hours  
**Dependencies:** Tasks 6.4, 7.4, 8.1

---

### Task 9.2: League Filter UI 🟡
- [ ] Add league filter dropdown to picks page
- [ ] Options: All, NFL, NHL, NBA, NCAAB
- [ ] Update render logic to filter by league
- [ ] Save filter preference to localStorage
- [ ] Test filtering

**Files:** `index.html` (lines 2700-2800)  
**Time:** 2 hours  
**Dependencies:** Task 9.1

---

### Task 9.3: Pick Limit Enforcement 🔴
- [ ] Verify 3 picks per league for free users
- [ ] Verify unlimited for paid/admin users
- [ ] Test with multiple leagues
- [ ] Ensure consistent behavior

**Files:** `index.html` (lines 2745-2760)  
**Time:** 1 hour  
**Dependencies:** Task 9.2

---

## 📊 Results & Scorecard

### Task 10.1: Automated Result Fetching 🟡
- [ ] Create result fetching script for each league
- [ ] NFL: Use ESPN API
- [ ] NHL: Use NHL Stats API
- [ ] NBA: Use ESPN/NBA API
- [ ] NCAAB: Use NCAAB Stats API
- [ ] Run hourly to check for completed games
- [ ] Update Firebase with results
- [ ] Move completed picks to `completed_picks` collection

**Files:** New `fetch_results.py`  
**Time:** 6 hours  
**Dependencies:** League APIs set up

---

### Task 10.2: Scorecard Auto-Update 🟡
- [ ] Update scorecard calculation to use Firebase data
- [ ] Calculate win/loss for each pick
- [ ] Update accuracy percentages
- [ ] Update 7-day, 30-day, 180-day filters
- [ ] Test with real completed picks

**Files:** `index.html` (scorecard section)  
**Time:** 3 hours  
**Dependencies:** Task 10.1

---

### Task 10.3: Model Performance Tracking 🟡
- [ ] Track accuracy per model
- [ ] Track accuracy per league
- [ ] Track accuracy per team
- [ ] Display in admin dashboard
- [ ] Alert if model drops below threshold

**Files:** `index.html` (admin section), new tracking script  
**Time:** 4 hours  
**Dependencies:** Task 10.1

---

## 🔄 Automation & Reliability

### Task 11.1: Scheduled Tasks Setup 🔴
- [ ] Verify hourly pick generation task (already set up)
- [ ] Add hourly result fetching task
- [ ] Add daily model performance check
- [ ] Add daily backup task
- [ ] Test all scheduled tasks
- [ ] Set up task failure alerts

**Platform:** Windows Task Scheduler  
**Time:** 2 hours  
**Dependencies:** Tasks 10.1, 4.3

---

### Task 11.2: Health Checks 🟡
- [ ] Create health check endpoint
- [ ] Check Firebase connection
- [ ] Check Google Sheets connection
- [ ] Check Odds API connection
- [ ] Check Stripe connection
- [ ] Run every 15 minutes
- [ ] Alert on failures

**Files:** New `health_check.py`  
**Time:** 3 hours  
**Dependencies:** None

---

### Task 11.3: Rate Limiting 🟡
- [ ] Add rate limiting to API endpoints
- [ ] Limit picks fetching (e.g., 100 requests/hour per IP)
- [ ] Limit sign-up attempts
- [ ] Limit password reset requests
- [ ] Return 429 status code when exceeded

**Files:** Firebase Functions or backend  
**Time:** 3 hours  
**Dependencies:** Backend setup

---

# **PHASE 4: Polish & Testing (Days 22-28)**

## 🎨 UI/UX Improvements

### Task 12.1: Loading States 🟢
- [ ] Add loading spinners to:
  - [ ] Pick loading
  - [ ] Sign in/sign up
  - [ ] Payment processing
  - [ ] Scorecard loading
- [ ] Add skeleton screens
- [ ] Test loading states

**Files:** `index.html` (various sections)  
**Time:** 3 hours  
**Dependencies:** None

---

### Task 12.2: Error Messages 🟡
- [ ] Replace generic error alerts with user-friendly messages
- [ ] Add error toast notifications
- [ ] Categorize errors (network, auth, payment, etc.)
- [ ] Provide actionable next steps
- [ ] Test error scenarios

**Files:** `index.html` (error handling)  
**Time:** 3 hours  
**Dependencies:** None

---

### Task 12.3: Onboarding Flow 🟢
- [ ] Create welcome modal for new users
- [ ] Explain how picks work
- [ ] Highlight confidence scores
- [ ] Show how to upgrade
- [ ] Add "Skip" option
- [ ] Show only once per user

**Files:** `index.html` (new modal)  
**Time:** 4 hours  
**Dependencies:** None

---

### Task 12.4: Help/FAQ Section 🟢
- [ ] Create FAQ page
- [ ] Common questions:
  - [ ] How do picks work?
  - [ ] What is confidence score?
  - [ ] How accurate are predictions?
  - [ ] How to read odds?
  - [ ] How to cancel subscription?
  - [ ] Refund policy
- [ ] Add search functionality
- [ ] Link from footer

**Files:** `index.html` (new section)  
**Time:** 4 hours  
**Dependencies:** None

---

## 🧪 Testing

### Task 13.1: Browser Testing 🟡
- [ ] Test on Chrome (desktop)
- [ ] Test on Firefox (desktop)
- [ ] Test on Safari (desktop)
- [ ] Test on Edge (desktop)
- [ ] Test on Chrome (mobile)
- [ ] Test on Safari (iOS)
- [ ] Fix any browser-specific issues

**Time:** 4 hours  
**Dependencies:** All features complete

---

### Task 13.2: Mobile Testing 🟡
- [ ] Test on iPhone (various sizes)
- [ ] Test on Android (various sizes)
- [ ] Test touch interactions
- [ ] Test responsive layout
- [ ] Fix mobile-specific issues

**Time:** 3 hours  
**Dependencies:** All features complete

---

### Task 13.3: Payment Testing 🔴
- [ ] Test sign-up flow
- [ ] Test upgrade flow
- [ ] Test with real credit card
- [ ] Test payment failure
- [ ] Test subscription cancellation
- [ ] Test subscription renewal
- [ ] Verify webhooks fire correctly
- [ ] Verify user access updates

**Time:** 3 hours  
**Dependencies:** Tasks 1.4, 1.5, 1.6

---

### Task 13.4: Load Testing 🟡
- [ ] Use tool like Apache JMeter or k6
- [ ] Simulate 100 concurrent users
- [ ] Simulate 1,000 concurrent users
- [ ] Test pick loading performance
- [ ] Test Firebase query performance
- [ ] Identify bottlenecks
- [ ] Optimize slow queries

**Time:** 4 hours  
**Dependencies:** All features complete

---

### Task 13.5: Security Testing 🔴
- [ ] Test Firebase security rules
- [ ] Try to modify role as regular user
- [ ] Try to access admin panel as regular user
- [ ] Test XSS vulnerabilities
- [ ] Test SQL injection (if applicable)
- [ ] Test CSRF protection
- [ ] Run automated security scan

**Time:** 3 hours  
**Dependencies:** Task 1.1

---

## 📱 Marketing & Launch Prep

### Task 14.1: Landing Page 🟢
- [ ] Create compelling landing page
- [ ] Highlight key features:
  - [ ] 4 leagues
  - [ ] 100+ picks per week
  - [ ] 60%+ accuracy
  - [ ] $15/month
- [ ] Add social proof (when available)
- [ ] Add call-to-action buttons
- [ ] Optimize for conversions

**Files:** `index.html` or separate landing page  
**Time:** 6 hours  
**Dependencies:** None

---

### Task 14.2: Social Media Setup 🟢
- [ ] Create Twitter/X account
- [ ] Create Instagram account
- [ ] Create Facebook page
- [ ] Design profile images
- [ ] Write bio/description
- [ ] Post launch announcement
- [ ] Plan content calendar

**Time:** 3 hours  
**Dependencies:** None

---

### Task 14.3: Email Marketing Setup 🟢
- [ ] Choose email platform (Mailchimp, ConvertKit, etc.)
- [ ] Create welcome email sequence
- [ ] Create weekly picks email
- [ ] Create win/loss recap email
- [ ] Set up automated campaigns
- [ ] Test email delivery

**Time:** 4 hours  
**Dependencies:** Task 1.2 (Email System)

---

### Task 14.4: Launch Checklist 🔴
- [ ] All critical tasks complete
- [ ] All payment flows tested
- [ ] All leagues generating picks
- [ ] Error monitoring active
- [ ] Backups running
- [ ] Legal documents in place
- [ ] Domain configured
- [ ] SSL certificate active
- [ ] Analytics tracking
- [ ] Support email set up

**Time:** 2 hours  
**Dependencies:** All previous tasks

---

# **POST-LAUNCH (Days 29+)**

## 🚀 Soft Launch (Days 29-35)

### Task 15.1: Beta Testing
- [ ] Invite 50-100 beta users
- [ ] Offer free premium for 1 month
- [ ] Collect feedback
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Fix critical issues
- [ ] Iterate based on feedback

**Time:** Ongoing  
**Dependencies:** Task 14.4 (Launch Checklist)

---

### Task 15.2: Public Launch (Day 36)
- [ ] Open to public
- [ ] Post on social media
- [ ] Submit to Product Hunt
- [ ] Submit to relevant subreddits
- [ ] Email marketing campaign
- [ ] Monitor sign-ups
- [ ] Monitor server load
- [ ] Respond to support requests

**Time:** Launch day + ongoing  
**Dependencies:** Task 15.1 (Beta Testing)

---

## 📈 Phase 2 Expansion (Weeks 6-8)

### Task 16.1: Add Props to Existing Leagues
- [ ] NFL Spreads
- [ ] NFL Totals
- [ ] NHL Puck Lines
- [ ] NHL Totals
- [ ] NBA Spreads
- [ ] NBA Totals
- [ ] NCAAB Run Lines
- [ ] NCAAB Totals

**Time:** 2-3 weeks  
**Dependencies:** Launch complete

---

### Task 16.2: Add More Leagues
- [ ] Soccer (Premier League, Champions League)
- [ ] UFC/MMA
- [ ] Tennis
- [ ] Golf

**Time:** 1 week per league  
**Dependencies:** Phase 2 complete

---

### Task 16.3: Add Player Props
- [ ] NBA player points, rebounds, assists
- [ ] NFL player touchdowns, yards
- [ ] NCAAB player hits, home runs
- [ ] NHL player goals, assists

**Time:** 3-4 weeks  
**Dependencies:** Phase 2 complete

---

# **SUMMARY**

## Critical Path (Must Complete Before Launch)
1. Firebase Security Rules (2h)
2. Email System (4h)
3. Password Reset (3h)
4. Stripe Live Mode (1h)
5. Stripe Webhooks (6h)
6. Domain Setup (1h)
7. Hosting Setup (2h)
8. Terms of Service (4h)
9. Privacy Policy (4h)
10. Error Monitoring (2h)
11. Automated Backups (3h)
12. League Config System (2h)
13. Refactor Pick Generator (4h)
14. Standardize Firebase (2h)
15. NBA Data + Model (18h)
16. NCAAB Data + Model (18h)
17. NHL Model Completion (ongoing)
18. Multi-League Pick Generation (2h)
19. Scheduled Tasks (2h)
20. Payment Testing (3h)
21. Security Testing (3h)
22. Launch Checklist (2h)

**Total Critical Path Time: ~90 hours (11-12 days of focused work)**

## Parallel Tasks (Can Do Simultaneously)
- NBA setup while NHL trains
- NCAAB setup while NBA trains
- UI improvements while models train
- Marketing prep while testing
- Legal documents while building features

## Background Tasks (Set and Forget)
- NHL exhaustive testing (ongoing)
- NBA model training (12-24h)
- NCAAB model training (12-24h)
- Automated backups (daily)
- Health checks (every 15min)

---

**Total Estimated Time: 3-4 weeks to public launch**

**Next Immediate Steps:**
1. Start NBA data collection (Task 6.1)
2. Start NCAAB data collection (Task 7.1)
3. Set up Firebase security rules (Task 1.1)
4. Get Stripe live keys (Task 1.4)
5. Purchase domain (Task 2.1)

---

*Last Updated: October 25, 2025*  
*Document Version: 1.0*

