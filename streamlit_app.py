# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose fruits you want in your smoothie:")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:',name_on_order)

# Assuming you have already defined the 'session' and 'my_dataframe' variables
conn = st.connection("snowflake")
session = conn.session()

# Display the dataframe
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
                                                                                            
#convert snowpark dataframe to Pandas dataframe
pd_df=my_dataframe.to_pandas()

st.dataframe(pd_df)  
#st.stop()
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list= st.multiselect(
    'Choose up to 5 ingredients:'
,my_dataframe
,max_selections =5
)

# Assuming you have an `ingredients_list` variable, you can check if it's not null like this:
if ingredients_list:
    
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutritional Information')
        #st.write(ingredients_string)
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+fruit_chosen)
        fv_df=st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients,name_on_order)
                   VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""
     
    st.write(my_insert_stmt)
        
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!',icon="✅")

