import streamlit as st
import pandas as pd
from langchain.llms import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
load_dotenv()
st.set_page_config(
    page_title="KeenSight - Health-GPT",
    layout='wide')


# add the default prompts here
default_prompts = ["How many rows are in the dataset?",
                   "What's the dataset about?"]

with st.sidebar:
    OPEN_AI_API_KEY = st.text_input(
        'OpenAI API Key', placeholder='Enter your OpenAI API key', type='password')
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    csv = st.file_uploader(
        'Upload CSV', type=['csv']
    )
st.image("logo.png",width=200)
st.title("💬 Chat with csv")


def create_agent(data):
    llm = OpenAI(openai_api_key=OPEN_AI_API_KEY,model_name="gpt-3.5-turbo-instruct")
    # save last 2 conv in memory
    memory = ConversationBufferMemory(llm=llm, k=2)
    return create_pandas_dataframe_agent(llm, data, verbose=False, memory=memory)


def query_agent(agent, query):
    prompt = (f"""
            This is a dataset.
            Answer the question based on the dataset.
            If you do not know the answer, reply "I do not know."
            Below is the query.
            Query: {query}
    """
              )
    return agent.run(prompt)


def main():
    try:
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [
                {"role": "assistant", "content": "How can I assist you?"}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        if csv:
            data = pd.read_csv(
                csv)
            st.sidebar.write(data)
        if not OPEN_AI_API_KEY:
            st.stop()
        agent = create_agent(
            data)

        for prompt in default_prompts:
            if st.sidebar.button(prompt):
                with st.chat_message("user"):
                    st.write(prompt)
                    st.session_state.messages.append(
                        {"role": "user", "content": prompt})
        # User-provided prompt
        if prompt := st.chat_input("Ask a query?"):
            with st.chat_message("user"):
                st.write(prompt)
            st.session_state.messages.append(
                {"role": "user", "content": prompt})

        # Generate response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Generating response..."):
                    # Query the agent.
                    response = query_agent(agent=agent, query=prompt)
                    placeholder = st.empty()

                    placeholder.markdown(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
    except Exception as e:
        print(e)
        st.error(e)
        st.stop()


if __name__ == "__main__":
    main()
