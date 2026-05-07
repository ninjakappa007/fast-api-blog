

- Execution command : fastapi dev (this supports auto reload)
- Execution command : fastapi run (this does not support auto reload)
- Api docs using swagger api : http://localhost:8000/docs
-



# Self notes
### Data flow
1. User makes API call
2. Request received by asgi service(uvicorn)
3. Pydantic validates the data
4. SQLAlcemy stores / retrives the data from DB
5. Pydantic format the data before sending to user
6. asgi workers send response to user