import cv2
from flask import Flask, Response, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from geoalchemy2 import Geometry





app = Flask(__name__)

camera = cv2.VideoCapture(0)

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
    
# class Camera(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     camera_name = db.Column(db.String(100))
#     floor_id = db.Column(db.Integer)
#     coordinates = db.Column(Geometry(geometry_type='POINT', srid=4326))   # Assuming coordinates are stored as 'x,y' string

#     def get_coordinates(self):
#         if self.coordinates:
#             return (self.coordinates.x, self.coordinates.y)
#         return None
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)  

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes() 
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # camera = Camera.query.first()
    floors = Floor.query.all()
    
    
    # coordinates = None
    # if camera:
        # coordinates = {'x': camera.get_coordinates()[0], 'y': camera.get_coordinates()[1]}
    return render_template('index.html' , floors= floors ,)

    # else :
    #  return jsonify({'error': 'Camera not found'})

    



@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_image/<int:floor_id>')
def get_image(floor_id):
    try:
        floor = Floor.query.get(floor_id)
        if floor:
            return send_file(BytesIO(floor.floor_image), mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
    



if __name__ == "__main__":
    app.run(debug=True)







