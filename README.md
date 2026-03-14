# Wev SaaS App

## Tech Stack

- **Backend**: Node.js with Express
  - Handles APIs and scheduled tasks (CRON jobs via node-cron)
- **Database**: PostgreSQL
  - Reliable for relational data (customers linked to purchase history)
- **Messaging Engine**: Twilio
  - For SMS/WhatsApp integration
- **Environment Management**: dotenv
  - For secure configuration

## Database Schema

See `schema.sql` for the core data structure:

- **Clients**: Businesses (pharmacies, hospitals, fashion houses)
- **Journeys**: Automation workflows with triggers, intervals, messages, and response types
- **End-Users**: People with contact info and industry-specific data
- **Messages**: Log of sent messages and responses
- **Scheduled Messages**: Queue for timed message delivery

## Industry Connectors

### Fashion (Shopify Integration)
- Webhook endpoint: `POST /webhooks/shopify/order-fulfilled`
- Verifies HMAC for security
- Triggers journey when order is fulfilled
- Extracts customer data and schedules follow-up messages

### Health Tech (FHIR Research)
See `FHIR_RESEARCH.md` for details on healthcare interoperability standards.

## Communication Channel

### WhatsApp Business API (Primary)
- **Provider**: Twilio (high response rates in Nigeria: 40-60%)
- **Features**:
  - Automated personalized messages with customer/item data
  - Incoming response handling via webhooks
  - Message logging and response tracking
  - **Sentiment Analysis**: Automatic categorization of responses
  - **Alert System**: SMS alerts for negative/emergency feedback
- **Setup**: Configure Twilio WhatsApp number and webhook URL
- **Fallback**: SMS capability available

## Response Intelligence

### Sentiment Analysis
- **Library**: `sentiment` (Node.js)
- **Scoring**: -5 (very negative) to +5 (very positive)
- **Triggers**: Alerts for scores < -1 or emergency keywords

### Alert System
- **Conditions**: Negative sentiment or emergency keywords (rash, dizzy, pain, etc.)
- **Action**: Immediate SMS to business contact phone
- **Future**: Email alerts, dashboard notifications

## MVP Dashboard

### Streamlit Command Center
- **File**: `dashboard.py`
- **Features**:
  - Start manual customer journeys
  - Monitor incoming responses
  - Basic analytics (customers, messages, response rates)
- **Setup**: Run with `streamlit run dashboard.py`
- **Requirements**: Python virtual environment with streamlit, psycopg2-binary

## Getting Started

1. **Backend Setup**:
   ```bash
   npm install
   # Configure .env with database and Twilio credentials
   node src/app.js
   ```

2. **Database Setup**:
   ```bash
   # Create PostgreSQL database
   psql -U postgres -c "CREATE DATABASE wev_db;"
   psql -U postgres -d wev_db -f schema.sql
   psql -U postgres -d wev_db -f sample_data.sql
   ```

3. **Dashboard**:
   ```bash
   # Activate Python venv and run dashboard
   .venv\Scripts\activate
   streamlit run dashboard.py
   ```

   **Alternative (Windows)**: Double-click `run_dashboard.bat`

   **Troubleshooting**:
   - If `ModuleNotFoundError: No module named 'psycopg2'`, run: `pip install psycopg2-binary`
   - Ensure virtual environment is activated before running streamlit
   - Check DATABASE_URL environment variable
   - If issues persist, use: `python -m streamlit run dashboard.py`

## Project Structure

- `src/app.js`: Main Express application
- `src/routes/`: API routes
- `src/models/`: Database models
- `src/services/`: Business logic and integrations (e.g., Twilio)
- `src/schedulers/`: Automated workflow schedulers
- `.env`: Environment variables (not committed to git)

## Getting Started

1. Install dependencies: `npm install`
2. Set up PostgreSQL database
3. Configure `.env` with Twilio credentials and DB connection
4. Run: `node src/app.js`

## Workflow Logic (Fashion Pillar)

See the Mermaid diagram in the project for the Trigger → Cadence → Action flow.