from sqlite3 import IntegrityError

from flask_restx import Resource, abort
from backend.app import api, logger, db
from backend.auth.auth import requires_auth
from backend.constants.constants import RESPONSE
from backend.database.post import Post
from backend.helpers.extract_exception import extract_exception
from backend.models.post import post_model, post_list_model

post_ns = api.namespace("posts", description="Post endpoints")


# Handles GET, POST requests (requiring no post id)
@post_ns.route("/")
class PostsNoID(Resource):

    # GET "/posts/" endpoint
    @post_ns.marshal_list_with(post_list_model, code=RESPONSE["200_OK"][0], description=RESPONSE["200_OK"][1])
    @post_ns.expect(post_model)
    @requires_auth("get:posts")
    def get(self, payload):
        # Retrieve all posts from newest to oldest
        all_posts = Post.query.order_by(db.desc(Post.id)).all()

        response = {
            "posts": all_posts,
            "total_posts": len(all_posts),
        }

        return response, RESPONSE["200_OK"][0]

    # POST "/posts/" endpoint
    @post_ns.marshal_with(post_model, code=RESPONSE["201_CREATED"][0], description=RESPONSE["201_CREATED"][1])
    @post_ns.expect(post_model)
    @requires_auth("post:post")
    def post(self, payload):
        try:
            # Retrieve the parts of the post from the body
            mood = api.payload["mood"]
            content = api.payload["content"]
            creation_datetime = api.payload["creation_datetime"]
            date_last_modified = api.payload["date_last_modified"]
            is_open = api.payload["is_open"]

            # Build a new post object
            new_post = Post(
                mood=mood,
                content=content,
                creation_datetime=creation_datetime,
                date_last_modified=date_last_modified,
                is_open=is_open,
            )

            new_post.insert()

        # Exception handling
        except Exception as ex:
            logger.exception(ex, exc_info=True)

            # Handle only exceptions which contain code, title, and description segments differently
            db.session.rollback()
            raise ex

        return api.payload, RESPONSE["201_CREATED"][0]


# Handles GET, DELETE, PATCH requests (requiring post id)
@post_ns.route("/<int:post_id>")
class PostsID(Resource):

    # GET "/posts/<int:post_id>" endpoint
    @post_ns.marshal_with(post_model, code=RESPONSE["200_OK"][0], description=RESPONSE["200_OK"][1])
    @post_ns.expect(post_model)
    @requires_auth("get:post")
    def get(self, request, post_id):
        try:
            # Retrieve existing post record to delete
            existing_post = Post.query.filter(Post.id == post_id).one_or_none()

            # If post record doesn't exist, abort
            if existing_post is None:
                err_code = RESPONSE["404_RESOURCE_NOT_FOUND"][0]
                err_desc = RESPONSE["404_RESOURCE_NOT_FOUND"][1]

            else:
                return existing_post, RESPONSE["200_OK"][0]

        # Exception handling
        except Exception as ex:
            logger.exception(ex, exc_info=True)

            db.session.rollback()

            raise ex

        if err_code:
            abort(int(err_code), err_desc)

    # DELETE "/posts/<int:post_id>" endpoint
    @post_ns.marshal_with(post_model, code=RESPONSE["204_NO_CONTENT"][0], description=RESPONSE["204_NO_CONTENT"][1])
    @post_ns.expect(post_model)
    @requires_auth("delete:post")
    def delete(self, request, post_id):
        # Try retrieving and deleting post record
        err_code = ""
        err_desc = ""

        try:
            existing_post = Post.query.filter(Post.id == post_id).one_or_none()

            # If post record doesn't exist, abort
            if existing_post is None:
                err_code = RESPONSE["404_RESOURCE_NOT_FOUND"][0]
                err_desc = RESPONSE["404_RESOURCE_NOT_FOUND"][1]

            else:
                existing_post.delete()
                return "", RESPONSE["204_NO_CONTENT"][0]

        # Exception handling
        except Exception as ex:
            logger.exception(ex, exc_info=True)

            db.session.rollback()

            raise ex

        if err_code:
            abort(int(err_code), err_desc)

    # PATCH "/posts/<int:post_id>" endpoint
    @post_ns.marshal_with(post_model, code=RESPONSE["204_NO_CONTENT"][0], description=RESPONSE["204_NO_CONTENT"][1])
    @post_ns.expect(post_model)
    @requires_auth("patch:post")
    def patch(self, request, post_id):
        # Try retrieving and updating post record
        err_code = ""
        err_desc = ""

        try:
            # Retrieve existing post record to update
            existing_post = Post.query.filter(Post.id == post_id).one_or_none()

            # If post record doesn't exist, abort
            if existing_post is None:
                err_code = RESPONSE["404_RESOURCE_NOT_FOUND"][0]
                err_desc = RESPONSE["404_RESOURCE_NOT_FOUND"][1]

            # Post record does exist, so update
            else:
                existing_post.update(api.payload)
                return "", RESPONSE["204_NO_CONTENT"][0]

        # Error handling
        except (ValueError, IntegrityError) as err:
            logger.error(err, exc_info=True)
            err_code = RESPONSE["422_UNPROCESSABLE_ENTITY"][0]
            err_desc = RESPONSE["422_UNPROCESSABLE_ENTITY"][1]
            db.session.rollback()

        # Exception handling
        except Exception as ex:
            logger.exception(ex, exc_info=True)

            db.session.rollback()

            raise ex

        if err_code:
            abort(int(err_code), err_desc)
