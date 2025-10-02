from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    """Return all pictures"""
    return jsonify(data), 200


######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    """Return a picture by its id"""
    # Find picture with matching id
    for picture in data:
        if picture.get("id") == id:
            return jsonify(picture), 200
    
    # If picture not found
    return {"message": "Picture not found"}, 404


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    """Create a new picture"""
    picture_data = request.get_json()
    
    # Check if picture_data is provided
    if not picture_data:
        return {"message": "Invalid input parameter"}, 422
    
    # Check if picture with same id already exists
    picture_id = picture_data.get("id")
    if picture_id:
        for existing_picture in data:
            if existing_picture.get("id") == picture_id:
                return {"Message": f"picture with id {picture_id} already present"}, 302
    
    # Add the new picture to data
    data.append(picture_data)
    
    # Save to file
    try:
        with open(json_url, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify(picture_data), 201
    except Exception as e:
        return {"message": "Error saving picture"}, 500


######################################################################
# UPDATE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    """Update a picture by its id"""
    picture_data = request.get_json()
    
    # Check if picture_data is provided
    if not picture_data:
        return {"message": "Invalid input parameter"}, 422
    
    # Find and update the picture
    for i, picture in enumerate(data):
        if picture.get("id") == id:
            # Update the picture
            data[i].update(picture_data)
            
            # Save to file
            try:
                with open(json_url, 'w') as f:
                    json.dump(data, f, indent=2)
                return jsonify(data[i]), 200
            except Exception as e:
                return {"message": "Error updating picture"}, 500
    
    # If picture not found
    return {"message": "picture not found"}, 404


######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    """Delete a picture by its id"""
    # Find and remove the picture
    for i, picture in enumerate(data):
        if picture.get("id") == id:
            deleted_picture = data.pop(i)
            
            # Save to file
            try:
                with open(json_url, 'w') as f:
                    json.dump(data, f, indent=2)
                return "", 204
            except Exception as e:
                # If save fails, add the picture back
                data.insert(i, deleted_picture)
                return {"message": "Error deleting picture"}, 500
    
    # If picture not found
    return {"message": "picture not found"}, 404
