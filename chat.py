import weaviate
from weaviate.config import ConnectionConfig, AdditionalConfig, Timeout

weaviate_client = weaviate.connect_to_local(
    additional_config=AdditionalConfig(
        timeout=Timeout(query=120)
    )
)
verddb = weaviate_client.collections.get("Verd")

promptmode = "debug"
promptdict = {
    "ask": {
        "limit": 3,
        "alpha": 0.7,
        "llmprompt": "You're assisting the user with their work. If any of the notes below seem relevant to their question, use them to inform your response. Otherwise, answer based on your best reasoning. Be clear, helpful, and concise."
    },
    "duck": {
        "limit": 5,
        "alpha": 0.9,
        "llmprompt": "The user is thinking through a problem related to their work: tools, processes, teams, or project ideas. Review the notes below and point out anything that seems relevant or worth reconsidering. Highlight gaps, suggest next steps, or connect ideas. Be as specific as possible and reference what note or topic you're referring to."
    },
    "summ": {
        "limit": 7,
        "alpha": 0.6,
        "llmprompt": "Summarize what the user has learned about this topic based on the notes below. If you use information from a note, cite it clearly using its title or timestamp. Be concise but thorough, and focus only on what's actually in the notes."
    },
    "debug": {
        "limit": 1,
        "alpha": 0.5, # or should this be 0 or 1?
        "llmprompt": "Use the provided notes to answer the question as best you can." 
    }
}


while True:
    user_query = input("Ask a question (OR 'exit', 'ask', 'duck', 'summ'): ").strip()
    if user_query.lower() == "exit":
        weaviate_client.close()
        break
    elif user_query.lower() == "ask":
        promptmode = "ask"
        print("Swapping to ASK mode.")
    elif user_query.lower() == "duck":
        promptmode = "duck"
        print("Swapping to RUBBERDUCK mode.")
    elif user_query.lower() == "summ":
        promptmode = "summ"
        print("Swapping to SUMMARIZER mode.")
    else:
        try:
            response = verddb.generate.hybrid(
                query=user_query,
                limit=promptdict[promptmode]["limit"],
                alpha=promptdict[promptmode]["alpha"],
                grouped_task=promptdict[promptmode]["llmprompt"],
            )
            print("\nGenerated Answer:\n", response.generated)
            print("-" * 50)

        except Exception as e:
            print("Error during generation:", e)
            weaviate_client.close()
            break