from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, ItemCatalog, User

engine = create_engine('sqlite:///itemcatalogwithloginusers.db')

Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)


session = DBSession()

# Create a dummy user
User1 = User(name="Jame Wilson", email="james@example.com",
             picture='/pictures/user_bg.jpg')
session.add(User1)
session.commit()

catalog1 = Catalog(user_id=1, name="Soccer")
session.add(catalog1)
session.commit()

# Item catalog description
itemCatalog1 = ItemCatalog(user_id=1, name='goalkeeper gloves',
                           description='it allows goalkeeper use gloves to \
                           catch the ball', catalog=catalog1)
session.add(itemCatalog1)
session.commit()

catalog2 = Catalog(user_id=1, name="Basketball")
session.add(catalog2)
session.commit()

itemCatalog2 = ItemCatalog(user_id=1, name="Silverback",
                           description="Ultimate strength and stability with \
                           Stabili-Frame steel-on-steel connection between \
                            steel chassis and main pole",
                           catalog=catalog2)
session.add(itemCatalog2)
session.commit()



catalog3 = Catalog(user_id=1, name="Baseball")
session.add(catalog3)
session.commit()

itemCatalog3 = ItemCatalog(user_id=1, name="Crown Mark Baseball Glove \
                            Chair/Ottoman",
                           description="This baseball glove chair \
                            and baseball \
                            ottoman are the perfect accent for any child's \
                            room. Comfortably padded throughout, the faux \
                             leather upholstery provides good looks \
                              and durability.",
                           catalog=catalog3)
session.add(itemCatalog3)
session.commit()

#####
catalog4 = Catalog(user_id=1, name="Frisbee")
session.add(catalog4)
session.commit()

itemCatalog4 = ItemCatalog(user_id=1, name="Activ Life Best Kid's \
                            Flying Rings",
                           description="When it comes to most flying discs,\
                              Normal flying discs weigh 6.2 ounces,\
                               which means if you catch them the \
                               you may find yourself with \
                               a nasty bruise, a jammed finger \
                               or a crying child",
                           catalog=catalog4)
session.add(itemCatalog4)
session.commit()


catalog5 = Catalog(user_id=1, name="Snowboarding")
session.add(catalog5)
session.commit()

itemCatalog5 = ItemCatalog(user_id=1, name="Funky Junque Confetti Knit\
                         Beanie - Thick Soft Warm Winter Hat ",
                           description="WHEN TO WEAR: A great outdoor beanie \
                         during the colder months, especially when\
                          its brutal outside. It will keep your head\
                           and ears warm during outdoor activities\
                            including a football game, ice skating, \
                            snowboarding, skiing, hiking, and \
                            walking the dog",
                           catalog=catalog5)
session.add(itemCatalog5)
session.commit()

catalog6 = Catalog(user_id=1, name="Rock Climbing")
session.add(catalog6)
session.commit()

itemCatalog6 = ItemCatalog(user_id=1, name="Design with Vinyl Design \
    258 Athletic Black Silhouette Of\
     Man Climbing Mountain Rock",
                           description="Decals are easily removed however \
                        they are not repositionable or reusable. \
                        Decals peel off of walls easily, typically \
                         without damaging the paint. However, \
                         different paint finishes or walls\
                          condition could require touch-ups\
                           after Decal is removed.",
                           catalog=catalog6)
session.add(itemCatalog6)
session.commit()


catalog7 = Catalog(user_id=1, name="Foosball")
session.add(catalog7)
session.commit()

itemCatalog7 = ItemCatalog(user_id=1, name="Foosball Coffee Game Wood 42\
 Table Tempered Glass Top Tabletop \
 Furniture Family Dark Brown",
                           description="This Barrington 42 inch foosball\
                            coffee table made from wood and designed as \
                            a elegant piece of furniture. With 3/8-inch\
                             thick heat treated tempered glass surface, \
                             it is safe for you with family to take \
                             a tea break and having excitement\
                              of foosball at the same time",
                           catalog=catalog7)
session.add(itemCatalog7)
session.commit()


catalog8 = Catalog(user_id=1, name='Skating')
session.add(catalog8)
session.commit()

itemCatalog8 = ItemCatalog(user_id=1, name="Ice Skating 3D Night Light \
    Ice Skates 3D Led Optical Illusion 7 Colors\
     Change Night Light Touch Button Creative\
      Design Decorative Lighting Effect Lamp",
                           description="VERSATILE: soft LED light,fatigue \
                           free,fun addition to KIDS/NURSERY ROOM;\
                           creative ICE SKATE SHAPE with distinctive colors,\
                            perfect for HOME/FESTIVAL",
                           catalog=catalog8)
session.add(itemCatalog8)
session.commit()


catalog9 = Catalog(user_id=1, name="Hockey")
session.add(catalog9)
session.commit()

itemCatalog9 = ItemCatalog(user_id=1, name="Franklin Sports Indoor Goal Set - \
    Includes 2 Adjustable Hockey Sticks, \
    2 Foam Hockey Balls, 1 Street Hockey Ball,\
     and 1 Mini Soccer Ball",
                           description="Franklin sports 3 in 1 indoor sports \
                           set lets you choose your game; hockey, \
                           soccer or knee hockey. Set includes 2 \
                           insta-set goals, 2 adjustable hockey sticks, \
                           1 Mini soccer ball, 2 Mini foam hockey balls, \
                           1 hockey ball, inflation pump and needle.\
                            Easily sets up in seconds for hours of play.\
                             Fun for ages 6 and up",
                           catalog=catalog9)
session.add(itemCatalog9)
session.commit()

print("Completing insert testing database data")
