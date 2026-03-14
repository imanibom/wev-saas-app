-- Wev Core Database Schema
-- PostgreSQL

-- Clients Table: Businesses (Pharmacies, Hospitals, Fashion Houses)
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('pharmacy', 'hospital', 'fashion')),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Journeys Table: Automation timelines and message sequences
CREATE TABLE journeys (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL, -- e.g., "12-Month Postpartum Journey"
    trigger_event VARCHAR(100) NOT NULL, -- e.g., "Rx_Filled_Event", "Order_Delivered_Event"
    wait_interval INTERVAL NOT NULL, -- e.g., '7 days', '3 days'
    message_payload TEXT NOT NULL, -- e.g., "How is the dosage?", "How does it fit?"
    response_type VARCHAR(50) NOT NULL, -- e.g., "Yes/No/SideEffect", "Rating (1-5)"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- End-Users Table: People (Patients, Mothers, Customers)
CREATE TABLE end_users (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    additional_data JSONB, -- Flexible field for industry-specific data (e.g., drug name, purchase history, size)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table: Log of sent messages and responses
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    journey_id INTEGER REFERENCES journeys(id) ON DELETE CASCADE,
    end_user_id INTEGER REFERENCES end_users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('outbound', 'inbound')), -- sent or received
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_expected BOOLEAN DEFAULT FALSE,
    response_received_at TIMESTAMP NULL,
    response_content TEXT NULL
);

-- Scheduled Messages Table: Queue for timed message sends
CREATE TABLE scheduled_messages (
    id SERIAL PRIMARY KEY,
    journey_id INTEGER REFERENCES journeys(id) ON DELETE CASCADE,
    end_user_id INTEGER REFERENCES end_users(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    message_payload TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_journeys_client_id ON journeys(client_id);
CREATE INDEX idx_end_users_client_id ON end_users(client_id);
CREATE INDEX idx_end_users_email ON end_users(email);
CREATE INDEX idx_end_users_phone ON end_users(phone);
CREATE INDEX idx_messages_journey_id ON messages(journey_id);
CREATE INDEX idx_messages_end_user_id ON messages(end_user_id);
CREATE INDEX idx_scheduled_messages_scheduled_at ON scheduled_messages(scheduled_at);
CREATE INDEX idx_scheduled_messages_status ON scheduled_messages(status);