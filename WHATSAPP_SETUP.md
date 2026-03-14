# WhatsApp Business API Setup Guide

## Why WhatsApp?
- **Nigeria Market Leader**: Primary communication channel
- **High Engagement**: 40-60% response rates vs 2% for email
- **Business API**: Professional messaging with Twilio

## Twilio Setup Steps

### 1. Twilio Account & WhatsApp
1. Sign up for Twilio account
2. Enable WhatsApp in Twilio Console
3. Apply for WhatsApp Business API access
4. Get approved WhatsApp number (takes 1-2 weeks)

### 2. Webhook Configuration
1. In Twilio Console > WhatsApp > Senders
2. Set webhook URL: `https://yourdomain.com/webhooks/twilio/whatsapp`
3. Configure for incoming messages

### 3. Environment Variables
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Your WhatsApp number
TWILIO_WEBHOOK_URL=https://yourdomain.com/webhooks/twilio/whatsapp
```

### 4. Testing
- Send test messages via API
- Verify webhook receives responses
- Check message logging in database

## Message Personalization
- `[Customer_Name]`: Replaced with end-user name
- `[Item_Name]`: Replaced with first purchased item
- Extendable for more placeholders

## Response Handling
- Automatic logging of customer replies
- Links responses to original messages
- Ready for branching logic (future enhancement)

## Compliance Notes
- WhatsApp Business API terms
- Nigerian telecom regulations
- Data privacy (customer consent for messaging)