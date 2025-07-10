import weaviate
import requests
import json
import os
import time
import re
from google import genai
from google.genai import types
from weaviate.config import ConnectionConfig, AdditionalConfig, Timeout

weaviate_client = weaviate.connect_to_local(
	additional_config=AdditionalConfig(
		timeout=Timeout(query=1200000)
	)
)

gemini_client = genai.Client(api_key="")
new_notes_path = "/Users/liz/projects/verdbot/new_notes/"
backups_path = "/Users/liz/projects/verdbot/notes_backups/"


#TODO: decide on thinking budget
def call_gemini_with_file(image_bytes, mime_type):
	response = gemini_client.models.generate_content(
				model="gemini-2.5-flash",
				contents=[
					types.Part.from_bytes(
						data=image_bytes,
						mime_type=mime_type,
					),
					"""
					Hey buddy!, could you please do a few things for me?: (1) transcribe the text in this image into plain text; (2) summarize the text in 10 words or less; (3) categorize the text based on topic (Eg. HEALTH; SCIENCE; FITNESS; MEDIA; etc.) If you could respond in the following format that would be especially helpful.\n
					{
						Content_Summary: the summary of the content\n
						Content_Categories: CATEGORY,CATEGORY,CATEGORY\n
						Content_Transcription: the plain text transcription of the image
					}
					"""
				]
				# config=types.GenerateContentConfig(
			    #     thinking_config=types.ThinkingConfig(thinking_budget=0)
			    # ), 
			)
	return response


def transcribe_notes(path):
	memory_notes = []
	directory = os.fsencode(path)
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.endswith(".jpg"):
			print(f'Processing {filename}')
			filewithpath = path + filename
			with open(filewithpath, 'rb') as image:
				image_bytes = image.read()
			gemini_response = call_gemini_with_file(image_bytes, 'image/jpeg')
			memory_notes.append(gemini_response.text)
			time.sleep(1)
		elif filename.endswith(".HEIC"):
			print(f'Processing {filename}')
			filewithpath = path + filename
			with open(filewithpath, 'rb') as image:
				image_bytes = image.read()
			gemini_response = call_gemini_with_file(image_bytes, 'image/heif')
			memory_notes.append(gemini_response.text)
			time.sleep(1)
		else:
			print(f'skipping {filename}')
	return memory_notes


def backup_notes(notes, path):
	directory = os.fsencode(path)
	backup_index = len(os.listdir(directory))
	print(f'Found {backup_index} current notes backups. Adding {len(notes)} new backups.')
	for note in notes:
		filepath = path + str(backup_index) + ".txt"
		with open(filepath, "w") as output:
			output.write(note) # this is the part to change
		backup_index = backup_index + 1
	print(f'Backups done. There are now {len(os.listdir(directory))} total backups.')


def add_notes_to_db(notes):
	verddb = weaviate_client.collections.get("verd")
	for note in notes:
		uuid = verddb.data.insert({
			'content_Summary': note['Content_Summary'],
			'content_Categories': note['Content_Categories'],
			'content_Transcription': note['Content_Transcription'],
		})
		print(f'added {uuid} to db')
	print("Finished adding new notes to db.")


def check_db_size():
	verddb = weaviate_client.collections.get("verd")
	count = 0
	for item in verddb.iterator():
		count = count + 1
	return count


def cleanup_new_notes_directory(path):
	directory = os.fsencode(path)
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		filewithpath = path + filename
		os.remove(filewithpath)


def prep_json_format(text):
	for character in text:
		if text[0] == "{":
			break
		else:
			text = text[1:]

	for attempt in range(20):
		try:
			jsonformatted = json.loads(text)
		except Exception as err:
			print(f'Hit error:... {err}')
			text = text[:-1]
			print(text)
		else:
			break

	return jsonformatted


def normalize_transcript(transcript):
	# This pattern replaces newlines with whitespace unless it's two newlines back to back
	normalized = re.sub(r'(?<!\n)\n(?!\n)', " ", transcript)
	return normalized


def formatnotes(list_of_notes):
	dictionary_notes = []
	for raw_note in list_of_notes:
		json_ready_note = prep_json_format(raw_note)
		normalized_transcript = normalize_transcript(json_ready_note["Content_Transcription"])
		json_ready_note["Content_Transcription"] = normalized_transcript
		dictionary_notes.append(json_ready_note)
	return dictionary_notes


def pull_from_backups(path):
	memory_notes = []
	directory = os.fsencode(path)
	count = 0
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.endswith(".txt"):
			print(f'Processing {filename}')
			filewithpath = path + filename
			with open(filewithpath, 'r') as backup:
				memory_notes.append(backup.read())
			count = count + 1
		if count >= 44 and count <= 47:
			print(filewithpath)
	print(f"loaded {len(memory_notes)} backups")
	return memory_notes


if __name__ == "__main__":
	try:
		print("_Ingesting New Notes into DB_\nFirst, transcribing notes...")
		memory_notes = transcribe_notes(new_notes_path)
		print(f"Found {len(memory_notes)} new notes.")
		print("Backing up notes...")
		backup_notes(memory_notes, backups_path)
		# memory_notes = pull_from_backups(backups_path)
		dbsize = check_db_size()
		print(f'Currently db has {dbsize} entries.')
		print(f'Formatting and preparing notes for DB entry.')
		formatted_notes = formatnotes(memory_notes)
		print("Beginning vectorization and adding new notes to DB.")
		add_notes_to_db(formatted_notes)
		dbsize = check_db_size()
		print(f"DB now has {dbsize} total entries.")
		print("Note ingestion complete. Cleaning up new notes directory...")
		cleanup_new_notes_directory(new_notes_path)
		print("All done. Goodbye.")
	finally:
		weaviate_client.close()
