#Viraj Dissanayake
#CS50 Project1
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    count = 0
    for isbn, title, author, year in reader:
        #author table
        if db.execute("SELECT id FROM author WHERE name = :author", {"author": author}).rowcount == 0:
            db.execute("INSERT INTO author (name) VALUES (:author)",  {"author": author})
            db.commit()
        author = db.execute("SELECT id FROM author WHERE name = :author", {"author": author}).fetchone()
        #year table
        if db.execute("SELECT id FROM year WHERE year = :year", {"year": year}).rowcount == 0:
            db.execute("INSERT INTO year (year) VALUES (:year)",  {"year": year})
            db.commit()
        year = db.execute("SELECT id FROM year WHERE year = :year", {"year": year}).fetchone()
        #books table
        db.execute("INSERT INTO books (isbn, title, author_id, year_id) VALUES (:isbn, :name, :author_id, :year_id)",
                  {"isbn": isbn, "name": title, "author_id": author.id, "year_id": year.id })
        print(count)
        count += 1
        db.commit()

if __name__ == "__main__":
    main()
