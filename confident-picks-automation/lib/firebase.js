// Firebase Admin SDK integration
import admin from 'firebase-admin';

// Initialize Firebase Admin
if (!admin.apps.length) {
  try {
    // Use service account from environment variables
    const serviceAccount = {
      type: "service_account",
      project_id: process.env.FIREBASE_PROJECT_ID,
      private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
      client_id: process.env.FIREBASE_CLIENT_ID,
      auth_uri: "https://accounts.google.com/o/oauth2/auth",
      token_uri: "https://oauth2.googleapis.com/token",
      auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
      client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${process.env.FIREBASE_CLIENT_EMAIL}`
    };

    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      projectId: process.env.FIREBASE_PROJECT_ID
    });
  } catch (error) {
    console.error('Firebase initialization failed:', error);
  }
}

const db = admin.firestore();

// Firebase operations
export const firebase = {
  // Store raw data from DraftKings
  async storeRawData(sport, data) {
    try {
      const docRef = await db.collection('raw_data').doc(sport).collection('daily').doc().set({
        ...data,
        timestamp: admin.firestore.FieldValue.serverTimestamp()
      });
      console.log(`✅ Raw data stored for ${sport}`);
      return docRef;
    } catch (error) {
      console.error('❌ Failed to store raw data:', error);
      throw error;
    }
  },

  // Store generated picks
  async storePicks(picks) {
    try {
      const batch = db.batch();
      
      picks.forEach(pick => {
        const docRef = db.collection('qa_picks').doc();
        batch.set(docRef, {
          ...pick,
          status: pick.auto_approve ? 'approved' : 'draft',
          createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
      });
      
      await batch.commit();
      console.log(`✅ ${picks.length} picks stored`);
    } catch (error) {
      console.error('❌ Failed to store picks:', error);
      throw error;
    }
  },

  // Update pick status
  async updatePickStatus(pickId, status) {
    try {
      await db.collection('qa_picks').doc(pickId).update({
        status,
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      });
      console.log(`✅ Pick ${pickId} status updated to ${status}`);
    } catch (error) {
      console.error('❌ Failed to update pick status:', error);
      throw error;
    }
  },

  // Get completed games for scoring
  async getCompletedGames() {
    try {
      const now = new Date();
      const snapshot = await db.collection('live_picks')
        .where('startTime', '<=', now)
        .where('status', '==', 'live')
        .get();
      
      const completedGames = [];
      snapshot.forEach(doc => {
        completedGames.push({ id: doc.id, ...doc.data() });
      });
      
      console.log(`✅ Found ${completedGames.length} completed games`);
      return completedGames;
    } catch (error) {
      console.error('❌ Failed to get completed games:', error);
      throw error;
    }
  },

  // Mark pick as hit or miss
  async markAsHitOrMiss(pickId, result) {
    try {
      await db.collection('scoring').doc(pickId).set({
        pickId,
        result, // 'hit' or 'miss'
        scoredAt: admin.firestore.FieldValue.serverTimestamp()
      });
      console.log(`✅ Pick ${pickId} marked as ${result}`);
    } catch (error) {
      console.error('❌ Failed to mark pick result:', error);
      throw error;
    }
  }
};

export default firebase;