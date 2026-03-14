const express = require('express');
const cron = require('node-cron');
require('dotenv').config();
const db = require('./models/db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use('/webhooks', require('./routes/shopify')); // Mount Shopify routes
app.use('/webhooks', require('./routes/twilio')); // Mount Twilio routes

// Basic route
app.get('/', (req, res) => {
  res.json({ message: 'Wev SaaS API is running' });
});

// Test DB connection route
app.get('/test-db', async (req, res) => {
  try {
    const result = await db.query('SELECT NOW()');
    res.json({ message: 'Database connected', time: result.rows[0].now });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Placeholder for workflow scheduler
cron.schedule('0 0 * * *', () => {
  console.log('Running daily workflow check...');
  // TODO: Implement Trigger → Cadence → Action logic
});

// Start server
app.listen(PORT, () => {
  console.log(`Wev server running on port ${PORT}`);
});

module.exports = app;