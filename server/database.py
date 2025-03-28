import random;
import math;

from flask_peewee.db import Database
from peewee import TextField, CharField, DateTimeField, ForeignKeyField, fn

from server import application

db = Database( application )


### Database thingies

class PostDB( db.Model ):
	title = TextField()
	date = DateTimeField()

class TagDB( db.Model ):
	tag = CharField( unique=True )
	description = TextField()

class PostTagDB( db.Model ):
	post = ForeignKeyField( PostDB, backref = "tags" )
	tag = ForeignKeyField( TagDB, backref = "posts" )


### CONTENT PROVIDING

#http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.select
#http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.where

PAGE_SIZE = 5
def get_page( page_index ):
	return (
		PostDB.select()
		.where( PostDB.id >= (page_index * PAGE_SIZE) )
		.where( PostDB.id < (page_index * PAGE_SIZE + PAGE_SIZE ) )
		.order_by( PostDB.date.desc() )
		)

def get_most_recent( count = PAGE_SIZE ):
	return PostDB.select().limit( count ).order_by( PostDB.date.desc() )

def get_posts_with_tags( tags ):

	tags = TagDB.select().where( TagDB.tag.in_( tags ) )
	tag_ids = [tag.id for tag in tags]

	tag_count = len(tag_ids)

	result = ( PostDB.select()
		.join(PostTagDB)
		.where(PostTagDB.tag.in_(tag_ids))
		.group_by(PostDB)
		.having( fn.COUNT(PostTagDB.tag) == tag_count)  # Ensures all tags are matched
	)

	return result