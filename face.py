from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask import request, Flask, redirect, url_for, render_template
import os
import face_recognition
import glob

app = Flask(__name__)
app.config['UPLOADED_PHOTO_DEST'] = os.path.dirname(os.path.abspath(__file__))+'/uploadimg'
app.config['UPLOADED_PHOTO_ALLOW'] = IMAGES

#app.config['UPLOAD_PHOTO_URL'] = 'http://localhost:5000/'
photos = UploadSet('PHOTO')

configure_uploads(app, photos)

@app.route('/upload/', methods=['POST', 'GET'])
def upload():
    print app.config['UPLOADED_PHOTO_DEST']
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return redirect(url_for('faceMatch', name=filename))
    return render_template('upload.html')

@app.route('/photo/<name>')
def show(name):
    if name is None:
        abort(404)
    url = photos.url(name)
    return render_template('show.html', url=url, name=name)

@app.route('/matchrlt/<name>')
def matchrlt(name):
    print app.config['UPLOADED_PHOTO_DEST']
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return redirect(url_for('show', name=filename))
    return render_template('upload.html')

@app.route('/facePosition/<name>')
def facePosition(name):
    if name is None:
        abort(404)
    name = './uploadimg/'+name
    image = face_recognition.load_image_file(name)
    face_locations = face_recognition.face_locations(image)
    all = []
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        all.append("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
                                                                                                    right))
    print all
    return render_template('faceposition.html', name=all)

@app.route('/faceMatch/<name>')
def faceMatch(name):
    if name is None:
        abort(404)
    name = './uploadimg/'+name
    unknown_image = face_recognition.load_image_file(name)

    #position fail
    res = []
    if unknown_image is None:
        res.append(" position fail!")
    else:
        try:
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            #original sample
            WSI_MASK_PATH = './orisample/'  #
            wsi_mask_paths = glob.glob(os.path.join(WSI_MASK_PATH, '*.jpg'))
            for pic in wsi_mask_paths:
                known_image = face_recognition.load_image_file(pic)
                print pic
                known_encoding = face_recognition.face_encodings(known_image)[0]
                results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance = 0.4)
                if results[0] == True:
                    res.append(pic.split('/')[2]+" It's a picture of me!")
                else:
                    res.append(pic.split('/')[2]+" not")
        except:
            res.append(" position fail!!")
    return render_template('facematch.html', url=res, name=res)

app.debug = True
app.run()