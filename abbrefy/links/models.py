from uuid import uuid4
from abbrefy import mongo
from datetime import datetime
from abbrefy.links.tools import generate_slug, get_title
from flask import url_for, session
import pymongo
import os


class Link:

    # initializing the class
    def __init__(self, url=None, author=None, title=None):
        self.url = url
        self.author = author
        self.title = get_title(self.url)

    # slug retrieval helper function
    def get_origin(self, slug):
        if self.check_slug(slug):
            return self.check_slug(slug)['origin']
        return None

    # link object retrieval helper function
    def get_link(self, slug):
        link = self.check_slug(slug)
        if link:
            del link['_id']
            return link
        return None

    # slug validator helper function
    @staticmethod
    def check_slug(slug):
        data = mongo.db.links.find_one({"slug": slug})
        bulk = mongo.db.links.find_one({"origin": slug})
        link = data if data else bulk
        return link

    # slug validator helper function
    @staticmethod
    def delete(link):

        try:
            mongo.db.links.delete_one({"slug": link["slug"]})
        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            return response

        return {"status": True,
                "message": "Abbrefy link deletion successful"}

    # slug generator helper function
    def new_slug(self):
        slug = generate_slug()
        if self.check_slug(slug):
            self.new_slug()
        return slug

    # updating a link data
    @staticmethod
    def update_link(filter, new, update):

        try:
            # adding link object to db
            mongo.db.links.update_one(filter, update)
        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            return response

        response = {

            "status": True,
            "message": "Abbrefy link update successful.",
            "origin": new['origin'],
            "slug": new['slug'],
            "url": f"http://abbrefy.xyz/{new['slug']}",
            "title": new['title'],
            "clicks": new['clicks'],
            "stealth": new['stealth']
        }

        return response

    # abbrefy helper function
    def abbrefy(self):

        try:
            slug = self.new_slug()

            # creating the link object
            link = {
                "author": self.author,
                "public_id": uuid4().hex,
                "date_created": datetime.utcnow(),
                "origin": self.url,
                "slug": slug,
                "stealth": False,
                "clicks": 0,
                "audience": [],
                "title": self.title
            }

            # adding link object to db
            mongo.db.links.insert_one(link)
        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            return response

        response = {
            "status": True,
            "message": "URL abbrefy successful.",
            "origin": self.url,
            "url": f"http://abbrefy.xyz/{slug}",
            "title": self.title,
            "dateCreated": link['date_created'].strftime('%b %d, %Y, %I:%M %p'),
            "dateCreated2": link['date_created'].strftime("%b %d, %Y"),
            "slug": slug,
            "stealth": False,
            "audience": [],
            "clicks": 0
        }

        return response

    # abbrefy helper function
    def bulk_abbrefy(self, location, origin):

        MONGO_URI = os.environ.get("MONGO_URI", "")

        client = pymongo.MongoClient(MONGO_URI)
        db = client.abbrefy

        # try:

        # creating the link object
        link = {
            "author": self.author,
            "public_id": uuid4().hex,
            "date_created": datetime.utcnow(),
            "origin": origin,
            "slug": location,
            "stealth": False,
            "clicks": 0,
            "audience": [],
            "title": 'Bulk URL Abbrefy | Download Links Below',
            "type": "bulk"
        }

        # adding link object to db
        db.links.insert_one(link)
        # except:
        #     response = {
        #         "status": False,
        #         "error": "Something went wrong. Please try again."
        #     }
        #     return response

        response = {
            "status": True,
            "message": "URL abbrefy successful.",
            "origin": f"http://abbrefy.xyz/bulk/{origin}",
            "url": f"http://abbrefy.xyz/bulk/{location}",
            "title": 'Bulk URL Abbrefy | Download Links Below',
            "dateCreated": link['date_created'].strftime('%b %d, %Y, %I:%M %p'),
            "dateCreated2": link['date_created'].strftime("%b %d, %Y"),
            "slug": location,
            "stealth": False,
            "audience": [],
            "clicks": 0,
            "type": "bulk"
        }

        return response
    
     # abbrefy helper function
    
    # search helper function
    def search(self, term, author):

        try:
            # write a mongo query to search using regex and return as json
            res = mongo.db.links.find({
                "$or": [
                    {"origin": {"$regex": term, "$options":"i" } }, {"title": {"$regex": term, "$options":"i" } },
                    {"slug": {"$regex": term, "$options":"i" } }
                ],
                "author": author
            }).sort([("date_created", -1)])
            

      
        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            return response

        response = {
            "status": True,
            "message": "Abbrefy links search successful.",
            "links": res
        }

        return response

