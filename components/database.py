import os
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings

class OnboardingVectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.index_name = "bank-compliance-registry"
        # Completely free local embeddings running on your CPU
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        if self.index_name not in [index.name for index in self.pc.list_indexes()]:
            self.pc.create_index(
                name=self.index_name,
                dimension=384, 
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

    def seed_regulatory_knowledge(self, filepath: str):
        if not os.path.exists(filepath):
            return
        
        with open(filepath, "r") as f:
            content = f.read()
        
        chunks = [c.strip() for c in content.split("##") if c.strip()]
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self.embeddings.embed_query(chunk)
            vectors.append({
                "id": f"reg-rule-{i}",
                "values": embedding,
                "metadata": {"text": chunk, "category": "regulatory_mandate"}
            })
        
        self.index.upsert(vectors=vectors)

    def query_compliance_rules(self, query_text: str, top_k: int = 2) -> str:
        query_vector = self.embeddings.embed_query(query_text)
        results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        
        matched_contexts = [match["metadata"]["text"] for match in results["matches"] if "metadata" in match]
        return "\n\n---\n\n".join(matched_contexts)