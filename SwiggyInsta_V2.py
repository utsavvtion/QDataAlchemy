#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import schedule
import numpy as np
import re


# In[2]:



# Initialize Edge WebDriver
options = EdgeOptions()
#options.add_argument('--headless')
driver = webdriver.Edge(options=options)

# List of keywords to search
list_search = ['Dairy','Bread','Eggs','Snacks','Bakery','Biscuits','Tea','Coffee','Atta','Rice','Dal','Masala','Oil','Sauces','Spreads']
Pincode="400709"
pin = 1
# Initialize an empty list to store the scraped data
final_data = []

for keyword in list_search:
    # Open the URL with the current search keyword
    driver.get(f"https://www.swiggy.com/instamart/search?custom_back=true&query={keyword}")
    time.sleep(3)
    if pin==1:
        try:
            pincode_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[2]/div[2]/div[1]')))
            pincode_box.click()
            time.sleep(3)
            pincode_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div[1]/div/input')))
            pincode_box.click()
            time.sleep(3)
            pincode_box.send_keys(Pincode)
            pincode_box.send_keys(Keys.ENTER)
            time.sleep(2)
            sel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div[2]/div/div[2]/div[1]/div[2]')))
            sel.click()
            time.sleep(2)
            el2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div[2]/div[2]/div/div[4]')))
            sel2.click()
        except:
            pass
    try:
        clos = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[7]/div/div[2]/div/div[2]')))
        clos.click()
    except:
        pass
    
    # Define the base XPath for the data items
    base_xpath = '/html/body/div[1]/div/div/div/div[4]'
    
    # Scraping loop with scrolling
    list_data = []
    while True:
        # Scrape visible data on the current page
        text_box = driver.find_elements(By.XPATH, base_xpath)
        
        # Append text content from the items
        for i in text_box:
            list_data.append(i.text)
        
        # Scroll down slowly to load more content
        scroll_height_before = driver.execute_script("return document.body.scrollHeight")
        
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load
        
        # Check if new content has been loaded
        scroll_height_after = driver.execute_script("return document.body.scrollHeight")
        
        if scroll_height_before == scroll_height_after:
            print(f"Reached the bottom of the page for keyword '{keyword}'.")
            break
    pin += 1
    # Append scraped data with the current keyword
    for item in list_data:
        # Get current timestamp
        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        
        final_data.append({
            'Keyword': keyword,
            'Data': item,
            'Timestamp': int(current_time),  # Unix timestamp as an integer
            'Date': current_datetime.strftime('%Y-%m-%d'),  # Date in YYYY-MM-DD format
            'Time': current_datetime.strftime('%H:%M:%S')  # Time in HH:MM:SS format
        })
    # Append scraped data with the current keyword
    #for item in list_data:
        #final_data.append({'Keyword': keyword, 'Data': item})
    
    print(f"Collected {len(list_data)} items for keyword '{keyword}'.")
    time.sleep(5)

# Convert the final data into a DataFrame
df = pd.DataFrame(final_data)

# Save the DataFrame to a CSV file
#df.to_csv('scraped_data.csv', index=False)

# Print summary
print(f"Total collected data: {len(final_data)} items.")
print(df.head())

# Close the driver
driver.quit()


# In[88]:


import re

# Initialize an empty list to store structured data
structured_data = []

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    keyword = row['Keyword']
    data = row['Data']
    timestamp = row['Timestamp']
    date = row['Date']
    time = row['Time']
    
    # Use a regular expression to split data based on 'ADD' or 'Out of Stock'
    items = re.split(r'(ADD|Out of Stock|options|Sold Out|Add to Cart|Notify)', data)
    
    # Process items in pairs: each item is followed by its corresponding separator
    for i in range(0, len(items) - 1, 2):
        item = items[i].strip()  # The product details
        separator = items[i + 1].strip()  # Either 'ADD' or 'Out of Stock'
        
        if not item:  # Skip empty strings resulting from split
            continue
        
        # Split item into lines
        details_split = item.split('\n')
        
        # Combine all lines into a dictionary dynamically
        product_data = {
            'Keyword': keyword,
            'Separator': separator,  # 'ADD' or 'Out of Stock'
            'Data': data,  # Retain the original 'Data' column for reference
            'Timestamp': timestamp,  # Add 'Timestamp' to structured data
            'Date': date,  # Add 'Date' to structured data
            'Time': time   # Add 'Time' to structured data
        }
        
        # Add each line from details_split as a separate field with dynamic keys
        for j, detail in enumerate(details_split):
            product_data[f'Field_{j+1}'] = detail
        
        # Append the product data to the structured data list
        structured_data.append(product_data)

# Convert the structured data into a new DataFrame
df_structured = pd.DataFrame(structured_data)


# In[ ]:



df_structured[['Discount', 'Delivery_Time', 'Ad','Imported', 'Product', 'Pack_Size', 'Final_Price', 'Actual_Price','Stock']] = np.nan
# Create the new columns in the DataFrame and initialize them with empty strings
new_columns = [
    'Discount', 'Delivery_Time', 'Ad', 'Imported', 
    'Product', 'Pack_Size', 'Final_Price', 'Actual_Price'
]
for col in new_columns:
    df_structured[col] = ""

# Function to classify content
def classify_content(row):
    # Variable to track if we've assigned Product
    product_assigned = False

    for i, col in enumerate(['Field_1', 'Field_2', 'Field_3', 'Field_4', 'Field_5', 'Field_6', 'Field_7', 'Field_8', 'Field_9', 'Field_10']):
        value = str(row[col]) if pd.notna(row[col]) else ""

        # Check for 'Discount' (case-insensitive and starts with "% off" or "%off")
        if '% off' in value.lower():
            row['Discount'] = value
        
        # Check for 'Delivery Time' (case-insensitive and starts with a number followed by space)
        elif re.match(r'^\d+ ', value):  # Regular expression for numbers followed by a space
            # Check if it contains 'mins', 'hrs', etc., case-insensitive
            if any(unit in value.lower() for unit in ['mins']):
                row['Delivery_Time'] = value
        
        # Check for 'Ad'
        elif value.strip().lower() == 'ad':  # Exact match for "Ad" (case-insensitive)
            row['Ad'] = value
        elif value.strip() == 'Handpicked':   # Exact match for "Imported" (case-sensitive)
            row['Imported'] = value
        
        # Check for 'Pack Size' criteria
        elif any(char.isdigit() for char in value) and any(unit in value.lower() for unit in ['g',' g', 'kg', 'l','pack','unit','units','packs','piece','pieces']):
            # Pack size should be assigned only after Product
            if not product_assigned:
                row['Product'] = value  # Assign to Product if it's the first content
                product_assigned = True
            elif '₹' not in value:
                row['Pack_Size'] = value  # Assign to Pack_Size if the content doesn't contain ₹
        # Handle final and actual price
        elif '₹' in value:
            if row['Final_Price'] == "":
                row['Final_Price'] = value
            else:
                row['Actual_Price'] = value
        else:
            # If no other condition is met, assign to Product if not assigned yet
            if not product_assigned:
                row['Product'] = value
                product_assigned = True

    # If Product was assigned first, assign the next non-₹ value to Pack_Size
    if product_assigned and row['Pack_Size'] == "":
        for i, col in enumerate(['Field_1', 'Field_2', 'Field_3', 'Field_4', 'Field_5', 'Field_6', 'Field_7', 'Field_8', 'Field_9', 'Field_10']):
            value = str(row[col]) if pd.notna(row[col]) else ""
            if '₹' not in value and row['Pack_Size'] == "":
                row['Pack_Size'] = value
                break

    return row

# Apply the classification function row by row
df_structured = df_structured.apply(classify_content, axis=1)

df_structured.loc[df_structured[df_structured['Separator']=='Sold Out'].index,'Stock'] = 'Out of Stock'


# In[ ]:


df_structured['Actual_Price'] = np.nan
df_structured['Final_Price'] = np.nan

indx1 =df_structured[(df_structured['Field_9'].notnull()) & (df_structured[f"Field_9"].str.isdigit()) &(df_structured['Field_9'].str.len() >= 2)&(df_structured['Actual_Price'].isna())].index
df_structured.loc[indx1, "Actual_Price"] = df_structured.loc[indx1, 'Field_9']
df_structured.loc[indx1, "Final_Price"] = df_structured.loc[indx1, 'Field_8']


indx2 =df_structured[(df_structured['Field_8'].notnull()) & (df_structured[f"Field_8"].str.isdigit()) &(df_structured['Field_8'].str.len() >= 2)&(df_structured['Actual_Price'].isna())].index
df_structured.loc[indx2, "Actual_Price"] = df_structured.loc[indx2, 'Field_8']
df_structured.loc[indx2, "Final_Price"] = df_structured.loc[indx2, 'Field_7']

indx3 =df_structured[(df_structured['Field_7'].notnull()) & (df_structured[f"Field_7"].str.isdigit()) &(df_structured['Field_7'].str.len() >= 2)&(df_structured['Actual_Price'].isna())].index
df_structured.loc[indx3, "Actual_Price"] = df_structured.loc[indx3, 'Field_7']
df_structured.loc[indx3, "Final_Price"] = df_structured.loc[indx3, 'Field_6']

indx4 =df_structured[(df_structured['Field_6'].notnull()) & (df_structured[f"Field_6"].str.isdigit()) &(df_structured['Field_6'].str.len() >= 2)&(df_structured['Final_Price'].isna())].index
df_structured.loc[indx4, "Final_Price"] = df_structured.loc[indx4, 'Field_6']

indx5 =df_structured[(df_structured['Field_5'].notnull()) & (df_structured[f"Field_5"].str.isdigit()) &(df_structured['Field_5'].str.len() >= 2)&(df_structured['Final_Price'].isna())].index
df_structured.loc[indx5, "Final_Price"] = df_structured.loc[indx5, 'Field_5']


# Define the keywords to check
keywords = ['g', ' g', 'kg', 'l', 'pack', 'unit', 'units', 'packs', 'piece', 'pieces']

# Create a regex pattern to match any combination of the keywords
pattern = '|'.join(keywords)

# Check for the keywords in the Final_Price column
matching_rows = df_structured['Final_Price'].str.contains(pattern, case=False, na=False)

# Copy Actual_Price to Final_Price for matching rows
df_structured.loc[matching_rows, 'Final_Price'] = df_structured.loc[matching_rows, 'Actual_Price']


# In[24]:


df_structured['app'] = 'Swiggy Instamart'


# In[25]:


df_structured = df_structured[['app','Keyword', 'Separator', 'Data', 'Timestamp', 'Date', 'Time',
        'Discount', 'Delivery_Time', 'Ad',
       'Imported', 'Product', 'Pack_Size', 'Final_Price', 'Actual_Price','Stock']]


# In[26]:


#df_structured.to_excel('Blinkit_Sample.xlsx',index=False)
from datetime import datetime

# Get the current date and time
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Define the file name with the current date and time
file_name = f'SwiggyInsta_{current_datetime}.xlsx'

# Save the DataFrame to Excel
df_structured.to_excel(file_name, index=False)


# In[ ]:




