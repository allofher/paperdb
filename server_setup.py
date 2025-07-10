import weaviate
from weaviate.classes.config import Configure

client = weaviate.connect_to_local()

def create_collection():
	client.collections.create(
		name="verd",
		vectorizer_config=Configure.Vectorizer.text2vec_ollama(
        	api_endpoint="http://host.docker.internal:11434", 
        	model="bge-m3",
    	),
    	generative_config=Configure.Generative.ollama(
        	api_endpoint="http://host.docker.internal:11434",
        	model="llama3.2",
    	)
	)

	return "created collection 'verd' on server"


def client_ready():
	return client.is_ready()


if __name__ == '__main__':
	try:
		print("Checking Client Connection...")
		print(client_ready())
		print("Creating Collection...")
		print(create_collection())
		print("Server setup complete. Goodbye.")

	finally:
		client.close()  