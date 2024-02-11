from fastapi import FastAPI, Request, Form, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from Models.main import Model
from loguru import logger
import json 
import uvicorn 


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='application')
app.add_middleware(CORSMiddleware, allow_headers=['*'], allow_methods=['*'], allow_origins=['*'])
model = Model()


@app.get('/', name='docs', description='Redirect to docs page.')
def docs():
	return RedirectResponse('/docs')


@app.get('/users', name='users', description='All users show')
def users():
    try:
        users = model.users()
        return JSONResponse(content={'status': users['status'], 'message': users['message'], 'users': users['users']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.get('/user', name='user', description='Users data show')
def user(email: str = Query(...)):
    try:
        user = model.user(email)
        return JSONResponse(content={'status': user['status'], 'message': user['message'], 'user': user['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/auth', name='auth', description='Users auth')
def auth(data: str = Form(...)):
    try:
        data = json.loads(data)
        auth = model.auth(data)
        return JSONResponse(content={'status': auth['status'], 'message': auth['message'], 'user': auth['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/registration', name='registration', description='Users registration')
def registration(data: str = Form(...)):
    try:
        data = json.loads(data)
        registration = model.registration(data)
        return JSONResponse(content={'status': registration['status'], 'message': registration['message'], 'user': registration['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/update', name='update', description='Users data update')
def update(data: str = Form(...)):
    try:
        data = json.loads(data)
        update = model.update(data)
        return JSONResponse(content={'status': update['status'], 'message': update['message'], 'user': update['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/delete', name='delete', description='Users profile delete')
def delete(data: str = Form(...)):
    try:
        data = json.loads(data)
        delete = model.delete(data)
        return JSONResponse(content={'status': delete['status'], 'message': delete['message'], 'user': delete['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.get('/resetpassword', name='resetpassword', description='Users reset password')
def resetpassword(email: str = Query(...)):
    try:
        resetpassword = model.resetpassword(email)
        return JSONResponse(content={'status': resetpassword['status'], 'message': resetpassword['message']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e)}, status_code=500)


@app.post('/chat_history', name="chat_history", description="Users chat history")
def chat_history(email: str = Form(...)):
    try:
        chat_history = model.chat_history(email)
        return JSONResponse(content={'status': chat_history['status'], 'message': chat_history['message'], 'messages': chat_history['messages']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'messages': None}, status_code=500)


# @app.post('/checkout', name='checkout', description='Payment for user by services')
# def checkout(data: str = Form(...)):
#     try:
#         data = json.loads(data)
#         checkout = model.checkout(data)
#         return JSONResponse(content={'status': checkout['status'], 'message': checkout['message'], 'user': checkout['user']}, status_code=200)

#     except Exception as e:
#         return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.get('/checkout', name='checkout', description='Payment page for user')
def checkout(email: str = Query(...)):
    try:
        checkout = model.checkout(email)
        if checkout['status'] == 500:
            return JSONResponse(content={'status': 500, 'message': checkout['message']}, status_code=200)

        return JSONResponse(content={'status': 200, 'message': checkout['message']}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e)}, status_code=500)


@app.post('/fix_pay', name='fix_pay', description='Fix payment')
async def fix_pay(request: Request):
    try:
        fix_pay = await model.fix_pay(request)
        if fix_pay['status'] == 500:
            logger.error(fix_pay['message'])
        else:
            logger.info(fix_pay['message'])
            
        return True
    except Exception as e:
        logger.error(str(e))
        return True  


@app.post('/send_notifications', name='send_notifications', description='Operation to send notifications to users.')
async def send_notifications(file: UploadFile = File(None), data: str = Form(...)):
    try:
        data = json.loads(data)
        if file is not None:
            data['file'] = file
        send_notifications = await model.send_notifications(data)
        return JSONResponse(content={'status': send_notifications['status'], 'message': send_notifications['message'], 'user': send_notifications['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/send_invoices', name='send_invoices', description='Operation to send invoices to users.')
def send_invoices(file: UploadFile = File(None), data: str = Form(...)):
    try:
        data = json.loads(data)
        if file is not None:
            data['file'] = file
        send_invoices = model.send_invoices(data)
        return JSONResponse(content={'status': send_invoices['status'], 'message': send_invoices['message'], 'user': send_invoices['user']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/delete_task_schedule', name='delete_task_schedule', description='Delete task schedule.')
def delete_task_schedule(data: str = Form(...)):
    try:
        data = json.loads(data)
        delete_task_schedule = model.delete_task_schedule(data)
        return JSONResponse(content={'status': delete_task_schedule['status'], 'message': delete_task_schedule['message']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


@app.post('/all_tasks_schedule', name='all_tasks_schedule', description='Show tasks schedule list for owner.')
def all_tasks_schedule(data: str = Form(...)):
    try:
        data = json.loads(data)
        all_tasks_schedule = model.all_tasks_schedule(data)
        return JSONResponse(content={'status': all_tasks_schedule['status'], 'message': all_tasks_schedule['message'], 'tasks': all_tasks_schedule['tasks']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={'status': 500, 'message': str(e), 'user': None}, status_code=500)


if __name__ == '__main__':
	uvicorn.run('routers:app', host='127.0.0.1', port=8000, reload=True)