# LLM api keys
export MISTRAL_API_KEY=$(keyring get cybrid mistralapi)
export OPENAI_API_KEY=$(keyring get cybrid openaiapi)
# Tool api keys
export TAVILY_API_KEY=$(keyring get cybrid tavilyapi)
# LangSmith env vars
export LANGCHAIN_TRACING_V2=false
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY=$(keyring get cybrid langchainapi)
export LANGCHAIN_PROJECT="lg-agent-k8s"

