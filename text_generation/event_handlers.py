from typing import Callable

import torch
from aiocache import Cache
from fastapi import FastAPI
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import model_settings


def _set_device(app: FastAPI) -> None:
    is_cuda_available = torch.cuda.is_available()
    logger.info(f"is cuda available : {is_cuda_available}")
    app.state.device = torch.device("cuda") if is_cuda_available else torch.device("cpu")


def _load_tokenizer(app: FastAPI) -> None:
    logger.info(f"load tokenizer from {model_settings.model_path}")
    app.state.tokenizer = AutoTokenizer.from_pretrained(
        model_settings.model_path, use_fast=model_settings.use_fast_tokenizer
    )


def _load_model(app: FastAPI) -> None:
    logger.info(f"load model from {model_settings.model_path}")
    device: torch.device = app.state.device
    if device.type == "cuda":
        app.state.model = AutoModelForCausalLM.from_pretrained(
            model_settings.model_path, low_cpu_mem_usage=True, torch_dtype=torch.float16
        ).to(device)
    else:
        app.state.model = AutoModelForCausalLM.from_pretrained(model_settings.model_path, low_cpu_mem_usage=True)


def _set_queue(app: FastAPI) -> None:
    app.state.cache = Cache(Cache.REDIS, endpoint="127.0.0.1", port=6379)


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        _set_device(app)
        _load_tokenizer(app)
        _load_model(app)
        _set_queue(app)

    return startup
