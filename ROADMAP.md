# Confident Picks — Implementation Roadmap

Status
- Live gating: client-side password gate active (PASS = "getmoney").
- Repo: origin/main deploying to GitHub Pages.

## 1) Branding, SEO, and Assets
Owner: Agent (needs your assets)
- [ ] Replace `og:url` with `https://confident-picks.com`
- [ ] Add assets: `favicon.ico`, `logo.svg`, `apple-touch-icon.png`, `og-image.png`
- [ ] Provide `manifest.webmanifest` (name, icons, theme)
- [ ] Finalize `<meta name="description">`
You provide: all image assets + final description copy

## 2) Gate Strategy
Owner: You → Agent
- [ ] Decide: keep temporary gate on live OR move to Cloudflare Access (recommended)
- [ ] If keeping, confirm final password and removal date
You provide: decision + (optional) Cloudflare Access details

## 3) Authentication (Firebase recommended)
Owner: Agent (needs Firebase config)
- [ ] Enable Firebase SDK and real auth flows (Google + Email/Password)
- [ ] Replace localStorage verification with Firebase email verification
- [ ] Persist profile basics (createdAt, lastLoginAt) from auth
You provide: Firebase config (apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId); enable Google sign-in

## 4) Favorites and Outcomes Storage
Owner: Agent (depends on 3 or backend)
- [ ] Move Favorites from localStorage to Firestore (per-user collection)
- [ ] Outcomes: define data source and map favorites to graded results
You provide: choose source (Firestore vs API/N8N) and data shape

## 5) Picks/Results Data Feed
Owner: Agent (needs endpoint)
Option A (N8N/webhook):
- [ ] Provide `n8nEndpoints.picks` URL + auth header
- [ ] Implement fetch + render, keep local mock as fallback
Option B (Firestore/REST API):
- [ ] Provide collection/API schema and read rules
You provide: endpoint(s), payload format, and auth method

## 6) Subscriptions/Payments (Stripe)
Owner: Agent (needs Stripe details)
- [ ] Implement Stripe Checkout/Customer Portal
- [ ] Map subscription status to "free/paid" UI
- [ ] Replace coupon mock (SAVE20) with real promo logic
You provide: Stripe publishable key, test price IDs (monthly/yearly), webhook receiver URL (N8N or other)

## 7) Contact Form
Owner: Agent (needs destination)
- [ ] Wire POST to N8N (or email service) instead of console.log
- [ ] Add bot protection (Cloudflare Turnstile)
You provide: `n8nEndpoints.contact` + any required headers/secrets

## 8) Admin and Roles
Owner: Agent (needs policy)
- [ ] Replace mock `isAdmin` with role-based access (Firebase custom claims or API)
- [ ] Hide/secure dev-only buttons in prod
You provide: list of admin emails or role policy

## 9) Legal/Compliance
Owner: You → Agent
- [ ] Replace placeholder Terms and Privacy content
- [ ] Confirm responsible gaming copy/jurisdiction notes
You provide: legal copy or approval to draft v1

## 10) Localization
Owner: Agent (needs final copy per language)
- [ ] Audit strings and complete translations beyond nav/settings
You provide: languages to support and final text per language (or approval to use machine-aided drafts)

## 11) Analytics
Owner: Agent (needs ID)
- [ ] Add GA4/Plausible and basic event tracking (view, filters, favorite, subscribe, contact)
You provide: tool choice + property/site ID

## Known Placeholders in `index.html`
- [ ] `<meta property="og:url" content="https://your-live-url.com">`
- [ ] Asset references: `/favicon.ico`, `/logo.svg`, `/apple-touch-icon.png`, `/og-image.png`
- [ ] Firebase config (commented): firebaseConfig block
- [ ] `n8nEndpoints` placeholders (contact/picks/analytics)
- [ ] Legal sections: Terms, Privacy (placeholder copy)
- [ ] Temporary gate password: `var PASS = 'getmoney'` (confirm keep/remove)

## Deliverables per Phase
Phase A (today)
- [ ] Swap SEO URL + add assets
- [ ] Decide gate strategy
- [ ] Commit and deploy

Phase B (Auth + Favorites)
- [ ] Firebase Auth live
- [ ] Favorites in Firestore
- [ ] Email verification UI

Phase C (Data + Subscribe)
- [ ] Picks API/N8N wired
- [ ] Stripe checkout + sub status in UI
- [ ] Contact → N8N + Turnstile

Phase D (Admin, Analytics, Legal)
- [ ] Role-based Admin
- [ ] Analytics events
- [ ] Final Terms/Privacy

## What I can do autonomously now
- Implement all front-end edits
- Enable Firebase SDK and wire flows once config is provided
- Integrate N8N endpoints once URLs/headers are provided
- Add Stripe Checkout client and UI; need your keys/price IDs
- Replace placeholders, add assets, SEO polish, analytics, Turnstile

## What I need from you (paste in reply)
- Firebase config JSON (or confirm alternative)
- N8N endpoint URLs + any required headers/secrets
- Stripe publishable key + price IDs (monthly/yearly)
- Final assets: `favicon.ico`, `logo.svg`, `apple-touch-icon.png`, `og-image.png`, `manifest.webmanifest`
- Decision: keep temp gate or adopt Cloudflare Access
- Legal copy (or permission to draft)
- Analytics provider + ID
- Admin emails (if using Firebase claims)
