# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Install only what the Frontend needs
# (Streamlit to show the UI, requests to talk to the API, pandas for tables)
RUN pip install streamlit requests pandas

# 4. Copy the frontend code (app.py) into the container
COPY . .

# 5. Expose the standard Streamlit port
EXPOSE 8501

# 6. Start Streamlit
# We set server.address to 0.0.0.0 so it is accessible outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

