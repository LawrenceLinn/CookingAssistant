from langchain.llms import HuggingFacePipeline
# from langchain_community.llms import HuggingFacePipeline
import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM
from transformers import AutoProcessor, LlavaForConditionalGeneration

def load_model():

    model = LlavaForConditionalGeneration.from_pretrained("llava-hf/llava-1.5-7b-hf")
    model.save_pretrained("./llm/")
    processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
    processor.save_pretrained("./llm/")


    return model, processor
    

def LangModel(llm, user_input):
    # use torch in mps
    output = llm.invoke(user_input)

    return output