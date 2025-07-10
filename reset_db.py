import weaviate
from weaviate.classes.query import Filter

weaviate_client = weaviate.connect_to_local()


def delete_objects(collection_name):
	collection = weaviate_client.collections.get(collection_name)
	response = collection.query.fetch_objects(limit=100)
	ids = [o.uuid for o in response.objects]

	collection.data.delete_many(
	    where=Filter.by_id().contains_any(ids)
	)
	# dryrun = collection.data.delete_many(
	# 	where=Filter.by_id().contains_any(ids),
	# 	dry_run=True,
	# 	verbose=True
	# )	
	# print(f'Would delete {dry_run["results"]["matches"]} matches. Proceed?')


if __name__ == '__main__':
	try:
		delete_objects("verd") # change name of collection
	finally:
		weaviate_client.close()