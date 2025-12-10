from agents import Agent


def manager_agent(model, scheduler, canceller, rescheduler, updater):
    return Agent(
        name="Manager Agent",
        instructions="""
        You are the central router.
        - If user mentions 'schedule', 'book', or 'set up a meeting' → handoff to scheduler agent.
        - If user mentions 'cancel', 'delete' → handoff to canceller agent.
        - If user mentions 'reschedule', 'move', 'change time' → handoff to rescheduler agent.
        - If user mentions 'update', 'modify', 'change details' → handoff to updater agent.
        - Otherwise, politely inform the user that you can only assist with meeting management tasks
        """,
        handoffs=[
            canceller,
            rescheduler,
            updater,
            scheduler
        ],
        model=model
    )
   
