# Inventory Management

## Steps to Run  

1. Activate the virtual environment:  
   ```sh
   venv\Scripts\activate  # For Windows
   source venv/bin/activate  # For macOS/Linux
   ```
2. Install required packages:  
   ```sh
   pip install -r requirements.txt
   ```
3. Navigate to the project directory:  
   ```sh
   cd inventory
   ```
4. Run the application using different ports for different environments:  
   ```sh
   python manage.py runserver --settings=inventory.settings.development 8000
   python manage.py runserver --settings=inventory.settings.test 9000
   ```
5. Download and start Redis:  
   ```sh
   redis-server
   ```
6. Run the Celery worker:  
   ```sh
   celery -A inventory worker --loglevel=info --pool=solo -Q webhook_queue
   ```
7. Check registered Celery tasks:  
   ```sh
   celery -A inventory inspect registered
   ```

---

## API Endpoints  

### 1. Search Products  
- **URL:** `http://127.0.0.1:8000/api/products/search?page=1&limit=10`  
- **Method:** `POST`  
- **Body (JSON):**  
  ```json
  {
    "name": "",
    "min_price": "",
    "max_price": "",
    "available": "true",
    "active_last_30_days": "true"
  }
  ```

### 2. Webhook  
- **URL:** `http://127.0.0.1:8000/api/webhook`  
- **Method:** `POST`  
- **Body (JSON):**  
  ```json
  {
    "product_id": 1,
    "price": "1000"
  }
  ```

### 3. Email Masking  
- **URL:** `http://127.0.0.1:8000/api/UserDataView?page=1&limit=20`  
- **Method:** `GET`  

### 4. Product Update (Using Celery and Retry Logic)  
- **URL:** `http://127.0.0.1:8000/api/ProductUpdateView`  
- **Method:** `POST`  
- **Body (JSON):**  
  ```json
  {
    "product_id": 1,
    "price": "1000"
  }
