## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Agent orchestration | LangGraph |
| AI model integration | Microsoft Azure AI |
| Structured data | SQL database |
| Knowledge retrieval | Retrieval-Augmented Generation (RAG) |
| External information | Weather API |
| User interface | Streamlit |
| Containerization | Docker |
| AI infrastructure | Microsoft Azure |
| CI/CD | GitHub Actions |

*The exact Azure services and model endpoints depend on the implementation.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or later, compatible with the project dependencies
- Git
- Access to the Azure AI model deployment used by the application
- Database credentials and a compatible fleet dataset
- Weather API credentials, if required
- Vector store dependencies, if used by the RAG pipeline

### Configure environment variables

Create a `.env` file containing the configuration required by your Azure model integration and other services.

Example template:

```dotenv
AZURE_AI_ENDPOINT=
AZURE_AI_API_KEY=
AZURE_AI_MODEL_DEPLOYMENT=
DATABASE_URL=
VECTOR_STORE_URL=
```

The variable names above are illustrative. Use the exact names expected by your implementation and the authentication method configured for your Azure service.

**Security:** Never commit API keys, credentials, or `.env` files to GitHub. Keep secrets in environment variables or an appropriate secrets-management service.

## ☁️ Azure Integration

Microsoft Azure provides the AI model infrastructure used by the application. The assistant integrates with the configured model deployment to interpret natural-language requests, coordinate tools, and generate responses grounded in available fleet data and retrieved documentation.

The LangGraph workflow manages the agent's execution, while the model integration supplies the language-model capabilities required for reasoning and response generation.

The exact Azure service, model, and deployment configuration should be documented according to the resources actually used in this project.

