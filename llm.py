import os
import asyncio
import re
import httpx

# Allow overriding via environment for easier deployments and testing
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))


def estimate_tokens(text: str) -> int:
  """Approximate token count using a simple word/punctuation split."""
  if not text:
    return 0
  return len(re.findall(r"\w+|[^\w\s]", text, re.UNICODE))

async def llm(prompt: str, model: str = OLLAMA_MODEL) -> str:
  max_retries = 3
  timeout = 180.0
  last_exc = None
  prompt_tokens = estimate_tokens(prompt)

  for attempt in range(1, max_retries + 1):
    try:
      print(
        f"[LLM] calling model={model} attempt={attempt}/{max_retries} "
        f"prompt_tokens={prompt_tokens} num_predict={OLLAMA_NUM_PREDICT}"
      )
      async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
          OLLAMA_URL,
          json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
              "num_predict": OLLAMA_NUM_PREDICT,
            },
          },
        )

      if response.status_code >= 400:
        raise RuntimeError(f"Ollama request failed ({response.status_code}): {response.text}")

      data = response.json()
      done_reason = data.get("done_reason", "unknown")
      prompt_eval_count = data.get("prompt_eval_count", "n/a")
      eval_count = data.get("eval_count", "n/a")
      print(
        "[LLM] response "
        f"done_reason={done_reason} prompt_eval_count={prompt_eval_count} "
        f"eval_count={eval_count}"
      )

      return data.get("response", "")

    except httpx.ConnectError as e:
      last_exc = e
      if attempt == max_retries:
        raise RuntimeError(
          f"Failed to connect to Ollama at {OLLAMA_URL} after {max_retries} attempts. "
          "Is the Ollama server running? Try `ollama serve` or check the URL/port." 
        ) from e
      await asyncio.sleep(2 ** attempt)

