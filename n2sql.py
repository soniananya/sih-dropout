
from populate import engine  # your SQLAlchemy engine

from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_huggingface import HuggingFaceEndpoint


# Setup database and LLM
db = SQLDatabase(engine)
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    temperature=0
)

# Create SQL toolkit and agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

def ask_agent(question: str):
    """Ask the AI agent a question about the database"""
    result = agent.invoke({"input": question})
    return result["output"]

if __name__ == "__main__":
    def test_agent():
        """Run some test queries on the database via the agent"""
        queries = [
            "List all the students in the database.",
            "Who are the students with grade A?",
            "What is the average age of all students?",
            "How many students are older than 20?",
            "Show the names of students who are younger than 21."
        ]

        for q in queries:
            print(f"Query: {q}")
            try:
                result = ask_agent(q)
                print("Result:", result)
            except Exception as e:
                print("Error:", e)
            print("-" * 50)


    # Run the test
    test_agent()
