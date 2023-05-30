import psycopg2
import json

connection = psycopg2.connect(
		host='localhost',
		dbname='mydukaangpt',
		user='yug',
		password='2603',
		port=5432
	)

cursor = connection.cursor()


cursor.execute(
	"""
		CREATE EXTENSION vector;
		CREATE TABLE documents (
				id bigserial PRIMARY KEY,
				title text NOT NULL,
				url text NOT NULL,
				doc text NOT NULL,
				embedding vector(1536) NOT NULL
			);
	"""
	)

with open('./db.json') as f:
	data = json.load(f)

for vector in data['vectors']:
	title = vector['metadata']['title'].replace("'", "''")
	url = vector['metadata']['url'].replace("'", "''")
	doc = vector['metadata']['doc'].replace("'", "''")
	embedding = vector['values']

	cursor.execute(
		f"""
			INSERT INTO documents (title, url, doc, embedding) VALUES ('{title}', '{url}', '{doc}', '{embedding}');
		"""
		)

connection.commit()
cursor.close()
connection.close()