const twilio = require('twilio');

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;
const whatsappNumber = process.env.TWILIO_WHATSAPP_NUMBER; // WhatsApp-enabled number

let client = null;
if (accountSid && accountSid.startsWith('AC') && authToken) {
  client = twilio(accountSid, authToken);
}

// Send WhatsApp message
async function sendWhatsAppMessage(to, message) {
  if (!client) {
    console.log('Twilio client not initialized - skipping message send');
    return { success: false, error: 'Twilio not configured' };
  }
  try {
    const response = await client.messages.create({
      body: message,
      from: `whatsapp:${whatsappNumber}`,
      to: `whatsapp:${to}`
    });
    return { success: true, messageId: response.sid };
  } catch (error) {
    console.error('Error sending WhatsApp message:', error);
    return { success: false, error: error.message };
  }
}

// Send SMS fallback (if needed)
async function sendSMS(to, message) {
  try {
    const response = await client.messages.create({
      body: message,
      from: twilioPhoneNumber,
      to: to
    });
    return { success: true, messageId: response.sid };
  } catch (error) {
    console.error('Error sending SMS:', error);
    return { success: false, error: error.message };
  }
}

module.exports = {
  sendWhatsAppMessage,
  sendSMS
};