#!/usr/bin/env python
# coding: utf-8

# In[4]:


## If Internet Connectivity was good then we can run in one go or else skip next cell and run one by one scraping for each app.
## Use below cell code for parallel run 


# In[2]:


import subprocess
import concurrent.futures

def run_script(script_name):
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{script_name} executed successfully.")
    else:
        print(f"Error in {script_name}: {result.stderr}")

def main():
    scripts = ['Blinkit_V1.py', 'Bigbasket_V1.py',  'SwiggyInsta_V1.py','Zepto_V1.py']

    # Use ThreadPoolExecutor to run scripts in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_script, scripts)

if __name__ == "__main__":
    main()


# In[ ]:


## Use below code for sequential run 


# import subprocess
# 
# def run_script(script_name):
#     result = subprocess.run(['python', script_name], capture_output=True, text=True)
#     if result.returncode == 0:
#         print(f"{script_name} executed successfully.")
#     else:
#         print(f"Error in {script_name}: {result.stderr}")
# 
# def main():
#     # Run each script independently
#     run_script('Blinkit_V1.py')
#     run_script('Bigbasket_V1.py')
#     run_script('Zepto_V1.py')
#     run_script('SwiggyInsta_V1.py')
# 
# if __name__ == "__main__":
#     main()
# 

# In[ ]:




