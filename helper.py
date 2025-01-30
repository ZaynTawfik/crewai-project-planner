#import os
#from dotenv import load_dotenv

#def load_env():
#    load_dotenv()  # Load .env file if available
#   os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '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')

import os
import streamlit as st

def load_env():
    os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
