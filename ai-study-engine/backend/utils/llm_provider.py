from backend.config import settings

def get_llm():
    if settings.OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
    else:
        from transformers import pipeline
        from langchain.llms.base import LLM
        from typing import Any, Optional, List

        class SimpleLocalLLM(LLM):
            pipeline: Any
            
            def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> str:
                # Call pipeline text2text without passing problematic kwargs like return_full_text
                outputs = self.pipeline(prompt)
                return outputs[0]['generated_text']
                
            @property
            def _llm_type(self) -> str:
                return "simple_local_llm"
                
        pipe = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base", 
            max_new_tokens=512,
            model_kwargs={"temperature": 0.0}
        )
        return SimpleLocalLLM(pipeline=pipe)
