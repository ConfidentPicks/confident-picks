/**
 * Confident Picks - Stripe Webhook Handler
 * 
 * This Firebase Cloud Function handles Stripe webhook events for subscription management.
 * It listens for checkout.session.completed and customer.subscription.deleted events
 * and updates user subscription status in Firestore accordingly.
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const stripe = require('stripe')(functions.config().stripe.secret_key);
const cors = require('cors')({ origin: true });

// Initialize Firebase Admin
admin.initializeApp();

/**
 * Stripe Webhook Endpoint
 * 
 * Handles incoming webhook events from Stripe.
 * Events handled:
 * - checkout.session.completed: Activates premium subscription
 * - customer.subscription.updated: Updates subscription status
 * - customer.subscription.deleted: Cancels subscription
 */
exports.stripeWebhook = functions.https.onRequest(async (req, res) => {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).send('Method Not Allowed');
  }

  const event = req.body;
  
  console.log('📨 Webhook event received:', {
    type: event.type,
    id: event.id,
    created: event.created
  });

  try {
    // Handle different event types
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object);
        break;
        
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;
        
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;
        
      default:
        console.log(`⚠️ Unhandled event type: ${event.type}`);
    }

    // Acknowledge receipt of the event
    res.json({ received: true });
    
  } catch (error) {
    console.error('❌ Error processing webhook:', error);
    res.status(500).send('Webhook processing failed');
  }
});

/**
 * Handle checkout.session.completed event
 * Activates premium subscription for the user
 */
async function handleCheckoutCompleted(session) {
  console.log('💳 Processing checkout completion:', session.id);
  
  const userId = session.client_reference_id;
  
  if (!userId) {
    console.error('❌ No client_reference_id found in session');
    throw new Error('Missing user ID in checkout session');
  }

  try {
    const subscriptionData = {
      status: 'active',
      tier: 'premium',
      stripeCustomerId: session.customer,
      stripeSubscriptionId: session.subscription,
      stripePriceId: session.metadata?.priceId || 'unknown',
      amount: session.amount_total / 100, // Convert from cents
      currency: session.currency,
      startedAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      currentPeriodEnd: null // Will be updated by subscription.updated event
    };

    await admin.firestore()
      .collection('users')
      .doc(userId)
      .update({ subscription: subscriptionData });

    console.log('✅ Subscription activated for user:', userId);
    
  } catch (error) {
    console.error('❌ Error activating subscription:', error);
    throw error;
  }
}

/**
 * Handle customer.subscription.updated event
 * Updates subscription details (renewal, status changes)
 */
async function handleSubscriptionUpdated(subscription) {
  console.log('🔄 Processing subscription update:', subscription.id);
  
  const customerId = subscription.customer;
  
  try {
    // Find user by Stripe customer ID
    const usersSnapshot = await admin.firestore()
      .collection('users')
      .where('subscription.stripeCustomerId', '==', customerId)
      .limit(1)
      .get();

    if (usersSnapshot.empty) {
      console.warn('⚠️ No user found for customer:', customerId);
      return;
    }

    const userDoc = usersSnapshot.docs[0];
    const updates = {
      'subscription.status': subscription.status,
      'subscription.currentPeriodEnd': new Date(subscription.current_period_end * 1000),
      'subscription.updatedAt': admin.firestore.FieldValue.serverTimestamp()
    };

    // If subscription is no longer active, downgrade to free
    if (subscription.status !== 'active' && subscription.status !== 'trialing') {
      updates['subscription.tier'] = 'free';
    }

    await userDoc.ref.update(updates);
    
    console.log('✅ Subscription updated for customer:', customerId);
    
  } catch (error) {
    console.error('❌ Error updating subscription:', error);
    throw error;
  }
}

/**
 * Handle customer.subscription.deleted event
 * Cancels premium subscription and downgrades to free
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('🚫 Processing subscription cancellation:', subscription.id);
  
  const customerId = subscription.customer;
  
  try {
    // Find user by Stripe customer ID
    const usersSnapshot = await admin.firestore()
      .collection('users')
      .where('subscription.stripeCustomerId', '==', customerId)
      .limit(1)
      .get();

    if (usersSnapshot.empty) {
      console.warn('⚠️ No user found for customer:', customerId);
      return;
    }

    const userDoc = usersSnapshot.docs[0];
    
    await userDoc.ref.update({
      'subscription.status': 'canceled',
      'subscription.tier': 'free',
      'subscription.canceledAt': admin.firestore.FieldValue.serverTimestamp(),
      'subscription.updatedAt': admin.firestore.FieldValue.serverTimestamp()
    });
    
    console.log('✅ Subscription canceled for customer:', customerId);
    
  } catch (error) {
    console.error('❌ Error canceling subscription:', error);
    throw error;
  }
}

/**
 * Create Stripe Checkout Session
 * Called by frontend to initiate payment flow
 */
exports.createCheckoutSession = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    // Only accept POST requests
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    try {
      const { priceId, userId, userEmail } = req.body;

      if (!priceId || !userId || !userEmail) {
        return res.status(400).json({ 
          error: 'Missing required fields: priceId, userId, userEmail' 
        });
      }

      console.log('💳 Creating checkout session for user:', userId);

      // Create Stripe Checkout Session
      const session = await stripe.checkout.sessions.create({
        mode: 'subscription',
        payment_method_types: ['card'],
        line_items: [
          {
            price: priceId,
            quantity: 1,
          },
        ],
        success_url: `${req.headers.origin || 'https://confident-picks.com'}/?session_id={CHECKOUT_SESSION_ID}&success=true`,
        cancel_url: `${req.headers.origin || 'https://confident-picks.com'}/?canceled=true`,
        customer_email: userEmail,
        client_reference_id: userId,
        metadata: {
          userId: userId,
          priceId: priceId
        }
      });

      console.log('✅ Checkout session created:', session.id);

      res.json({ sessionId: session.id, url: session.url });

    } catch (error) {
      console.error('❌ Error creating checkout session:', error);
      res.status(500).json({ 
        error: 'Failed to create checkout session',
        message: error.message 
      });
    }
  });
});

/**
 * Test function to verify deployment
 * Can be called via: https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/testFunction
 */
exports.testFunction = functions.https.onRequest((req, res) => {
  res.json({
    status: 'ok',
    message: 'Confident Picks Cloud Functions are working!',
    timestamp: new Date().toISOString()
  });
});

