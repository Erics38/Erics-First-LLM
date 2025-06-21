from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama
import json
import sqlite3
import uuid

MODEL_PATH = "/app/models/phi-2.Q4_K_M.gguf"

llm = Llama(model_path=MODEL_PATH)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Presidential birth years for order numbers (first 20 presidents)
PRESIDENTIAL_YEARS = [
    1732, 1735, 1743, 1751, 1758, 1767, 1767, 1782, 1773, 1784,
    1795, 1784, 1800, 1804, 1808, 1809, 1822, 1818, 1831, 1881
]

# The Common House Menu Data
MENU_DATA = {
    "restaurant_name": "The Common House",
    "starters": [
        {"name": "Truffle Fries", "description": "Parmesan, rosemary, truffle oil", "price": 12.00},
        {"name": "Spicy Tuna Tartare", "description": "Ahi tuna, avocado, sesame-soy dressing", "price": 16.00},
        {"name": "Crispy Brussels", "description": "Balsamic glaze, chili flakes, lemon zest", "price": 11.00},
        {"name": "Burrata & Tomato", "description": "Heirloom tomato, basil oil, sea salt", "price": 14.00},
        {"name": "Smoked Chicken Flatbread", "description": "Arugula, goat cheese, roasted red pepper", "price": 13.00}
    ],
    "mains": [
        {"name": "Seared Salmon Bowl", "description": "Brown rice, avocado, miso vinaigrette", "price": 24.00},
        {"name": "Short Rib Pappardelle", "description": "Red wine braise, parmesan, gremolata", "price": 26.00},
        {"name": "Buttermilk Fried Chicken Sandwich", "description": "Pickles, garlic aioli, brioche bun", "price": 18.00},
        {"name": "Miso Glazed Cod", "description": "Snap peas, jasmine rice, sesame", "price": 28.00},
        {"name": "Steak Frites", "description": "8 oz sirloin, chimichurri, hand-cut fries", "price": 32.00},
        {"name": "House Smash Burger", "description": "Double patty, cheddar, caramelized onion", "price": 16.00},
        {"name": "Roasted Mushroom Risotto", "description": "Truffle oil, parmesan, thyme", "price": 22.00},
        {"name": "Grilled Chicken Cobb", "description": "Bacon, egg, blue cheese, avocado ranch", "price": 19.00},
        {"name": "Lobster Mac & Cheese", "description": "Cavatappi, gruyère, breadcrumbs", "price": 29.00},
        {"name": "Spaghetti Pomodoro", "description": "San Marzano tomato, basil, pecorino", "price": 17.00}
    ],
    "desserts": [
        {"name": "Warm Chocolate Torte", "description": "Sea salt, vanilla cream", "price": 9.00},
        {"name": "Olive Oil Cake", "description": "Lemon glaze, whipped mascarpone", "price": 8.00},
        {"name": "Salted Caramel Pudding", "description": "Toasted pecans, chantilly", "price": 7.00}
    ],
    "drinks": [
        {"name": "Old Fashioned", "description": "Bourbon, bitters, sugar, orange peel", "price": 12.00},
        {"name": "Espresso Martini", "description": "Vodka, espresso, coffee liqueur", "price": 14.00},
        {"name": "Negroni", "description": "Gin, Campari, sweet vermouth", "price": 13.00},
        {"name": "Margarita", "description": "Tequila, lime, orange liqueur", "price": 11.00},
        {"name": "Whiskey Sour", "description": "Bourbon, lemon, egg white", "price": 12.00}
    ]
}

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('/app/orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_number INTEGER UNIQUE,
            session_id TEXT,
            items TEXT,
            total REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_next_order_number():
    conn = sqlite3.connect('/app/orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM orders')
    count = cursor.fetchone()[0]
    conn.close()
    
    if count < len(PRESIDENTIAL_YEARS):
        return PRESIDENTIAL_YEARS[count]
    else:
        return PRESIDENTIAL_YEARS[count % len(PRESIDENTIAL_YEARS)]

@app.get("/")
def root():
    return {"status": "The Common House AI Assistant is running", "restaurant": "The Common House"}

@app.get("/menu")
def get_menu():
    return MENU_DATA

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt") or data.get("message", "")
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        if not prompt:
            return {"error": "No prompt or message provided"}
        
        # Check for magic password
        has_magic_password = "i'm on yelp" in prompt.lower()
        magic_note = " VIP Customer!" if has_magic_password else ""
        
        # Simple prompt to avoid context issues
       	simple_prompt = f"You are Tobi, a chill surfer who works at The Common House restaurant. Respond to this customer message in one short response only. Use casual surfer language.{magic_note}\n\nCustomer: {prompt}\nTobi:"

        output = llm(simple_prompt, max_tokens=50, temperature=0.5)
        ai_response = output["choices"][0]["text"].strip()
        
        return {
            "response": ai_response,
            "session_id": session_id,
            "has_magic_password": has_magic_password,
            "restaurant": "The Common House"
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/order")
async def create_order(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id", str(uuid.uuid4()))
        items = data.get("items", [])
        
        if not items:
            return {"error": "No items provided"}
        
        total = sum(float(item.get('price', 0)) for item in items)
        order_number = get_next_order_number()
        
        conn = sqlite3.connect('/app/orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (order_number, session_id, items, total, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_number, session_id, json.dumps(items), total, 'confirmed'))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "order_number": order_number,
            "items": items,
            "total": total,
            "message": f"Order #{order_number} confirmed! Your food will be ready shortly."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/order/{order_number}")
def get_order(order_number: int):
    try:
        conn = sqlite3.connect('/app/orders.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            return {"error": "Order not found"}
        
        return {
            "order_number": order[1],
            "items": json.loads(order[3]),
            "total": order[4],
            "status": order[5],
            "created_at": order[6]
        }
    except Exception as e:
        return {"error": f"Error retrieving order: {str(e)}"}