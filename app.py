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
  floor_id = db.Column(db.Integer, ForeignKey('Floor.id'))  # Define ForeignKey
  coordinate_x = db.Column(db.Integer)
  coordinate_y = db.Column(db.Integer)
  
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






    