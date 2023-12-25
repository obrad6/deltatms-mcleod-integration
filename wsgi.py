from app import initialize_app
import scheduler_tasks

app = initialize_app()
scheduler_tasks.initialize_scheduler()


if __name__ == "__main__":
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)
    app.run(host='0.0.0.0', port=8080)
