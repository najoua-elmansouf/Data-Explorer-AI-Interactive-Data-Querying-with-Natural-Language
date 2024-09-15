import pandas as pd

import streamlit as st

from sqlalchemy import create_engine

from langchain_community.utilities import SQLDatabase

from langchain_community.agent_toolkits import create_sql_agent

from langchain_community.chat_models import ChatOllama

from langchain.chains import create_sql_query_chain

from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import PromptTemplate

from langchain_core.runnables import RunnablePassthrough

from operator import itemgetter

 

# Fonction pour charger les données depuis un fichier (CSV ou Excel)

def load_data(file):

    if file.name.endswith('.csv'):

        return pd.read_csv(file)

    elif file.name.endswith('.xlsx'):

        return pd.read_excel(file, engine='openpyxl')

    else:

        raise ValueError("Unsupported file format. Only CSV and Excel (xlsx) are supported.")

 

# Configuration de la base de données SQLite

def setup_sqlite_database(engine):

    return SQLDatabase(engine=engine)

 

# Configuration du modèle de langage local (Mistral)

def setup_language_model():

    return ChatOllama(model='mistral')

 

# Fonction pour gérer l'entrée utilisateur et exécuter la requête

def handle_user_input(llm, db, user_question):

    # Crée la chaîne pour générer la requête SQL

    write_query = create_sql_query_chain(llm, db)

   

    # Outil pour exécuter la requête SQL

    execute_query = QuerySQLDataBaseTool(db=db)

 

    # Génère la requête SQL avec la question

    response = write_query.invoke({"question": user_question})

   

    sql_query = response.split("SQLQuery: ")[-1].strip().split("\n")[0]

    if sql_query.endswith("]"):

        sql_query = sql_query[:-1]

   

    # Exécuter la requête SQL extraite

    result = execute_query.invoke({"query": sql_query})

    #st.write("Query Result:", result)

    print("slllm", result)

    print("sllm2", result[0][0])

 

    # Formater la réponse pour l'utilisateur

    #count = result['result'][0][0]

 

    # Générer une réponse compréhensible en utilisant le modèle de langage

    answer_prompt = PromptTemplate.from_template(

        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

 

        Question: {question}

        SQL Query: {query}

        SQL Result: {result}

        Answer: """

    )

 

    # Combine the question, query, and result into a final answer

    context = {

        "question": user_question,

        "query": sql_query,

        "result": result,

    }

 

    answer = answer_prompt | llm | StrOutputParser()

    final_answer = answer.invoke(context)

    print("final", final_answer)

 

    return final_answer

 

# Interface utilisateur avec Streamlit

def main():

    st.set_page_config(page_title="Data Explorer AI", page_icon=":bar_chart:")

 

    st.title("Data Explorer AI :bar_chart:")

    st.write("Upload a CSV or Excel file to interact with your table.")

 

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

 

    if uploaded_file is not None:

        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}

        st.write(file_details)

 

        try:

            df = load_data(uploaded_file)

            st.write("Data loaded successfully!")

 

            # Sauvegarde des données dans la base de données SQLite

            db_path = "sqlite:///titanic_db.sqlite"

            engine = create_engine(db_path)

            df.to_sql("titanic", engine, index=False, if_exists='replace')

            db = setup_sqlite_database(engine)

 

            # Configuration du modèle de langage local

            llm = setup_language_model()

 

            # Interaction avec l'utilisateur

            user_question = st.text_input("Ask a question about the  dataset:")

            if user_question:

                response = handle_user_input(llm, db, user_question)

                st.write(response)

 

        except Exception as e:

            st.error(f"Error: {str(e)}")

 

if __name__ == '__main__':

    main()