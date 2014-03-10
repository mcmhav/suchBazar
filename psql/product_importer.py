import json
import psycopg2

def main():
  f = open('product_db.txt', 'r')
  conn = psycopg2.connect("dbname=sobazar user=sobazar")
  cur = conn.cursor()
  i = 1
  for line in f:
    d = json.loads(line)
    if not "redirectWebUrl" in d:
      print i
    i += 1
    cur.execute("""INSERT INTO products (id, brandId, brandName, title,
                   description, terms, imageUrl, oldPrice, newPrice, type, 
                   currency, redirectWebUrl) VALUES (%s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s)""",
                  (d["id"], d["brandId"], d["brandName"], d["title"], d["description"],
                  d["terms"], d["imageUrl"], d.get("oldPrice",0), d["newPrice"], d["type"],
                  d["currency"], d["redirectWebUrl"]))
  conn.commit()
  cur.close()
  conn.close()

if __name__ == '__main__':
  main()
