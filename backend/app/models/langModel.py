# from langchain.llms import HuggingFacePipeline
# from langchain_community.llms import HuggingFacePipeline
import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM
from transformers import AutoProcessor, LlavaForConditionalGeneration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
import ollama
from langchain_core.prompts import ChatPromptTemplate


def llava(image_b64):

    model = Ollama(model="llava:7b-v1.6",base_url="http://ollama:11434")
    modelwithimg = model.bind(images=[image_b64])
    prompt = "Identify all cooking ingredients visible in the provided image and list them."
    output = modelwithimg.invoke(prompt)
    return output

def load_model(llava_result):
    model = Ollama(model="llama2",base_url="http://ollama:11434")
    prompt = [("system", "You are a gourmet and chef, skilled in the preparation and techniques of various regional cuisines. Your role is to suggest dishes that I would most likely enjoy based on the ingredients and specific requirements I provide. You will offer complete recipes, list additional ingredients I need to purchase, and provide relevant cooking tips and precautions."),
          ("assistant", llava_result)]

    return model, prompt

def LangModel(llm, prompt, user_input):
    prompt.append(("user", user_input))
    output = llm.invoke(user_input)
    prompt.append(("assistant", output))
    return output, prompt

