-- Sample Data for Fashion Pillar
-- Run after creating schema

-- Insert sample client (Fashion House)
INSERT INTO clients (name, type, contact_email) VALUES ('Chic Boutique', 'fashion', 'contact@chicboutique.com');

-- Insert sample journey (Fashion Fit Check)
INSERT INTO journeys (client_id, name, trigger_event, wait_interval, message_payload, response_type)
VALUES (
    1, -- client_id from above
    'Post-Purchase Fit Check',
    'Order_Delivered_Event',
    '3 days',
    'How does the [Item_Name] fit, [Customer_Name]?',
    'Rating (1-5)'
);

-- Insert sample end-user (Customer)
INSERT INTO end_users (client_id, name, email, phone, additional_data)
VALUES (
    1,
    'Jane Doe',
    'jane@example.com',
    '+1234567890',
    '{"purchase_history": ["Dress", "Shoes"], "size": "M"}'
);