const express = require('express');
const crypto = require('crypto');
const db = require('../models/db');

const router = express.Router();

// Shopify Webhook Secret (set in .env)
const SHOPIFY_WEBHOOK_SECRET = process.env.SHOPIFY_WEBHOOK_SECRET;

// Middleware to verify Shopify webhook
function verifyShopifyWebhook(req, res, next) {
  const hmac = req.get('X-Shopify-Hmac-Sha256');
  const body = JSON.stringify(req.body);
  const hash = crypto
    .createHmac('sha256', SHOPIFY_WEBHOOK_SECRET)
    .update(body, 'utf8')
    .digest('base64');

  if (hash === hmac) {
    next();
  } else {
    res.status(401).send('Unauthorized');
  }
}

// Webhook endpoint for Shopify order fulfillment
router.post('/shopify/order-fulfilled', express.raw({ type: 'application/json' }), verifyShopifyWebhook, async (req, res) => {
  try {
    const order = JSON.parse(req.body.toString());

    // Extract relevant data
    const customer = order.customer;
    const lineItems = order.line_items;
    const fulfillmentStatus = order.fulfillment_status; // Should be 'fulfilled'

    if (fulfillmentStatus !== 'fulfilled') {
      return res.status(200).send('Order not fulfilled yet');
    }

    // Assume client_id is passed or configured (for now, hardcode or get from shop domain)
    const clientId = 1; // From sample data

    // Check if journey exists for this trigger
    const journeyResult = await db.query(
      'SELECT * FROM journeys WHERE client_id = $1 AND trigger_event = $2 AND is_active = true',
      [clientId, 'Order_Delivered_Event']
    );

    if (journeyResult.rows.length === 0) {
      return res.status(200).send('No active journey for this trigger');
    }

    const journey = journeyResult.rows[0];

    // Create or update end-user
    let endUserResult = await db.query(
      'SELECT * FROM end_users WHERE client_id = $1 AND email = $2',
      [clientId, customer.email]
    );

    let endUserId;
    if (endUserResult.rows.length === 0) {
      // Insert new end-user
      const insertResult = await db.query(
        'INSERT INTO end_users (client_id, name, email, phone, additional_data) VALUES ($1, $2, $3, $4, $5) RETURNING id',
        [
          clientId,
          customer.first_name + ' ' + customer.last_name,
          customer.email,
          customer.phone,
          JSON.stringify({
            purchase_history: lineItems.map(item => item.name),
            size: lineItems[0]?.variant_title || 'N/A' // Assuming first item has size
          })
        ]
      );
      endUserId = insertResult.rows[0].id;
    } else {
      endUserId = endUserResult.rows[0].id;
      // Update additional_data if needed
    }

    // Calculate scheduled time
    const scheduledAt = new Date();
    scheduledAt.setTime(scheduledAt.getTime() + parseInterval(journey.wait_interval));

    // Insert into scheduled_messages
    await db.query(
      'INSERT INTO scheduled_messages (journey_id, end_user_id, scheduled_at, message_payload) VALUES ($1, $2, $3, $4)',
      [journey.id, endUserId, scheduledAt, journey.message_payload]
    );

    res.status(200).send('Webhook processed successfully');
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Internal Server Error');
  }
});

// Helper function to parse PostgreSQL INTERVAL to milliseconds
function parseInterval(interval) {
  // Simple parser for 'X days', 'X hours', etc.
  const match = interval.match(/(\d+)\s+(\w+)/);
  if (!match) return 0;
  const value = parseInt(match[1]);
  const unit = match[2].toLowerCase();
  switch (unit) {
    case 'day':
    case 'days':
      return value * 24 * 60 * 60 * 1000;
    case 'hour':
    case 'hours':
      return value * 60 * 60 * 1000;
    case 'minute':
    case 'minutes':
      return value * 60 * 1000;
    default:
      return 0;
  }
}

module.exports = router;