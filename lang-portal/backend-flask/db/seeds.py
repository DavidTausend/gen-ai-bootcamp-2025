from models import db, Word, WordGroup

def seed_data():
    # Add sample words
    word = Word(german='Hallo', english='Hello')
    word.set_parts({'part_of_speech': 'interjection'})
    db.session.add(word)
    db.session.commit()

    # Add sample word groups
    group1 = WordGroup(name='Basic Greetings')
    db.session.add(group1)

    db.session.commit()
