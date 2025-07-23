site_url = "https://docs.reach.cloud/reach-web-portal-guide/1.0-basic-information/"
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = WebBaseLoader(site_url)
doc = loader.load()
print("Original document length:", len(doc[0].page_content))

# Chunk the document into smaller pieces
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  
    chunk_overlap=100,  
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

records = text_splitter.split_documents(doc)
print(f"Document split into {len(records)} chunks")
print("First chunk:", records[0].page_content[:200] + "...")

from langchain_pinecone import PineconeEmbeddings
import os

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
from pinecone import Pinecone

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create a dense index with integrated embedding
index_name = "aiagent"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

index = pc.Index(index_name)

# Convert chunks to proper record format for Pinecone
pinecone_records = []
for i, chunk in enumerate(records):
    record = {
        "id": f"reach-docs-{i}",
        "text": chunk.page_content,  # This field matches the field_map "text" -> "chunk_text"
        "source": site_url,
        "chunk_index": i
    }
    pinecone_records.append(record)

try:
    index.upsert_records("reach-docs", pinecone_records)
except Exception as e:
    print(f"Error during upsert: {e}")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)
    index.upsert_records("reach-docs", pinecone_records)

print(f"Successfully upserted {len(pinecone_records)} records to Pinecone index '{index_name}'")
print("contents", pinecone_records[0])

def query_pinecone(query_text, top_k=3):
    try:
        results = index.query_records(
            namespace="reach-docs",
            query=query_text,
            top_k=top_k,
            include_metadata=True
        )
        return results.get('matches', [])
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return []


def call(client, query, img_base64, context_chunks, feature_list):
    context = "\n\n".join([chunk.get('metadata', {}).get('text', '') for chunk in context_chunks])
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an agent that controls a computer to complete tasks.\n"
                    "Your task is {query}. If you have already done the task, stop immediately.\n"
                    "Stop as soon as possible after the minimum number of steps.\n"
                    "To stop when the task is done, respond ONLY with {\"tool\": \"Done\", \"args\": {}}.\n"
                    "When not done, pick **one** tool for the next step and output ONLY the JSON object specified.\n"
                    "Important: If you want to type something, into a search bar for example, assume that the input for the search is not yet selected. This means you must click on it before typing. If you type and it doesn't work, it means you didn't select the input properly.\n"
                    "Tools are as follows:\n"
                    "- Click-Tool: Click at coordinates. Output in this format {{ \"tool\": \"Click-Tool\", \"args\": {{ \"element\": \"value\" }} }}\n\n"
                    "- Type-Tool: Type text on an element. Output: {{ \"tool\": \"Type-Tool\", \"args\": {{ \"text\": \"value\" }} }}\n\n"
                    "- Scroll-Tool: Scroll on the screen. {{ \"tool\": \"Scroll-Tool\", \"args\": {{ \"axis\": \"horizontal/vertical\", \"direction\": \"up/down\" }} }}\n\n"
                    "- Drag-Tool: Drag from one point to another. {{ \"tool\": \"Drag-Tool\", \"args\": {{ \"initial_element\": \"value\", \"final_position\": \"value\" }} }}\n\n"
                    "- Shortcut-Tool: Press keyboard shortcuts (e.g., Ctrl+C to copy, Ctrl+V to paste). {{ \"tool\": \"Shortcut-Tool\", \"args\": {{ \"keys\": [\"list of keys\"] }} }}\n\n"
                    "- Key-Tool: Press a single key. {{ \"tool\": \"Key-Tool\", \"args\": {{ \"key\": \"value\" }} }}\n\n"
                    "- Launch-Tool: Open an app. {{ \"tool\": \"Launch-Tool\", \"args\": {{ \"app\": \"value\" }} }}\n\n"
                    "- Query-Tool: Query Pinecone for relevant chunks. {{ \"tool\": \"Query-Tool\", \"args\": {{ \"query\": \"value\", \"top_k\": value }} }}\n\n"
                    "Only respond with one tool call, strictly in JSON format as specified.\n"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Your task is {query}. The actions you have taken so far are: {chat_history}.\n\n"
                            f"The list of elements on this laptop is here: {feature_list}.\n\n"
                            "Interpret the screenshot and features given. Try not to perform your last action again."
                            "Output the JSON object corresponding to the next step."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": img_base64}
                    }
                ]
            }
        ],
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    res = completion.choices[0].message
    action = json.loads(res.content)

    return action
