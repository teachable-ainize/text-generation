import asyncio

import torch
from aiocache import Cache
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from schemas.request import TextGenerationRequest
from schemas.response import TextGenerationResponse
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import app_settings


router = APIRouter()


@router.post("/generate", response_model=TextGenerationResponse)
async def post_generation(request: Request, data: TextGenerationRequest):
    tokenizer: AutoTokenizer = request.app.state.tokenizer
    model: AutoModelForCausalLM = request.app.state.model
    device: torch.device = request.app.state.device
    generation_paramters = data.generation_paramters
    cache: Cache = request.app.state.cache
    for _ in range(app_settings.app_max_retry):
        count = await cache.get("count", default=0)
        logger.info(f"Test {count}")
        if count < app_settings.app_max_queue_size:
            break
        await asyncio.sleep(1)
    else:
        raise HTTPException(505, "Server is too busy")
    inputs = {
        "inputs": tokenizer.encode(data.text, return_tensors="pt").to(device),
        "max_new_tokens": generation_paramters.max_new_tokens,
        "do_sample": generation_paramters.do_sample,
        "early_stopping": generation_paramters.early_stopping,
        "num_beams": generation_paramters.num_beams,
        "temperature": generation_paramters.temperature,
        "top_k": generation_paramters.top_k,
        "top_p": generation_paramters.top_p,
        "no_repeat_ngram_size": generation_paramters.no_repeat_ngram_size,
        "num_return_sequences": generation_paramters.num_return_sequences,
    }
    try:
        await cache.increment("count", 1)
        generated_ids = model.generate(**inputs)
    except ValueError as e:
        raise HTTPException(422, e)
    except Exception as e:
        raise HTTPException(500, e)
    finally:
        await cache.increment("count", -1)
        del inputs
    result = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return TextGenerationResponse(result=result)
