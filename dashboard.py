import streamlit as st
import os
from datetime import datetime, timedelta

# Try to import psycopg2 with error handling
try:
    import psycopg2
except ImportError:
    st.error("❌ psycopg2 not found. Please install with: pip install psycopg2-binary")
    st.stop()

# Try to import sentiment analyzer
try:
    from sentiment_analyzer import analyze_sentiment
except ImportError:
    st.warning("⚠️ Sentiment analyzer not available. Some features may be limited.")
    analyze_sentiment = None

# Database connection
def get_db_connection():
    try:
        return psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/wev_db'))
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.error("Please check your DATABASE_URL in environment variables")
        st.stop()

# Page config
st.set_page_config(page_title="Wev Command Center", page_icon="📱", layout="wide")

st.title("📱 Wev Command Center")
st.markdown("Manage automated customer journeys and monitor responses")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigation", ["Start Journey", "Monitor Responses", "Analytics"])

if page == "Start Journey":
    st.header("🚀 Start New Customer Journey")

    # Get available clients and journeys
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get clients
        cur.execute("SELECT id, name, industry FROM clients ORDER BY name")
        clients = cur.fetchall()

        # Get journeys
        cur.execute("SELECT id, name, trigger_type FROM journeys WHERE is_active = true ORDER BY name")
        journeys = cur.fetchall()

        cur.close()
        conn.close()

        if not clients:
            st.warning("No clients found. Please add clients to the database first.")
        else:
            # Client selection
            client_options = {f"{name} ({type})": id for id, name, type in clients}
            selected_client_name = st.selectbox("Select Business", list(client_options.keys()))
            client_id = client_options[selected_client_name]

            # Journey selection
            if journeys:
                journey_options = {name: id for id, name, trigger in journeys}
                selected_journey_name = st.selectbox("Select Journey Type", list(journey_options.keys()))
                journey_id = journey_options[selected_journey_name]

                # Customer details
                st.subheader("Customer Information")
                col1, col2 = st.columns(2)

                with col1:
                    customer_name = st.text_input("Customer Name")
                    customer_phone = st.text_input("Phone Number (with country code)")

                with col2:
                    customer_email = st.text_input("Email (optional)")
                    additional_data = st.text_area("Additional Data (JSON format)", placeholder='{"item": "Silk Kaftan", "size": "XL"}')

                # Start journey button
                if st.button("🚀 Start Wev Journey", type="primary"):
                    if not customer_name or not customer_phone:
                        st.error("Please fill in customer name and phone number")
                    else:
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()

                            # Insert or update end-user
                            cur.execute("""
                                INSERT INTO end_users (client_id, name, email, phone, additional_data)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (client_id, phone)
                                DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, additional_data = EXCLUDED.additional_data
                                RETURNING id
                            """, (client_id, customer_name, customer_email or None, customer_phone, additional_data or '{}'))

                            end_user_id = cur.fetchone()[0]

                            # Get journey details
                            cur.execute("SELECT wait_interval, message_payload FROM journeys WHERE id = %s", (journey_id,))
                            journey_data = cur.fetchone()
                            wait_interval, message_payload = journey_data

                            # Calculate scheduled time (parse interval)
                            # For simplicity, assume 'X days' format
                            days = int(wait_interval.split()[0]) if 'day' in wait_interval else 0
                            scheduled_at = datetime.now() + timedelta(days=days)

                            # Schedule message
                            cur.execute("""
                                INSERT INTO scheduled_messages (journey_id, end_user_id, scheduled_at, message_payload)
                                VALUES (%s, %s, %s, %s)
                            """, (journey_id, end_user_id, scheduled_at, message_payload))

                            conn.commit()
                            cur.close()
                            conn.close()

                            st.success(f"✅ Journey started for {customer_name}! Message scheduled for {scheduled_at.strftime('%Y-%m-%d %H:%M')}")

                        except Exception as e:
                            st.error(f"Error starting journey: {str(e)}")
            else:
                st.warning("No active journeys found. Please create journeys first.")

    except Exception as e:
        st.error(f"Database connection error: {str(e)}")

elif page == "Monitor Responses":
    st.header("📊 Monitor Customer Responses")

    # Add sentiment analysis demo
    st.subheader("🔍 Sentiment Analysis Demo")
    test_message = st.text_area("Test message for analysis:", "I feel dizzy and have a rash")
    if st.button("Analyze Sentiment"):
        if test_message:
            result = analyze_sentiment(test_message, "pharmacy")
            col1, col2, col3 = st.columns(3)
            col1.metric("Compound Score", f"{result['compound']:.2f}")
            col2.metric("Needs Review", "Yes" if result['needs_human_review'] else "No")
            col3.metric("Alert Keywords", len(result['alert_keywords']))

            if result['alert_keywords']:
                st.warning(f"🚨 Alert keywords detected: {', '.join(result['alert_keywords'])}")

    st.markdown("---")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get recent messages with responses
        cur.execute("""
            SELECT m.sent_at, m.content, m.response_content, m.response_received_at,
                   eu.name, eu.phone, c.name as client_name, c.type as pillar
            FROM messages m
            JOIN end_users eu ON m.end_user_id = eu.id
            JOIN journeys j ON m.journey_id = j.id
            JOIN clients c ON j.client_id = c.id
            WHERE m.response_expected = true AND m.response_content IS NOT NULL
            ORDER BY m.response_received_at DESC
            LIMIT 50
        """)

        responses = cur.fetchall()
        cur.close()
        conn.close()

        if responses:
            # Analyze sentiment for each response
            analyzed_responses = []
            for resp in responses:
                sentiment = analyze_sentiment(resp[2] or "", resp[7])  # response_content, pillar
                analyzed_responses.append(resp + (sentiment,))

            # Display as table with sentiment
            response_data = []
            for resp in analyzed_responses:
                sentiment = resp[8]
                response_data.append({
                    'Date': resp[3].strftime('%Y-%m-%d %H:%M') if resp[3] else 'N/A',
                    'Customer': resp[4],
                    'Phone': resp[5],
                    'Business': resp[6],
                    'Pillar': resp[7],
                    'Response': resp[2],
                    'Sentiment': f"{sentiment['compound']:.2f}",
                    'Needs Review': 'Yes' if sentiment['needs_human_review'] else 'No',
                    'Alert Keywords': ', '.join(sentiment['alert_keywords']) if sentiment['alert_keywords'] else 'None'
                })

            st.dataframe(response_data)

            # Summary stats
            total_responses = len(analyzed_responses)
            needs_review = sum(1 for r in analyzed_responses if r[8]['needs_human_review'])
            has_alerts = sum(1 for r in analyzed_responses if r[8]['has_alert_keywords'])

            st.markdown("### Response Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Responses", total_responses)
            col2.metric("Needs Human Review", needs_review)
            col3.metric("With Alert Keywords", has_alerts)

        else:
            st.info("No responses received yet.")

    except Exception as e:
        st.error(f"Error loading responses: {str(e)}")

elif page == "Analytics":
    st.header("📈 Journey Analytics")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Basic metrics
        cur.execute("SELECT COUNT(*) FROM end_users")
        total_customers = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM messages WHERE message_type = 'outbound'")
        total_messages = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM messages WHERE response_content IS NOT NULL")
        total_responses = cur.fetchone()[0]

        cur.close()
        conn.close()

        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", total_customers)
        col2.metric("Messages Sent", total_messages)
        col3.metric("Responses Received", total_responses)

        if total_messages > 0:
            response_rate = (total_responses / total_messages) * 100
            st.metric("Response Rate", f"{response_rate:.1f}%")

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Wev Command Center - Automating Customer Care*")