from langchain_community.document_loaders import GitbookLoader

url = "https://docs.nado.xyz/"
print(f"Loading from {url}...")
loader = GitbookLoader(url, load_all_paths=True)
documents = loader.load()

print(f"Found {len(documents)} documents.")
for doc in documents[:5]:
    print(f"Source: {doc.metadata.get('source')}")
