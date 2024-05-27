import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
# import plotly.offline as pyo
# pyo.init_notebook_mode()
from PIL import Image


##### DATA PREP
data = pd.read_csv('data.csv')
data.columns = data.columns.str.lower().str.replace(' ', '_')
data['order_date'] = pd.to_datetime(data['order_date'])
numeric_columns = ['sold_price_item_a', 'sold_price_item_b', 'list_price_item_a', 'list_price_item_b', 'total_item_a_discount', 'total_item_b_discount', 'overall_total_discount']
for col in numeric_columns:
    data[col] = data[col].astype(str).str.replace(',', '').replace('  -   ', '0').astype(float)

# Calculate the overall discount
data['overall_total_discount'] = data['total_item_a_discount'] + data['total_item_b_discount']
data['total_list_price'] = data.list_price_item_a + data.list_price_item_b
data['discount_percentage'] = data.overall_total_discount /data['total_list_price']
data['total_sales'] = data.total_list_price - data.overall_total_discount


### paging
my_page =st.sidebar.selectbox('Select Page', ['Data', 'Descriptive Analysis',
                                             'Prescriptive Analysis', 'Diagnostic Analysis'])


if my_page=='Data':
    st.title("Data")
    st.header("Data set")
    if st.checkbox('Show data', value = True):
        st.subheader('Data')
        val = st.slider('How many rows do you want to see?', min_value=10, max_value=130)
        data_load_state = st.text('Loading data...')
        st.write(data.head(val))
        data_load_state.markdown('Loading data...**done!**')

elif my_page=='Descriptive Analysis':
    option = st.sidebar.selectbox('Which question do you want to see?', ['Descriptive Analysis Q1', 
                                                                    'Descriptive Analysis Q2',
                                                                    'Descriptive Analysis Q3',
                                                                    'Descriptive Analysis Q4',
                                                                    'Descriptive Analysis Q5'])
    if option == 'Descriptive Analysis Q1':
        
        st.title("Historical Overall Discount of Item A and Item B")

        df =data[['order_date', 'total_item_a_discount', 'total_item_b_discount', 'overall_total_discount']]
        df.set_index('order_date', inplace=True)
        resampled_df = df.resample('D').sum().reset_index() #.fillna(0)

        # Plot the resampled data
        fig = px.line(resampled_df, x='order_date', y=['total_item_a_discount', 'total_item_b_discount',
                                                      'overall_total_discount'],
                      title='Total Item Discounts Resampled by Day',
                      labels={'value': 'Total Discounts', 'order_date': 'Date'},
                      template='plotly_dark')

        st.plotly_chart(fig)
        
        " Item A is normally being discounted. There are several instances during the period where there are significant spikes in discounts for this item. For item B, a huge discount was given on Apr 24, 2023. " 
    
    elif option =='Descriptive Analysis Q2':
        option = st.sidebar.selectbox('Which one do you want to see?', ['sector', 'country',
                                                                          'account_edition', 'quarter'])

        st.title("Discount Distributions")
        st.subheader("Determine the "+ option +" with highest discount." )

        # Group by sector and calculate the sum of the overall discount
        grouped_sector_df = data.groupby([option]).sum().reset_index()

        # Create bar plot for sector
        fig_sector = px.bar(grouped_sector_df, x=option, y='overall_total_discount',
                            title='Overall Total Discount by ' + option,
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')

        st.plotly_chart(fig_sector)

        grouped_df = data.groupby(['sector', 'country', 'account_edition', 'quarter']).sum().reset_index()
        max_discount_row = grouped_df.loc[grouped_df['overall_total_discount'].idxmax()]

        # Display the results
        "Sector with highest discount:", max_discount_row['sector']
        "Country with highest discount:", max_discount_row['country']
        "Edition with highest discount:", max_discount_row['account_edition']
        "Quarter with highest discount:", max_discount_row['quarter']
        #"Highest overall total discount:", max_discount_row['overall_total_discount']

    elif option =='Descriptive Analysis Q3':
        st.title("Quarter Over Quarter Percentage Change")

        data['quarter'] = data['order_date'].dt.to_period('Q')
        quarterly_discount = data.groupby('quarter')[['total_item_a_discount', 'total_item_b_discount']].sum()

        # Calculate the total discount (item A + item B) for each quarter
        quarterly_discount['total_discount'] = quarterly_discount['total_item_a_discount'] + quarterly_discount['total_item_b_discount']

        quarterly_discount = quarterly_discount.transpose()
        quarterly_discount['QoQ_percentage_change'] = 100*(quarterly_discount['2023Q2'] -quarterly_discount['2023Q1'])/quarterly_discount['2023Q1']

        quarterly_discount['QoQ_percentage_change'] = quarterly_discount['QoQ_percentage_change'].apply(lambda x: f"{x:,.2f}%")
        # quarterly_discount = quarterly_discount.reset_index(drop=True)
        quarterly_discount.columns = ['2023Q1', '2023Q2', 'QoQ_percentage_change']
        quarterly_discount['2023Q1'] = quarterly_discount['2023Q1'].apply(lambda x: f"{x:,.2f}")
        quarterly_discount['2023Q2'] = quarterly_discount['2023Q2'].apply(lambda x: f"{x:,.2f}")
        quarterly_discount

        "Discounts significantly increased in Quarter 2 for both items. Item B discount spiked by 4,888%."


    elif option =='Descriptive Analysis Q4':
        st.title("Relationship Between Account Segment and Discounting")
        st.subheader("Define the relationship between an Account Segment and discounting. What could be the business logic behind this relationship?")

        # Group by sector and calculate the sum of the overall discount
        grouped_seg_df = data.groupby(['account_segment'])[['overall_total_discount']].sum().reset_index()

        # Create bar plot for sector
        fig_seg = px.bar(grouped_seg_df, x='account_segment', y='overall_total_discount',
                            title='Overall Total Discount by Account Segment',
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')

        st.plotly_chart(fig_seg)

        "It is observed that the big enterprises got the most discounts. Meanwhile, small businesses and SOHO are the least discounted segments. This behavior is due to the fact we have give to customers value so we can retain their loyalty. Large-scale organizations such as Enterprises buys with huge quantities and and has a wide reach, therefore getting their loyalty would bring us profitable business."

    elif option=='Descriptive Analysis Q5':
        st.title("Interesting Observations")
        st.subheader('Interesting Observation 1')
        # Group by sector and calculate the sum of the overall discount
        grouped_acct_df = data.groupby(['account_name'])[['overall_total_discount']].sum().reset_index()

        # Create bar plot for sector
        fig_acct = px.bar(grouped_acct_df, x='account_name', y='overall_total_discount',
                            title='Overall Total Discount by Account Name',
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')
        st.plotly_chart(fig_acct)

        accounts = data[['account_name', 'overall_total_discount']].groupby('account_name').sum()/data[['account_name', 'overall_total_discount']][['overall_total_discount']].sum()#.reset_index()
        accounts = accounts.reset_index().rename(columns = {'overall_total_discount': 'overall_total_discount_proportion'})
        accounts['overall_total_discount_proportion'] = accounts['overall_total_discount_proportion'].astype(float)
        accounts['overall_total_discount_proportion'] = 100* accounts['overall_total_discount_proportion']
        accounts['overall_total_discount_proportion'] = accounts['overall_total_discount_proportion'].apply(lambda x: f"{x:.2f}%")

        acct = accounts[accounts['account_name'].isin(['H8', 'J1', 'X6'])].reset_index(drop=True)
        acct

        "Almost 48% of all the discounts given were granted to only 3 accounts namely H8, J1, and X6. Both H8 and J1 are enterprises while X6 belongs to the majors."


        st.subheader('Interesting Observation 2')
        # Group by sector and calculate the sum of the overall discount
        grouped_act_seg_df = data.groupby(['account_segment', 'quarter']).sum().reset_index()

        # Create bar plot for sector
        fig_act_seg = px.bar(grouped_act_seg_df, x='account_segment', y='overall_total_discount', color='quarter',
                            title='Overall Total Discount by Account Segments per Quarter',
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')

        st.plotly_chart(fig_act_seg)

        "The huge spike in discounts in Quarter 2 can be mainly attributed to the arrival of big enterprises. The 3 large accounts above also entered in Q2."

        st.subheader('Interesting Observation 3')
        # Group by sector and calculate the sum of the overall discount
        grouped_sec_df = data.groupby(['account_segment', 'sector']).sum().reset_index()

        # Create bar plot for sector
        fig_sec = px.bar(grouped_sec_df, x='account_segment', y='overall_total_discount', color='sector',
                            title='Overall Total Discount by Account Segment per Sector',
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')

        st.plotly_chart(fig_sec)

        "Education became the highest discounted sector due to accounts H8 and J1."

elif my_page=='Prescriptive Analysis': 
    option = st.sidebar.selectbox('Which question do you want to see?', ['Prescriptive Analysis Q1', 
                                                                    'Prescriptive Analysis Q2',
                                                                    'Prescriptive Analysis Q3'])
    if option == 'Prescriptive Analysis Q1':
        st.subheader('Question:')
        "If selling at a higher discount is considered as a poor pricing performance, did RingCentral perform well Quarter over Quarter? Why/Why not?"

        fig_hist = px.histogram(data, x='discount_percentage', nbins=10, color = 'quarter',
                       title='Distribution of Discount Percentages',
                       labels={'discount_percentage': 'Discount Percentage'},
                       template='plotly_dark')
        st.plotly_chart(fig_hist)

        disc = data.groupby('quarter')[['discount_percentage']].agg({'mean', 'median'})
        disc

        "If we only look at the amount of discounts, it seems that RingCentral gave an extreme amount of discount. However, if we look at the proportion of the discount versus the actual suggested retail price, the mean and the median proportions in quarter 1 and quarter 2 are almost the equal."

        st.markdown('#### Quarter-over-Quarter Change in Sales')

        data['total_sales'] = data.total_list_price - data.overall_total_discount
        quarterly_sales = data.groupby('quarter')[['sold_price_item_a', 'sold_price_item_b', 'total_sales']].sum().transpose()
        quarterly_sales['QoQ_percentage_change_sales'] =  100*(quarterly_sales['Q2'] -quarterly_sales['Q1'])/quarterly_sales['Q1']

        quarterly_sales['QoQ_percentage_change_sales'] = quarterly_sales['QoQ_percentage_change_sales'].apply(lambda x: f"{x:,.2f}%")
        quarterly_sales.columns = ['2023Q1', '2023Q2', 'QoQ_percentage_change_sales']

        quarterly_sales['2023Q1'] = quarterly_sales['2023Q1'].apply(lambda x: f"{x:,.2f}")
        quarterly_sales['2023Q2'] = quarterly_sales['2023Q2'].apply(lambda x: f"{x:,.2f}")

        quarterly_sales

        "RingCentral maintained the proportion of discounts it gives from Quarter 1 to Quarter 2. If we look more closely at the sales, we can see that by providing customers with 36% discount, RingCentral was able to increase its sales by 43%. With this, I believe that RingCentral performed well."

        "Discounts are key in attracting customers and increasing volume of sales, however, it also affects the profits. Giving discount is helpful as long as attracts and retains customers, and most importantly, as long as we still have a margin for profit. Product should never be sold below its production price. We should strike a balance and optimize our pricing such that we still encourage purchases while maintaining agreeable profit."


    elif option=='Prescriptive Analysis Q2':  
        st.subheader('Question:')
        "Using the given data set, is there a particular reason that drives this good/poor pricing QoQ performance? "

        d70 = data[data['discount_percentage'] >= .70]
        fig_cap = px.histogram(d70, x='discount_percentage', nbins=10, color = 'quarter',
                       title='Distribution of Discount Percentages',
                       labels={'discount_percentage': 'Discount Percentage'},
                       template='plotly_dark')
        st.plotly_chart(fig_cap)

        "I found some discounts in the dataset that are very questionable. The transactions above were given discounts that are 70% or above of the suggested retail price. Giving 92% of discount might be equivalent to selling below production price already. These are the instances we can improve on."


    elif option=='Prescriptive Analysis Q3':  
        st.subheader('Question:')  
        "Based on your findings, what pricing initiatives can you recommend for increasing/maintaining the pricing performance of Company XYZ?"
    
        account_sales =  data.groupby('account_name')[['total_sales', 'overall_total_discount']].sum().reset_index()

        fig_account_sales = px.line(account_sales, x='account_name', y=['total_sales', 'overall_total_discount'],
                            title='Overall Total Discount by Account',
                            labels={'overall_total_discount': 'Overall Total Discount'},
                            template='plotly_dark')

        st.plotly_chart(fig_account_sales)
        
        "We can observe that there are some accounts such as B17, H8, J1, and M4, that are getting significantly high discounts. We can consider recalibrating the discount rates for these accounts. It also might be interesting to note that we are getting high sales while giving low discounts from account DO2, a SOHO from the public sector."
        

elif my_page=='Diagnostic Analysis': 
    
    option = st.sidebar.selectbox('Which question do you want to see?', ['Diagnostic Analysis Q1', 
                                                                    'Diagnostic Analysis Q2',
                                                                    'Diagnostic Analysis Q3',
                                                                    'Diagnostic Analysis Q4'])
    
    st.subheader('Instruction:') 
    "You have been hired as a Senior Data Analyst to work in a bank. Your first assignment is to join your team in using analytics for the early detection of credit card fraud."
    "You have been given a database that contains all the credit card transaction details for the users."
    
    im2 = Image.open('RingCentral_Fraud_Detection.png')
    st.image(im2)
    
    if option == 'Diagnostic Analysis Q1':
        st.markdown("##### 1. List at least 5 data points that are required for the detection of a credit card fraud. ")
        
        "To detect possible credit card fraud, we can use the following features: " 
        " 1. IP Address "
        " 2. Transaction Time "
        " 3. Transaction Value "
        " 4. Shipping Address "
        " 5. Units Purchased "
        
    elif option == 'Diagnostic Analysis Q2':
        st.markdown("##### 2. Identify 3 errors that could impact the accuracy of your findings.")
        
        "Here are some noticeable errors in the dataset"
        " 1. The sample data is too small and not enough to establish what the normal behavior of a client. If we were given more data, we can build a fraud detection model using machine learning algorithms. "
        " 2. There are several missing values. "
        " 3. Transaction date has different formats that might lead to inaccuracies. "
        
    elif option == 'Diagnostic Analysis Q3':
        st.markdown("##### 3. Identify 2 irregularities that would lead you to believe the transaction may be suspect. ")
        
        im3 = Image.open('suspicious_transactions.PNG')
        st.image(im3)
        
        " The two transactions above look suspicious."
        " The transaction by user johnp on 03-06-2020 where he bought tools seems different from his other transactions. He made 3 transactions in the early morning of 03-06-2020. Among those 3 transactions, this particular transaction was sent on a different shipping address."
        " The last transaction by user ellend looks suspicious. It is placed around midnight and has significantly high transaction value than her normal transactions. Lastly, the IP address and shipping address are different from the other transactions. " 
        
        
    elif option == 'Diagnostic Analysis Q4':
        st.markdown("##### 4. Explain the provided data visualization chart. ")
        
        im1 = Image.open('value_per_transaction.PNG')
        st.image(im1)
        
        " The visualization shows the amount (in USD) of the transactions made by the 3 users johnp, davidg, and ellend. davidg's transactions are consistent all throughout. For ellend, there is spike in the transaction amount that could signal possibility of fraud. For johnp, his last 3 transactions have a significant increase in amount. " 
