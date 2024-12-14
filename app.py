import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.tools import Tool
from langchain_experimental.tools.python.tool import PythonREPLTool


# Load .env file
load_dotenv()


# Initialize the agent
def initialize_agent(excel_file):
    # Convert Excel to CSV
    df_excel = pd.read_excel(excel_file, sheet_name='Sheet1', header=1)
    csv_file_path = '/tmp/temp.csv'
    df_excel.to_csv(csv_file_path, index=False)

    # Initialize LLM
    # Get API Key from environment variable
    groq_api = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(temperature=0, model="llama3-70b-8192", api_key=groq_api)

    # Include tools for calculations and Python code execution
    python_tool = PythonREPLTool()  # Enables calculations and code execution

    tools = [
        Tool(name="Python REPL", func=python_tool.run, description="Useful for performing calculations and solving math problems."),
    ]

    # Create agent with additional tools
    agent = create_csv_agent(llm, csv_file_path, verbose=True, tools=tools, allow_dangerous_code=True)
    return agent

# Query function
def query_data(agent, query):
    response = agent.invoke(query)
    return response

# Generate and display a plot
def generate_plot():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30])  # Example plot data
    ax.set_title("Sample Plot")
    st.pyplot(fig)

# Save conversation
def save_conversation(title, messages):
    if "saved_conversations" not in st.session_state:
        st.session_state.saved_conversations = {}
    st.session_state.saved_conversations[title] = messages

# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Excel Query Assistant", layout="wide")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hey, what can I assist you with?"}]
    if "saved_conversations" not in st.session_state:
        st.session_state.saved_conversations = {}
    if "agent" not in st.session_state:
        st.session_state.agent = None

    # Sidebar: Saved Conversations
    with st.sidebar.expander("📁 Saved Conversations", expanded=True):
        if st.session_state.saved_conversations:
            for i, title in enumerate(st.session_state.saved_conversations.keys()):
                if st.button(title, key=f"conversation_{i}"):
                    st.session_state.messages = st.session_state.saved_conversations[title]
                    st.rerun()
        else:
            st.write("No saved conversations yet.")

    # New Chat Button
    st.sidebar.divider()
    if st.sidebar.button("➕ New Chat", key="new_chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Hey, what can I assist you with?"}]
        st.rerun()

    # File Uploader
    st.sidebar.divider()
    uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type="xlsx")
    if uploaded_file is not None and st.session_state.agent is None:
        st.session_state.agent = initialize_agent(uploaded_file)
        st.sidebar.success("File loaded successfully!")

    # Chat Interface
    st.title("🗂️ Excel Query Assistant")
    st.subheader("Chat with Your Data")

    # Display Chat Messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])

    # User Query Input
    user_query = st.chat_input("Type your question here...")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Process Query
        with st.spinner("Thinking..."):
            if st.session_state.agent:
                try:
                    response = query_data(st.session_state.agent, user_query)
                    agent_response = response['output']
                except Exception as e:
                    agent_response = f"Error processing your query: {str(e)}"
            else:
                agent_response = "Please upload a valid Excel file to start querying."

        # Add Assistant Response
        st.session_state.messages.append({"role": "assistant", "content": agent_response})
        st.rerun()

    # Plot Example Button
    if st.sidebar.button("📊 Generate Example Plot"):
        generate_plot()

    # Save Conversation
    st.sidebar.divider()
    save_title = st.sidebar.text_input("Save Conversation As:")
    if st.sidebar.button("💾 Save Conversation"):
        if save_title:
            save_conversation(save_title, st.session_state.messages)
            st.sidebar.success(f"Conversation saved as '{save_title}'!")
        else:
            st.sidebar.warning("Please provide a title to save the conversation.")

if __name__ == "__main__":
    main()