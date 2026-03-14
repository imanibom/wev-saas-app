const express = require('express');
const twilio = require('twilio');
const Sentiment = require('sentiment');
const db = require('../models/db');
const twilioService = require('../services/twilioService');

const router = express.Router();
const sentiment = new Sentiment();

// Twilio webhook for incoming WhatsApp messages
router.post('/twilio/whatsapp', express.urlencoded({ extended: false }), async (req, res) => {
  try {
    const from = req.body.From; // WhatsApp number: whatsapp:+1234567890
    const body = req.body.Body; // Message content
    const messageSid = req.body.MessageSid;

    // Extract phone number (remove whatsapp: prefix)
    const phoneNumber = from.replace('whatsapp:', '');

    // Find end_user by phone
    const userResult = await db.query('SELECT * FROM end_users WHERE phone = $1', [phoneNumber]);
    if (userResult.rows.length === 0) {
      console.log('Unknown user responded:', phoneNumber);
      return res.status(200).send('OK');
    }

    const endUser = userResult.rows[0];

    // Find the latest outbound message for this user
    const msgResult = await db.query(
      'SELECT m.*, j.response_type, c.contact_phone FROM messages m ' +
      'JOIN journeys j ON m.journey_id = j.id ' +
      'JOIN clients c ON j.client_id = c.id ' +
      'WHERE m.end_user_id = $1 AND m.message_type = $2 AND m.response_expected = true ' +
      'ORDER BY m.sent_at DESC LIMIT 1',
      [endUser.id, 'outbound']
    );

    if (msgResult.rows.length > 0) {
      const message = msgResult.rows[0];

      // Update with response
      await db.query(
        'UPDATE messages SET response_received_at = $1, response_content = $2 WHERE id = $3',
        [new Date(), body, message.id]
      );

      // Analyze sentiment
      const result = sentiment.analyze(body);
      const sentimentScore = result.score; // -5 to +5
      const isNegative = sentimentScore < -1;
      const isEmergency = /rash|dizzy|nausea|pain|emergency|help/i.test(body.toLowerCase());

      console.log(`Response from ${endUser.name}: "${body}" (Sentiment: ${sentimentScore})`);

      // Alert system for negative/emergency responses
      if (isNegative || isEmergency) {
        const alertMessage = `ALERT: ${endUser.name} (${phoneNumber}) reported: "${body}". Sentiment: ${sentimentScore}. Please follow up immediately.`;

        // Send SMS alert to business contact
        if (message.contact_phone) {
          await twilioService.sendSMS(message.contact_phone, alertMessage);
          console.log(`Alert sent to business: ${message.contact_phone}`);
        }

        // TODO: Send email alert (integrate nodemailer)
      }

      // TODO: Implement branching logic based on response_type and content
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('Error processing WhatsApp response:', error);
    res.status(500).send('Error');
  }
});

module.exports = router;