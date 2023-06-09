# Bring in deps
import os 
import requests
import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain 
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper 


# apikey = st.secrets['API_KEY']

st.title('📝 YoutubeScript GPT')


apikey = st.text_input('Enter your API key here' , type='password') 
st.markdown('_[To grab your apikey](https://platform.openai.com/account/api-keys) or check OpenAI website_')


if apikey:
    
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer {}'.format(apikey)

    response = session.get('https://api.openai.com/v1/engines')

    if response.status_code == 200:
        print('Success!')

        os.environ['OPENAI_API_KEY'] = apikey

        # App framework

        # apikey = st.text_input('Enter your API key here') 
        prompt = st.text_input('Plug in your prompt here') 

        # Prompt templates
        title_template = PromptTemplate(
            input_variables = ['topic'], 
            template='write me a youtube video title about {topic}'
        )

        script_template = PromptTemplate(
            input_variables = ['title', 'wikipedia_research'], 
            template='write me a youtube video script based in on this title TITLE: {title} while leveraging this wikipedia reserch:{wikipedia_research} '
        )

        # Memory 
        title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')
        script_memory = ConversationBufferMemory(input_key='title', memory_key='chat_history')


        # Llms
        llm = OpenAI(temperature=0.9, max_tokens=1000) 
        title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
        script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True, output_key='script', memory=script_memory)

        wiki = WikipediaAPIWrapper()

        # Show stuff to the screen if there's a prompt
        if prompt: 
            title = title_chain.run(prompt)
            wiki_research = wiki.run(prompt) 
            script = script_chain.run(title=title, wikipedia_research=wiki_research)

            st.write(title) 
            st.write(script) 

            with st.expander('Title History'): 
                st.info(title_memory.buffer)

            with st.expander('Script History'): 
                st.info(script_memory.buffer)

            with st.expander('Wikipedia Research'): 
                st.info(wiki_research)

    else:
        st.write('Please enter a valid API key')
        print('Failure!')
