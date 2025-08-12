# Tobi's Restaurant - Local LLM API

A self-hosted AI restaurant ordering system using the Phi-2 language model with Docker.
What I wanted to accomplish with this project is to understand how to host an LLM locally and share it with others. I started by downloading an LLM and training data from HuggingFace and hosted it on my computer. I containerized it in Docker for easy setup. I found that it took a long time to get everything started, so I created a custom PowerShell script to start up the program, and this created a quick, repeatable way to start using the app. Another reason for hosting this app locally is that I wanted to avoid having to pay fees to run my project. All of the services I ended up using had free tiers, and this allows me to iterate indefinitely.

##Novelty
I had no idea what to expect with the answers that Tobi would give, and the results were better than what I could have asked for. I found that a lot of hilarious scenarios would start to appear when talking with Tobi. For example: After placing my order, he would start to role-play using the character description I gave him. He would take a sip of my beer or get defensive when I said I didn't want to take surfing lessons with him after dinner.

Overall, this project was an absolute blast and taught me the basics of containerization in Docker, self-hosting, and simple AI implementation
## Features

- **Tobi the Surfer AI**: Chill surfer dude personality
- **The Common House Menu**: 20 curated restaurant items
- **Magic Password**: "I'm on Yelp" for VIP treatment
- **One-Click Startup**: Automated PowerShell script

## Dependencies

- Docker Desktop
- Python 3.10
- FastAPI + uvicorn + CORS
- llama-cpp-python
- Phi-2 model (Q4_K_M quantization)
- SQLite for order storage

## Project Architecture

```mermaid
graph TB
    subgraph "Users"
        U1["Family Member<br/>Phone/Computer"]
        U2["Local User<br/>Your Computer"]
    end
    
    subgraph "Frontend Layer"
        HTML1["restaurant_chat.html<br/>Local Version<br/>API: localhost:8000"]
        HTML2["restaurant_chat_public.html<br/>Public Version<br/>API: ngrok URL"]
    end
    
    subgraph "Network & Sharing"
        NGROK["ngrok Tunnel<br/>Public URL:<br/>https://abc123.ngrok.io<br/>-> localhost:8000"]
        GH["GitHub Repository<br/>Erics-First-LLM<br/>Code & Documentation"]
    end
    
    subgraph "Docker Environment"
        CONTAINER["Tobi Container<br/>Name: tobi-api<br/>Port: 8000<br/>Image: tobi-restaurant"]
    end
    
    subgraph "Application Layer"
        API["FastAPI Server<br/>server.py<br/>Endpoints:<br/>GET /<br/>GET /menu<br/>POST /chat<br/>POST /order"]
        AI["Phi-2 AI Model<br/>phi-2.Q4_K_M.gguf<br/>2.7B Parameters<br/>Local LLM Processing"]
        DB["SQLite Database<br/>orders.db<br/>Presidential Order Numbers<br/>Order History"]
    end
    
    subgraph "Data & Configuration"
        MENU["Menu Data<br/>The Common House<br/>20 Items:<br/>Starters (5)<br/>Mains (10)<br/>Desserts (3)<br/>Drinks (5)"]
        PRES["Presidential Years<br/>Order Numbers:<br/>1732 (Washington)<br/>1735 (Adams)<br/>1743 (Jefferson)"]
        DOCKER_FILE["Dockerfile<br/>Python 3.10<br/>FastAPI Dependencies<br/>CORS Configuration"]
        SCRIPT["start-tobi.ps1<br/>One-Click Startup<br/>Auto Build & Run<br/>Error Handling"]
    end
    
    subgraph "Tobi's Personality"
        CHAR["Surfer Dude AI<br/>North shore surfing<br/>Free surf lessons<br/>Chill responses<br/>Magic password: I'm on Yelp"]
    end
    
    U1 -.->|Opens HTML file| HTML2
    U2 -.->|Opens directly| HTML1
    
    HTML2 -->|API Calls| NGROK
    HTML1 -->|API Calls| CONTAINER
    NGROK -->|Forwards to| CONTAINER
    
    CONTAINER -->|Runs| API
    API -->|Uses| AI
    API -->|Stores orders| DB
    API -->|Serves| MENU
    API -->|Implements| CHAR
    
    DB -.->|References| PRES
    CONTAINER -.->|Built from| DOCKER_FILE
    CONTAINER -.->|Volume mount| AI
    
    HTML2 -.->|Hosted on| GH
    DOCKER_FILE -.->|Stored in| GH
    API -.->|Source in| GH
    SCRIPT -.->|Automation| GH
