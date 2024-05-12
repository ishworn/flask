import cv2

from flask import Flask, Response, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, ForeignKey

app = Flask(__name__)


  




cam = cv2.VideoCapture(0)

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
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'))  # Adjust this if necessary
    coordinate_x = db.Column(db.Integer)
    coordinate_y = db.Column(db.Integer)
  
    def __repr__(self):
        return f'<Camera camera_name={self.camera_name} floor_id={self.floor_id} ' \
               f'coordinate_x={self.coordinate_x} coordinate_y={self.coordinate_y}>'
  
    def get_coordinates(self):
      if self.coordinate_x is not None and self.coordinate_y is not None:
         return {'x': self.coordinate_x, 'y': self.coordinate_y}
      else:
         return None

    
 

  # Return None if coordinates are not set

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)  

def generate_frames():
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes() 
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    
 
  floors = Floor.query.all()
 
  
  
  return render_template('index.html' , floors =floors )
  # ... rest of the code


   
    
    # try:
    #     # Try to query the Test table
    #     floors = Floor.query.first()
    #     return 'Database connection successful'
    # except Exception as e:
    #     return f'Database connection failed: {str(e)}'
    



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


























# @app.route('/submit-form', methods=['POST'])
# def submit_form():
#     try:
#         data = request.json
#         print("Received data from form:", data)  # Print received data for debugging

#         # Extract data from the request JSON
#         id = data.get('camera_id')
#         coordinate_x = data.get('coordinate_x')
#         coordinate_y = data.get('coordinate_y')

#         # Retrieve the previous floor_id value from the database
#         previous_camera = Camera.query.order_by(Camera.id.desc()).first()
#         previous_floor_id = previous_camera.floor_id if previous_camera else None
#         previous_camera_name = previous_camera.camera_name if previous_camera else None
        

#         # Save data to the database
#         new_camera = Camera(id=id, floor_id=previous_floor_id,camera_name=previous_camera_name, coordinate_x=coordinate_x, coordinate_y=coordinate_y)
#         db.session.add(new_camera)
#         db.session.commit()

#         return jsonify({'message': 'Data saved successfully'}), 201

#     except Exception as e:
#         print("Error processing form data:", e)
#         return jsonify({'error': 'Internal server error'}), 500



# @app.route('/get-data', methods=['GET'])
# def get_data():
#     cameras = Camera.query.all()
#     data_list = []
#     for camera in cameras:
#         data_list.append({
#             'camera_name': camera.camera_name,
#             'floor_id': camera.floor_id,
#             'coordinate_x': camera.coordinate_x,
#             'coordinate_y': camera.coordinate_y
#         })
#     return jsonify(data_list)





@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
    
        floors = Floor.query.all()
        cameras = Camera.query.all()  # Retrieve all cameras
        
        coordinates = []
        for camera in cameras:
            camera_coords = camera.get_coordinates()  # Assuming get_coordinates returns a dictionary
            if camera_coords:
                coordinates.append({'camera_id': camera.id, 'floor_id' : camera.floor_id , 'x': camera_coords['x'], 'y': camera_coords['y']})
                
        return jsonify(coordinates)
    except Exception as e:
        return jsonify({'error': str(e)})






if __name__ == "__main__":
    app.run(debug=True)






    