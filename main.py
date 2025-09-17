from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import uuid
import html

app = FastAPI()

# In-memory storage for todos
todos = []

class Todo:
    def __init__(self, id: str, text: str, completed: bool = False):
        self.id = id
        self.text = text
        self.completed = completed

def generate_html():
    todo_items = ""
    if todos:
        for todo in todos:
            completed_style = "text-decoration: line-through;" if todo.completed else ""
            checked = "checked" if todo.completed else ""
            todo_items += f"""
                <div id="todo-{todo.id}" style="display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee;">
                    <input type="checkbox" {checked} onchange="toggleTodo('{todo.id}')" style="margin-right: 10px;">
                    <span style="{completed_style}">{html.escape(todo.text)}</span>
                    <button onclick="deleteTodo('{todo.id}')" style="margin-left: 10px; background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Delete</button>
                </div>
            """
    else:
        todo_items = '<div style="text-align: center; color: #999; padding: 40px; font-style: italic;">No todos yet. Add one above!</div>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todo App</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }}
            .add-todo {{
                display: flex;
                margin-bottom: 20px;
                gap: 10px;
            }}
            input[type="text"] {{
                flex: 1;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }}
            button {{
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{
                background: #0056b3;
            }}
            .todo-list {{
                border: 1px solid #ddd;
                border-radius: 4px;
                min-height: 200px;
            }}
        </style>
        <script>
            async function addTodo() {{
                const input = document.getElementById('todoInput');
                const text = input.value.trim();
                if (!text) return;

                const response = await fetch('/add', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: 'text=' + encodeURIComponent(text)
                }});

                if (response.ok) {{
                    input.value = '';
                    location.reload();
                }} else {{
                    const error = await response.json();
                    alert('Error: ' + (error.detail || 'Failed to add todo'));
                }}
            }}

            async function toggleTodo(id) {{
                try {{
                    const response = await fetch(`/toggle/${{id}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Error: ' + (error.detail || 'Failed to toggle todo'));
                    }}
                }} catch (e) {{
                    alert('Network error: ' + e.message);
                }}
            }}

            async function deleteTodo(id) {{
                try {{
                    const response = await fetch(`/delete/${{id}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Error: ' + (error.detail || 'Failed to delete todo'));
                    }}
                }} catch (e) {{
                    alert('Network error: ' + e.message);
                }}
            }}

            document.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter' && e.target.id === 'todoInput') {{
                    addTodo();
                }}
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Todo App</h1>
            <div class="add-todo">
                <input type="text" id="todoInput" placeholder="Enter a new todo...">
                <button onclick="addTodo()">Add</button>
            </div>
            <div id="todo-list" class="todo-list">
                {todo_items}
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return generate_html()

@app.post("/add")
async def add_todo(text: str = Form(...)):
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Todo text cannot be empty")
    if len(text.strip()) > 500:
        raise HTTPException(status_code=400, detail="Todo text too long (max 500 characters)")

    new_todo = Todo(id=str(uuid.uuid4()), text=text.strip())
    todos.append(new_todo)
    return {"status": "success"}

@app.post("/toggle/{todo_id}")
async def toggle_todo(todo_id: str):
    for todo in todos:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/delete/{todo_id}")
async def delete_todo(todo_id: str):
    global todos
    original_length = len(todos)
    todos = [todo for todo in todos if todo.id != todo_id]
    if len(todos) == original_length:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)