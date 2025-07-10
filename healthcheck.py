import weaviate

client = weaviate.connect_to_local()


def check_for_connection():
	print("Checking if client can connect...")
	try:
		print(client.is_ready())
	except Exception as err:
		print(f"Error could not connect to client:... {err}")


def check_for_collection():
	print("Checking if client can find 'verd' collection...")
	try:
		print(client.collections.get("verd"))
		#probably print some smaller part of this get (overwhelms cli)
	except Exception as err:
		print(f"Error could not get collection 'verd':... {err}")


def get_collection_data(collection_name):
	collection = client.collections.get(collection_name)
	for item in collection.iterator():
	    print(item.uuid, item.properties)


def check_for_data_length(collection_name):
	collection = client.collections.get(collection_name)
	count = 0
	for item in collection.iterator():
		count += 1
	print(f'{count} total items in dataset for: {collection_name}')


if __name__ == "__main__":
	try:
		# Uncomment tests you want to run
		# check_for_connection()
		# check_for_collection()
		# get_collection_data("verd") #replace with name of collection in your project
		# check_for_data_length("verd")
		#test_data_upload()
		#test_specific_data_retrieval()
		#test_data_delete()
		#etc.
		#test_ollama_query()
	finally:
		client.close()
