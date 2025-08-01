from celery import Celery
import socketio



# Create a Celery app with Redis as broker and backend
celery = Celery(
    'tasks',  # Name of the task module
    broker='redis://localhost:6379/0',   # Redis queue (broker)
    backend='redis://localhost:6379/0'   # For storing task results
) 

@celery.task
def stu_notifications(email,message):
    sio = socketio.Client()
    try:
        sio.connect('http://localhost:8000')
        sio.emit('notify',{'email':email, 'message' : message})
        sio.disconnect()
    except Exception as e:
        print(f"SocketIO connection failed: {e}")    