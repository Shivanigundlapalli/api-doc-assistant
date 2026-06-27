from services.llm_service import generate_answer; print(''.join([c for c in generate_answer('how to auth', 'To auth you use an API key in header X-API-Key')]))
