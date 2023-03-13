from flask import Flask, redirect, url_for, request, render_template, send_from_directory, jsonify
import gdown
import os
import shutil
import PyPDF2
app = Flask(__name__)
 
 
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            lang = data.get('lang')
            if lang == '':
                lang = 'id'
            sheet_id = data.get('sheet_id')
            if sheet_id != '':
                sheet_id = str(sheet_id)
                dirName = 'storage/'+lang+'/'+sheet_id
                if not os.path.exists(dirName):
                    os.makedirs(dirName)
            input = data.get('input')
            input = input.split(',')
            if input:
                j = 1
                for i in input:
                    if i != '':
                        i = i.replace("https://drive.google.com/file/d/", "")
                        i = i.replace("/view?usp=drivesdk", "")
                        i = i.replace(" ", "")
                        output = gdown.download(id=i, output=sheet_id+'_'+str(j)+'.pdf', quiet=False)
                        if (output != ''):
                            shutil.move(output, "storage/"+lang+"/"+sheet_id+"/"+output)
                        j+=1
                merge(sheet_id, lang)
                data = {
                    "url" : request.base_url + 'dl/' + lang + '/' + sheet_id + '.pdf'
                }
                return jsonify(data)
            else:
                data = {
                    "error" : "empty array"
                }
                return jsonify(data)
        else:
            data = {
                "error" : "not json data"
            }
            return jsonify(data)
    else:
        return render_template('index.html')

def merge(sheet_id, lang):
    pdfiles = []
    for filename in os.listdir('storage/'+lang+"/"+sheet_id):
        if filename.endswith('.pdf'):
            pdfiles.append(filename)                        
    pdfiles.sort(key = str.lower)
    pdfMerge = PyPDF2.PdfMerger()
    for filename in pdfiles:
        pdfFile = open('storage/'+lang+'/'+sheet_id+'/'+filename, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFile)
        pdfMerge.append(pdfReader)
        pdfFile.close()
    pdfMerge.write('storage/'+lang+'/'+sheet_id+'.pdf')
    shutil.rmtree('storage/'+lang+'/'+sheet_id)


@app.route('/dl/<path:path>')
def download(path):
    return send_from_directory('storage', path)

if __name__ == '__main__':
    app.run(debug=True)