import streamlit as st
import pandas as pd
import math
import io
import base64

# Set page title and favicon
st.set_page_config(page_title="Metrics Calculator", page_icon=":bar_chart:")

# Define function to calculate metrics
def calculate_metrics(your_plan, avg_plan_ref, ref_payout_percent, sales_conversion_rate, response_rate):
    payout = avg_plan_ref * (ref_payout_percent / 100)
    referrals_needed_to_be = your_plan / payout
    conversions_needed = referrals_needed_to_be / sales_conversion_rate
    touch_points_needed = math.ceil(conversions_needed / response_rate)
    
    return payout, referrals_needed_to_be, conversions_needed, touch_points_needed

# Define function to create a downloadable link
def create_download_link(df, format_type):
    if format_type == "XLSX":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Metrics", index=False)
        output.seek(0)
        excel_data = output.read()
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="metrics.xlsx">Download XLSX</a>'
    elif format_type == "PDF":
        # You can implement PDF export using libraries like pdfkit, weasyprint, or others
        # Here's a basic example using weasyprint:
        import weasyprint
        pdf = weasyprint.HTML(string=df.to_html()).write_pdf()
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="metrics.pdf">Download PDF</a>'
    else:
        href = ""
    return href

# Define main function
def main():
    # Add title and header
    st.markdown("<h1 style='color:navy'>Metrics Calculator</h1>", unsafe_allow_html=True)
    #st.markdown("<h2 style='color:navy'>This is the Calculated metrics for your AudienceLab Partners</h2>", unsafe_allow_html=True)
    
    # Add sidebar for input fields and file uploader
    st.sidebar.image("large.png") 
    with st.sidebar:
        # Add company logo at the top of the sidebar
        #st.sidebar.image("labb1.png", use_container_width=True)
        st.markdown("### Input Fields")
        manual_input = st.checkbox("Manual Input", value=False)
        
        if manual_input:
            your_plan = st.number_input("Plan ($)", value=2500.00)
            avg_plan_ref = st.number_input("Avg Plan Ref ($)", value=2500.00)
            ref_payout_percent = st.number_input("Ref Payout %", value=10.00)
            sales_conversion_rate = st.number_input("Sales Conversion Rate (%)", value=40.00)
            response_rate = st.number_input("Response Rate (%)", value=60.00)
        else:
            uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if manual_input or (uploaded_file is not None):
        if manual_input:
            # Use manual input values
            data = [{'Plan ($)': your_plan, 'Avg Plan Ref ($)': avg_plan_ref, 'Ref Payout %': ref_payout_percent, 'Sales Conversion Rate (%)': sales_conversion_rate, 'Response Rate (%)': response_rate}]
            df = pd.DataFrame(data)
        else:
            # Load Excel data into a DataFrame
            df = pd.read_excel(uploaded_file)
        
        # Perform calculations using data from the input
        payouts = []
        referrals_needed = []
        conversations_needed = []
        touch_points_needed = []
        
        for index, row in df.iterrows():
            payout, referrals_needed_to_be, conversations, touch_points = calculate_metrics(row['Plan ($)'], row['Avg Plan Ref ($)'], row['Ref Payout %'], row['Sales Conversion Rate (%)'] / 100, row['Response Rate (%)'] / 100)
            payouts.append(payout)
            referrals_needed.append(referrals_needed_to_be)
            conversations_needed.append(conversations)
            touch_points_needed.append(touch_points)
        
        # Add calculated columns to the DataFrame
        df['Payout ($)'] = payouts
        df['Referrals Needed'] = referrals_needed
        df['Conversations Needed'] = conversations_needed
        df['Touch Points Needed'] = touch_points_needed
        
        # Rearrange columns to follow the specified sequence
        column_sequence = ['Plan ($)', 'Avg Plan Ref ($)', 'Ref Payout %', 'Payout ($)', 'Referrals Needed', 'Sales Conversion Rate (%)', 'Response Rate (%)', 'Conversations Needed', 'Touch Points Needed']
        df = df[column_sequence]
        
        # Transpose the DataFrame to display the result vertically
        df = df.transpose()
        
        # Display metrics in a table
        st.markdown("<h2 style='color:navy'>Metrics</h2>", unsafe_allow_html=True)
        st.dataframe(df)
        
        # Create download buttons for XLSX and PDF formats
        download_format = st.selectbox("Select Download Format", ["XLSX", "PDF"])
        download_link = create_download_link(df, download_format)
        st.markdown(download_link, unsafe_allow_html=True)

        # Add success message
        st.success("Metrics calculated successfully!")
        
        # Add a logout button
        if st.button("Logout"):
            st.session_state.logged_in = False

if __name__ == "__main__":
    # Set background color
    st.markdown("<style>body {background-color: lightSkyBlue;}</style>", unsafe_allow_html=True)
    
    main()
