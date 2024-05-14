import cv2

from flask import Flask, Response, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, ForeignKey

app = Flask(__name__)




# Login authentication
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/camproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Define the path for image uploads
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)





class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor_name = db.Column(db.String(100))
    floor_image = db.Column(db.LargeBinary)
    
class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String(100))
    floor_id = db.Column(db.Integer)
    coordinate_x = db.Column(db.Integer)
    coordinate_y = db.Column(db.Integer)
    cam_urls = db.Column(db.String(255))
  
    def __repr__(self):
        return f'<Camera camera_name={self.camera_name} floor_id={self.floor_id} ' \
               f'coordinate_x={self.coordinate_x} coordinate_y={self.coordinate_y}>'
  
    def get_coordinates(self):
      if self.coordinate_x is not None and self.coordinate_y is not None:
         return {'x': self.coordinate_x, 'y': self.coordinate_y}
      else:
         return None
  


@app.route('/')
def index():
  floors = Floor.query.all()
  return render_template('index.html' , floors =floors )
  

@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        data = request.json
        print("Received data from form:", data)  # Print received data for debugging

        # Extract data from the request JSON
        camera_id = data.get('camera_id')
        coordinate_x = data.get('coordinate_x')
        coordinate_y = data.get('coordinate_y')

        # Query the database to find the existing camera entry
        existing_camera = Camera.query.filter_by(id=camera_id).first()

        if existing_camera:
            # Update the existing entry
            existing_camera.coordinate_x = coordinate_x
            existing_camera.coordinate_y = coordinate_y
        else:
            # If the camera doesn't exist, create a new entry
            print("There is no camera on this camid")

        # Commit the changes to the database
        db.session.commit()

        return "Data submitted successfully"
    except Exception as e:
        # Handle exceptions
        return str(e), 500  # Return the error message with a status code


@app.route('/get_image/<int:id>')
def get_image(id):
    try:
        floor = Floor.query.get(id)
        if floor:
            return send_file(BytesIO(floor.floor_image), mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
      
    
@app.route('/get_coordinates/<int:id>')
def get_coordinates(id):
    try:
    
        # floors = Floor.query.all()
        cameras = Camera.query.all()  # Retrieve all cameras
        
        coordinates = []
        for camera in cameras:
            camera_coords = camera.get_coordinates()  # Assuming get_coordinates returns a dictionary
            if camera_coords:
                coordinates.append({'camera_id': camera.id, 'floor_id' : camera.floor_id , 'x': camera_coords['x'], 'y': camera_coords['y']})
                
        return jsonify(coordinates)
    except Exception as e:
        return jsonify({'error': str(e)})






 
   
   
def get_camera_urls():
    try:
        # Retrieve all camera objects from the database
        cameras = Camera.query.all()

        # Create an empty dictionary to store camera IDs and URLs
        camera_urls = {}

        # Extract camera IDs and URLs from the camera objects
        for camera in cameras:
            camera_urls[camera.id] = camera.cam_urls

        # print(camera_urls)
        return camera_urls
    except Exception as e:
        print("Error:", e)
        return {}

   

# Function to generate frames from a specific camera
def generate_frames(camera_url):
    cap = cv2.VideoCapture(camera_url)
    print(camera_url)

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to stream the video for a specific camera
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    camera_urls = get_camera_urls()
    
    camera_url = camera_urls.get(camera_id)
    # camera_url = 0
    print(camera_url)
    if camera_url:
        print("successful")
        return Response(generate_frames(camera_url), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    else:
        return "Camera not found", 404



if __name__ == "__main__":
    app.run(debug=True)






    