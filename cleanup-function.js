const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Initialize Firebase Admin
admin.initializeApp();
const db = admin.firestore();

// Cleanup function to remove duplicates and organize data
// TEMPORARILY DISABLED - This was automatically deleting newly created picks
// exports.cleanupMLBPicks = functions.https.onRequest(async (req, res) => {
