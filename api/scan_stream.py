from flask import Blueprint, Response, stream_with_context
import subprocess

scan_stream = Blueprint("scan_stream", __name__)

@scan_stream.route("/scan-stream", methods=["GET"])
def stream_scan():
    def generate():
        # Beispiel: Statt "whoami" auch "airodump-ng" oder dein Wrapper möglich
        process = subprocess.Popen(["whoami"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in iter(process.stdout.readline, ''):
            yield f"data: {line.strip()}\n\n"
        process.stdout.close()
        process.wait()

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
