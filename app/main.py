import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, default="")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body}


def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.getenv(
        "DATABASE_URL", "sqlite:///notes.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Prometheus metrics at /metrics (used later in Week 4).
    # Skipped in tests because the metrics registry is global.
    if not app.testing and os.getenv("ENABLE_METRICS", "true") == "true":
        from prometheus_flask_exporter import PrometheusMetrics

        PrometheusMetrics(app)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/notes")
    def list_notes():
        return jsonify([n.to_dict() for n in Note.query.order_by(Note.id).all()])

    @app.post("/notes")
    def create_note():
        data = request.get_json(silent=True) or {}
        if not data.get("title"):
            return jsonify(error="title is required"), 400
        note = Note(title=data["title"], body=data.get("body", ""))
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201

    @app.get("/notes/<int:note_id>")
    def get_note(note_id):
        note = db.session.get(Note, note_id)
        if note is None:
            return jsonify(error="not found"), 404
        return jsonify(note.to_dict())

    @app.delete("/notes/<int:note_id>")
    def delete_note(note_id):
        note = db.session.get(Note, note_id)
        if note is None:
            return jsonify(error="not found"), 404
        db.session.delete(note)
        db.session.commit()
        return "", 204

    return app


# Used by gunicorn: `gunicorn app.main:app`
app = create_app()
