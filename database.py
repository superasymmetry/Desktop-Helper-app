site_url = "https://docs.reach.cloud/reach-web-portal-guide/1.0-basic-information/" #test url
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

PINECONE_API_KEY = "pcsk_6nMG9i_EwaBCPpcHFA3fMFHUTspRVBuDv4KjMossNp8weDWzXZaHPqWpK6XGRxrTyDEKBJ"
# Import the Pinecone library
from pinecone import Pinecone

# Initialize a Pinecone client with your API key
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
