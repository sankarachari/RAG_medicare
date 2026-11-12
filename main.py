import streamlit as st

# 1. Define the individual pages pointing to their respective file paths
home_page = st.Page("1_Plotting_Demo.py", title="Home", icon="🏠", default=True)
data_page = st.Page("2_Mapping_Demo.py", title="Data Dashboard", icon="📊")
settings_page = st.Page("3_DataFrame_Demo.py", title="Settings", icon="⚙️")
medicare_page = st.Page("4_ragstream.py", title="Medicare Q&A", icon="💊")

# 2. Bundle the pages into a navigation structure
# You can also use a dictionary here to group them into sections if needed.
pg = st.navigation([home_page, data_page, settings_page,medicare_page])

# 3. Run the navigation system
pg.run()