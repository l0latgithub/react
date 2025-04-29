from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import asyncio
import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RAGDatabase:
    async def get_relevant_schema(self, question: str) -> str:
        """Retrieve relevant database schema for the question"""
        logger.info(f"Retrieving schema for question: {question}")
        await asyncio.sleep(0.5)  # Simulate network delay
        return """CREATE TABLE users (id INT, name TEXT, email TEXT);
CREATE TABLE orders (id INT, user_id INT, amount FLOAT);"""

    async def get_similar_questions(self, question: str) -> list:
        """Retrieve similar question/SQL pairs"""
        logger.info(f"Finding similar questions to: {question}")
        await asyncio.sleep(0.5)  # Simulate network delay
        return [
            {"question": "Get all users", "sql": "SELECT * FROM users;"},
            {"question": "Count orders", "sql": "SELECT COUNT(*) FROM orders;"}
        ]

class LLMService:
    def __init__(self):
        self.timeout = 30.0
        # In production, you'd initialize your LLM API connection here

    async def generate_sql(self, prompt: str) -> str:
        """Call LLM endpoint to generate SQL"""
        logger.info("Generating SQL from prompt...")
        await asyncio.sleep(2)  # Simulate LLM processing time
        # In production, you'd make actual API call here:
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(LLM_ENDPOINT, json={"prompt": prompt}) as resp:
        #         return await resp.json()
        return "SELECT * FROM users WHERE name LIKE '%John%';"

class DatabaseConnection:
    async def execute_query(self, sql: str) -> list:
        """Execute SQL query against database"""
        logger.info(f"Executing SQL: {sql}")
        await asyncio.sleep(1)  # Simulate query execution time
        # In production, you'd use a real database connector here
        return [{"id": 1, "name": "John Doe", "email": "john@example.com"}]

class Text2SQLProcessor:
    def __init__(self):
        self.rag = RAGDatabase()
        self.llm = LLMService()
        self.db = DatabaseConnection()

    async def process_question(self, question: str) -> dict:
        """Execute the full text2sql pipeline in proper sequence"""
        # 1. First get RAG results (must complete first)
        schema = await self.rag.get_relevant_schema(question)
        examples = await self.rag.get_similar_questions(question)
        
        # 2. Then generate SQL (depends on RAG results)
        prompt = self._build_prompt(schema, examples, question)
        sql = await self.llm.generate_sql(prompt)
        
        # 3. Finally execute query (depends on SQL generation)
        results = await self.db.execute_query(sql)
        
        return {
            "schema": schema,
            "examples": examples,
            "sql": sql,
            "results": results
        }

    def _build_prompt(self, schema: str, examples: list, question: str) -> str:
        """Build the LLM prompt (synchronous operation)"""
        example_text = "\n".join(
            f"Q: {ex['question']}\nSQL: {ex['sql']}" 
            for ex in examples
        )
        return f"""Database Schema:
{schema}

Example Questions:
{example_text}

New Question: {question}
Generate SQL query for this question:"""

# Initialize processor
processor = Text2SQLProcessor()

# HTML for the test client
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Text2SQL Test Client</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat {
            height: 400px;
            border: 1px solid #ddd;
            padding: 10px;
            overflow-y: scroll;
            margin-bottom: 10px;
            background-color: #f9f9f9;
        }
        #question {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
        }
        button {
            padding: 8px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:disabled {
            background-color: #cccccc;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }
        .user {
            background-color: #e3f2fd;
            text-align: right;
        }
        .system {
            background-color: #f1f1f1;
        }
        .progress {
            background-color: #fff9c4;
        }
        .sql {
            background-color: #e8f5e9;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .error {
            background-color: #ffebee;
            color: #d32f2f;
        }
        #progress-bar {
            width: 100%;
            background-color: #e0e0e0;
            margin-bottom: 10px;
        }
        #progress {
            height: 20px;
            background-color: #4CAF50;
            width: 0%;
            text-align: center;
            line-height: 20px;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Text2SQL Test Client</h1>
    <div id="chat"></div>
    <div id="progress-bar"><div id="progress">0%</div></div>
    <input type="text" id="question" placeholder="Enter your question (e.g., 'Get all users named John')">
    <button id="send" onclick="sendQuestion()">Send</button>
    
    <script>
        const chat = document.getElementById('chat');
        const questionInput = document.getElementById('question');
        const sendButton = document.getElementById('send');
        const progressBar = document.getElementById('progress');
        
        // Connect to WebSocket
        const socket = new WebSocket(`ws://${window.location.host}/ws/text2sql`);
        
        socket.onopen = () => {
            addMessage('system', 'Connected to Text2SQL service');
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                addMessage('error', data.error);
                return;
            }
            
            if (data.status === 'processing') {
                addMessage('system', data.message);
                return;
            }
            
            if (data.stage) {
                let message = data.message;
                if (data.sql) {
                    message += `<div class="sql">${data.sql}</div>`;
                }
                
                addMessage('progress', message);
                
                if (data.progress) {
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.textContent = `${data.progress}%`;
                }
                
                if (data.stage === 'complete') {
                    addMessage('system', 'Query executed successfully');
                    addMessage('sql', `SQL: ${data.sql}`);
                    addMessage('results', `Results: ${JSON.stringify(data.results, null, 2)}`);
                    sendButton.disabled = false;
                }
            }
        };
        
        socket.onclose = () => {
            addMessage('system', 'Disconnected from Text2SQL service');
        };
        
        function addMessage(type, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = content;
            chat.appendChild(messageDiv);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function sendQuestion() {
            const question = questionInput.value.trim();
            if (!question) {
                alert('Please enter a question');
                return;
            }
            
            addMessage('user', question);
            socket.send(JSON.stringify({question: question}));
            questionInput.value = '';
            sendButton.disabled = true;
            
            // Reset progress
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        }
        
        // Allow pressing Enter to send
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendQuestion();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# WebSocket endpoint
@app.websocket("/ws/text2sql")
async def websocket_text2sql(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive user question
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                question = payload.get("question")
                if not question:
                    await websocket.send_text(json.dumps({
                        "error": "No question provided"
                    }))
                    continue
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON payload"
                }))
                continue
            
            # Process through pipeline with proper sequencing
            try:
                # Stage 1: RAG Retrieval
                await websocket.send_text(json.dumps({
                    "stage": "rag_retrieval",
                    "message": "Retrieving relevant schema and examples...",
                    "progress": 20
                }))
                
                # Stage 2: SQL Generation
                await websocket.send_text(json.dumps({
                    "stage": "sql_generation",
                    "message": "Generating SQL query...",
                    "progress": 50
                }))
                
                # Stage 3: Query Execution
                await websocket.send_text(json.dumps({
                    "stage": "query_execution",
                    "message": "Executing generated SQL...",
                    "progress": 80
                }))
                
                # Get final results
                result = await processor.process_question(question)
                
                # Send completion
                await websocket.send_text(json.dumps({
                    "stage": "complete",
                    "message": "Query executed successfully",
                    "progress": 100,
                    "sql": result["sql"],
                    "results": result["results"],
                    "schema": result["schema"],
                    "examples": result["examples"]
                }))
                
            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "stage": "failed"
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)