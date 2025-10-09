# Confident Picks - Firebase Database Schema

## 📊 **Database Structure Overview**

```
confident-picks-app/
├── picks/                    # Main picks collection
├── users/                    # User data and preferences  
├── analytics/                # Performance tracking
├── system/                   # App configuration
└── data-lake/               # Future: External data sources
```

---

## 🎯 **1. PICKS Collection**

### **Structure:**
```
picks/
├── {pickId}/
│   ├── id: string
│   ├── league: string (NFL, NBA, MLB, etc.)
│   ├── marketType: string (moneyline, spread, totals, etc.)
│   ├── pickDesc: string
│   ├── oddsAmerican: number
│   ├── modelConfidence: number (0-100)
│   ├── commenceTime: timestamp
│   ├── tier: string (public, free, paid)
│   ├── riskTag: string (safe, degen)
│   ├── reasoning: string
│   ├── status: string (pending, settled, cancelled)
│   ├── result: string (W, L, P) - only when settled
│   ├── settledAt: timestamp - only when settled
│   ├── createdAt: timestamp
│   ├── updatedAt: timestamp
│   └── metadata: object
│       ├── source: string (manual, api, data-lake)
│       ├── confidenceFactors: array
│       └── externalData: object
```

### **Example Document:**
```json
{
  "id": "pick_001",
  "league": "NFL",
  "marketType": "spread", 
  "pickDesc": "Eagles -7 vs NYG",
  "oddsAmerican": -110,
  "modelConfidence": 85,
  "commenceTime": "2025-01-15T21:00:00Z",
  "tier": "public",
  "riskTag": "safe",
  "reasoning": "Eagles 9-1 ATS as home favorites, Giants missing key players",
  "status": "pending",
  "createdAt": "2025-01-14T10:00:00Z",
  "updatedAt": "2025-01-14T10:00:00Z",
  "metadata": {
    "source": "manual",
    "confidenceFactors": ["home-field-advantage", "injury-report", "weather"],
    "externalData": {
      "vegasOdds": -110,
      "dataLakeScore": 0.85
    }
  }
}
```

---

## 👥 **2. USERS Collection**

### **Structure:**
```
users/
├── {userId}/
│   ├── profile: object
│   │   ├── email: string
│   │   ├── displayName: string
│   │   ├── subscription: string (anon, free, paid)
│   │   ├── emailVerified: boolean
│   │   ├── createdAt: timestamp
│   │   └── lastLoginAt: timestamp
│   ├── favorites: array
│   │   └── [{pickId, addedAt}]
│   ├── settings: object
│   │   ├── language: string
│   │   ├── theme: string
│   │   ├── currency: string
│   │   └── notifications: object
│   └── analytics: object
│       ├── totalPicks: number
│       ├── winRate: number
│       └── favoriteLeagues: array
```

---

## 📈 **3. ANALYTICS Collection**

### **Structure:**
```
analytics/
├── picks/
│   ├── {pickId}/
│   │   ├── views: number
│   │   ├── favorites: number
│   │   ├── userInteractions: array
│   │   └── performance: object
├── users/
│   ├── {userId}/
│   │   ├── activity: array
│   │   ├── preferences: object
│   │   └── engagement: object
└── system/
    ├── dailyStats: object
    ├── performanceMetrics: object
    └── errorLogs: array
```

---

## ⚙️ **4. SYSTEM Collection**

### **Structure:**
```
system/
├── config/
│   ├── appVersion: string
│   ├── maintenanceMode: boolean
│   ├── featureFlags: object
│   └── apiEndpoints: object
├── banners/
│   ├── {bannerId}/
│   │   ├── type: string (maintenance, announcement, warning)
│   │   ├── title: string
│   │   ├── message: string
│   │   ├── active: boolean
│   │   └── schedule: object
└── admin/
    ├── users: object
    ├── metrics: object
    └── logs: array
```

---

## 🌊 **5. DATA-LAKE Collection (Future)**

### **Structure:**
```
data-lake/
├── sources/
│   ├── youtube/
│   │   ├── {videoId}/
│   │   │   ├── title: string
│   │   │   ├── channel: string
│   │   │   ├── publishedAt: timestamp
│   │   │   ├── analysis: object
│   │   │   └── picks: array
│   ├── external-apis/
│   │   ├── odds/
│   │   ├── news/
│   │   └── stats/
│   └── social/
│       ├── twitter/
│       └── reddit/
├── analysis/
│   ├── consensus/
│   ├── trends/
│   └── predictions/
└── processed/
    ├── insights/
    └── recommendations/
```

---

## 🔄 **6. Real-time Updates**

### **Collections with Real-time Listeners:**
- `picks/` - New picks, status updates
- `users/{userId}/favorites/` - User favorites changes
- `system/banners/` - Maintenance announcements
- `analytics/picks/{pickId}/` - Performance updates

---

## 📋 **7. Security Rules (Firestore)**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Picks - Read for all, write for admin
    match /picks/{pickId} {
      allow read: if true;
      allow write: if request.auth != null && 
        request.auth.token.admin == true;
    }
    
    // Users - Read/write own data only
    match /users/{userId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
    
    // Analytics - Read for all, write for system
    match /analytics/{document=**} {
      allow read: if true;
      allow write: if request.auth != null && 
        request.auth.token.admin == true;
    }
    
    // System - Admin only
    match /system/{document=**} {
      allow read, write: if request.auth != null && 
        request.auth.token.admin == true;
    }
  }
}
```

---

## 🚀 **8. Migration Strategy**

### **Phase 1: Static to Firebase**
1. Create collections structure
2. Migrate existing static data
3. Test with read-only operations

### **Phase 2: Real-time Integration**
1. Add real-time listeners
2. Implement CRUD operations
3. Add user favorites sync

### **Phase 3: Data Lake Integration**
1. Add external data sources
2. Implement analysis pipeline
3. Create consensus scoring

---

## 📊 **9. Indexes Required**

```javascript
// Composite indexes for efficient queries
picks: [
  ['league', 'status', 'commenceTime'],
  ['tier', 'modelConfidence', 'commenceTime'],
  ['status', 'result', 'settledAt'],
  ['league', 'marketType', 'commenceTime']
]

users: [
  ['subscription', 'createdAt'],
  ['emailVerified', 'lastLoginAt']
]

analytics: [
  ['pickId', 'timestamp'],
  ['userId', 'activity', 'timestamp']
]
```

---

## 🎯 **10. Data Flow**

```
External Sources → Data Lake → Analysis → Picks Collection → UI
                     ↓
User Interactions → Analytics → Performance Tracking
                     ↓
System Config → Feature Flags → App Behavior
```

This schema supports:
- ✅ **Current static data migration**
- ✅ **Real-time pick updates**
- ✅ **User favorites and settings**
- ✅ **Performance analytics**
- ✅ **Future data lake integration**
- ✅ **Admin dashboard functionality**
- ✅ **Scalable architecture**

