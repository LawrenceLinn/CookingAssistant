# from langchain.llms import HuggingFacePipeline
# from langchain_community.llms import HuggingFacePipeline
import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM
from transformers import AutoProcessor, LlavaForConditionalGeneration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama

def load_model():
    model = Ollama(model="llama2",base_url="http://ollama:11434")
    return model
    

def LangModel(llm, user_input):

    output = llm.invoke(user_input)

    return output