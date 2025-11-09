from agents import Agent

def manager_agent(model, scheduler, canceller):
    return Agent(
        name="Manager Agent",
        instructions="""
        You are the central router.
        - If user mentions 'schedule', 'book', or 'set up a meeting' → handoff to scheduler agent.
        - If user mentions 'cancel', 'delete' → handoff to canceller agent.
        """,
        handoffs=[scheduler, canceller],
        model=model
    )
