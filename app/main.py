from flask import Flask, jsonify, request, send_file, make_response
from logging import getLogger

import boilerplate
from hseling_api_direct_speech.process import process_data
from hseling_api_direct_speech.query import query_data

ALLOWED_EXTENSIONS = ['txt', 'xml']

log = getLogger(__name__)

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=boilerplate.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=boilerplate.CELERY_RESULT_BACKEND
)
celery = boilerplate.make_celery(app)


@celery.task
def process_task(file_ids_list=None):
    files_to_process = boilerplate.list_files(recursive=True,
                                              prefix=boilerplate.UPLOAD_PREFIX)
    if file_ids_list:
        files_to_process = [boilerplate.UPLOAD_PREFIX + file_id
                            for file_id in file_ids_list
                            if (boilerplate.UPLOAD_PREFIX + file_id)
                            in files_to_process]
    data_to_process = {file_id[len(
        boilerplate.UPLOAD_PREFIX):]:
                           boilerplate.get_file(
                               file_id) for file_id in files_to_process}
    processed_file_ids = list()
    for processed_file_id, contents in process_data(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                processed_file_id,
                contents))
    return processed_file_ids


@app.route('/upload', methods=['GET', 'POST'])
def upload_endpoint():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": boilerplate.ERROR_NO_FILE_PART})
        upload_file = request.files['file']
        if upload_file.filename == '':
            return jsonify({"error": boilerplate.ERROR_NO_SELECTED_FILE})
        if upload_file and boilerplate.allowed_file(
                upload_file.filename,
                allowed_extensions=ALLOWED_EXTENSIONS):
            return jsonify(boilerplate.save_file(upload_file))
    return boilerplate.get_upload_form()


@app.route('/files/<path:file_id>')
def get_file_endpoint(file_id):
    if file_id in boilerplate.list_files(recursive=True):
        response = make_response(boilerplate.get_file(file_id))
        response.headers["Content-Disposition"] = \
            "attachment; filename=%s" % file_id
        return response
    if file_id == "gold":
        query_type = request.args.get('type')
        processed_file, file_id = boilerplate.get_gold(query_type)
        return send_file(processed_file, mimetype='txt',
                         attachment_filename=file_id, as_attachment=True)
    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})


@app.route('/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})


@app.route('/process')
@app.route("/process/<file_ids>")
def process_endpoint(file_ids=None):
    file_ids_list = file_ids and file_ids.split(",")
    task = process_task.delay(file_ids_list)
    return jsonify({"task_id": str(task)})


@app.route("/query/<path:file_id>", methods=['GET', 'POST'])
def query_endpoint(file_id=None):
    query_type = request.args.get('type')
    if request.method == 'POST':
        tags_required = request.get_json()
    else:
        tags_required = None

    if file_id is None and query_type is None:
        return jsonify({"error": boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED})
    else:
        if file_id == "gold":
            if query_type == "statistics":
                return jsonify(boilerplate.get_gold_statistics())
            if query_type == "examples":
                limit = request.args.get('limit')
                try:
                    limit = int(limit)
                except ValueError:
                    return jsonify({"error": "wrong limit parameter passed"})
                return jsonify(boilerplate.get_gold_examples(limit))
            else:
                processed_file, file_id = boilerplate.get_gold("txt")
                text = boilerplate.read_file(processed_file)
        else:
            processed_file_id = boilerplate.PROCESSED_PREFIX + file_id
            if processed_file_id in boilerplate.list_files(recursive=True):
                text = boilerplate.get_file(processed_file_id)
            else:
                return jsonify({"error": boilerplate.ERROR_NO_SUCH_FILE})
        return jsonify(query_data(query_type, text, tags_required))


@app.route("/status/<task_id>")
def status_endpoint(task_id):
    return jsonify(boilerplate.get_task_status(task_id))


def get_endpoints(ctx):
    def endpoint(name, description, active=True):
        return {
            "name": name,
            "description": description,
            "active": active
        }

    all_endpoints = [
        endpoint("root", boilerplate.ENDPOINT_ROOT),
        endpoint("scrap", boilerplate.ENDPOINT_SCRAP,
                 not ctx["restricted_mode"]),
        endpoint("upload", boilerplate.ENDPOINT_UPLOAD),
        endpoint("process", boilerplate.ENDPOINT_PROCESS),
        endpoint("query", boilerplate.ENDPOINT_QUERY),
        endpoint("status", boilerplate.ENDPOINT_STATUS)
    ]

    return {ep["name"]: ep for ep in all_endpoints if ep}


@app.route("/")
def main_endpoint():
    ctx = {"restricted_mode": boilerplate.RESTRICTED_MODE}
    return jsonify({"endpoints": get_endpoints(ctx)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)

__all__ = [app, celery]
