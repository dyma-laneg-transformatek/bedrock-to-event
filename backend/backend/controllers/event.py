from backend import app, db
from backend.utils import requires_auth
from backend.models import Event
from flask import request
from sqlalchemy import select, func
from datetime import datetime



# ----------------------------- visitor side -----------------------------------
# get events filtred by status (ongoing, upcomming, past) , tags, location

def event_to_dict( event ):
     result = {
                 "slug": event.slug,
                 "title": event.title,
                 "organizer": event.organizer,
                 "location": event.location,
                 "start_date": event.start_date.isoformat() if event.start_date else None,
                 "end_date": event.end_date.isoformat() if event.end_date else None,
                 "tags":event.tags,
                 "description": event.description,
                 "image_url":event.image_url,
                 "source_link": event.source_link
             }
     return result

@app.route("/events", methods=["GET"])
def get_events():
    
    status = request.args.get("status")
    location = request.args.get("location")
    tags = request.args.get("tags", "").split(",") if request.args.get("tags") else []

    now = func.now()
    filters = []
    if location:
        filters.append(Event.location.ilike(f"%{location}%"))
    if tags:
        filters.append(Event.tags.overlap(tags))

    order_by = None

    match status:
        case "ongoing":
            filters.extend([Event.start_date <= now, Event.end_date >= now])
            order_by = Event.start_date.asc()
        case "upcoming":
            filters.append(Event.start_date > now)
            order_by = Event.start_date.asc()
        case "past":
            filters.append(Event.end_date < now)
            order_by = Event.end_date.desc()
        case _:
            filters.append(Event.end_date >= now)
            order_by = Event.start_date.asc()

    stmt = select(Event).where(*filters)
    stmt = stmt.order_by(order_by)

    events = db.session.scalars(stmt).all()

    results = [
        event_to_dict(event)
        for event in events
    ]

    return {"count": len(results), "events": results}

# ----------------------------- admin side -----------------------------------
# CRUD functions 
# helper functions

def find_event(slug):
         stmt = select(Event).where(Event.slug == slug)
         event = db.first_or_404(stmt)
         return event  
         

# create with post 
@app.route('/events', methods=['POST'])
def post_events ():
 
        data = request.get_json()
        new_event = Event(
            slug = data['slug'],
            title =  data['title'],
            organizer =  data['organizer'],
            location =  data['location'],
            start_date =  datetime.fromisoformat(data['start_date']),
            end_date = datetime.fromisoformat(data['end_date']),
            tags = data['tags'],
            description = data['description'],
            image_url = data['image_url'],
            source_link = data['source_link'])

        db.session.add(new_event)
        db.session.commit()
        return {"message": f"event : {new_event.title} has been created successfully"}
     
# Read event with slug
@app.route('/events/<slug>', methods=['GET'])
def get_event (slug): 
    event = find_event(slug)
    result = event_to_dict(event)
    return {"message": "success", "event": result}


# update with put
@app.route('/events/<slug>', methods=['PUT'])
def put_event (slug):
    event = find_event(slug)
    data = request.get_json()
   
    event.title =  data['title']
    event.organizer =  data['organizer']
    event.location =  data['location']
    event.start_date =  datetime.fromisoformat(data['start_date'])
    event.end_date = datetime.fromisoformat(data['end_date'])
    event.tags = data['tags']
    event.description = data['description']
    event.image_url = data['image_url']
    event.source_link = data['source_link']

    db.session.add(event)
    db.session.commit() 

    result = event_to_dict(event)

    return {"message": f"event {event.title} updated successfully ", "event": result}

# delete
@app.route('/events/<slug>', methods=['DELETE'])
def delete_event (slug):
    event = find_event(slug)
    db.session.delete(event)
    db.session.commit()

    return {"message":"event  deleted successfully "}
    