import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Importiere unsere selbst gebauten Werkzeuge!
from agent_tools import (
    read_pdf_document,
    highlight_pdf_text,
    check_inventory_db,
    update_inventory_db,
    delete_inventory_item,
    add_new_inventory_item
)

load_dotenv()

# 1. Das Basis-Modell initialisieren
llm = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.3-70b-versatile",
    temperature=0
)

# 2. Die Werkzeugkiste packen
tools = [
    read_pdf_document,
    highlight_pdf_text,
    check_inventory_db,
    update_inventory_db,
    delete_inventory_item,
    add_new_inventory_item
]

# 3. Den System-Prompt definieren
system_prompt = (
    "Du bist ein intelligenter KI-Assistent für Prozessoptimierung und Supply Chain Management. "
    "Du hast Zugriff auf verschiedene Werkzeuge, um PDFs zu lesen, zu markieren und eine SQL-Datenbank zu steuern. "
    "Entscheide völlig autonom, welches Werkzeug (oder welche Kombination) du benötigst, um die Aufgaben des Nutzers zu lösen. "
    "WICHTIG: Wenn eines deiner Werkzeuge einen Download-Link generiert (z. B. nach dem Markieren oder Übersetzen), "
    "MUSST du diesen Link zwingend und unverändert in deiner finalen Antwort an den Nutzer ausgeben! "
    "WICHTIG für die Datenbank: Füge NUR Produkte/Bauteile hinzu, die eindeutig einen Produktnamen, "
    "eine konkrete Stückzahl (integer > 0) und einen realen Preis (float > 0.0) haben. "
    "Zahlungsempfänger, Händlernamen oder Kontoauszugstexte sind KEINE Produkte und dürfen NICHT "
    "in die Datenbank eingefügt werden. Wenn du dir nicht sicher bist, frage lieber nach. "    
    "Wenn eines deiner Werkzeuge einen Download-Link generiert, MUSST du diesen Link zwingend "
    "und unverändert in deiner finalen Antwort ausgeben! "
    "Antworte immer professionell und auf Deutsch."
)
# 4. Den Agenten OHNE den fehleranfälligen Modifier bauen



memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory) 


def ask_ai(question: str, thread_id: str = "default"):  
    try:
        # config mit thread_id übergebe
        config = {"configurable": {"thread_id": thread_id}}

        response = agent_executor.invoke(
            {
                "messages": [
                    ("system", system_prompt),
                    ("user", question)
                ]
            },
            config=config  
        )
        return response["messages"][-1].content
    except Exception as e:
        return f"Fehler bei der Agenten-Ausführung: {str(e)}"