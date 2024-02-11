from env import ENV
from twilio.rest import Client
from SMTPEmail import SMTP
from liqpay import LiqPay
from datetime import datetime
from time import time
from loguru import logger
import pandas as pd
import io
import json
import re
import boto3
import cryptocode
import random
import string
import openpyxl
# import pywhatkit
import aiohttp


# recieving constants fron ENV class
env = ENV()
constans = env.data()
smtp_server = constans.get('smtp_server')
smtp_account = constans.get('smtp_account')
smtp_password = constans.get('smtp_password')
twilio_account_sid = constans.get('twilio_account_sid')
twilio_auth_token = constans.get('twilio_auth_token')
twilio_phone_number = constans.get('twilio_phone_number')
aws_access_key_id = constans.get('aws_access_key_id')
aws_secret_access_key = constans.get('aws_secret_access_key')
aws_access_key_id_s3 = constans.get('aws_access_key_id_s3')
aws_secret_access_key_s3 = constans.get('aws_secret_access_key_s3')
dynamodb_table_name = constans.get('dynamodb_table_name')
dynamodb_table_chat_name = constans.get('dynamodb_table_chat_name')
dynamodb_table_tasks = constans.get('dynamodb_table_tasks')
s3_bucket = constans.get('s3_bucket')
liqpay_public_key = constans.get('liqpay_public_key')
liqpay_private_key = constans.get('liqpay_private_key')
whatsapp_instance_id = constans.get('whatsapp_instance_id')
whatsapp_token = constans.get('whatsapp_token')
api_url = 'https://komunna-501136d53d67.herokuapp.com'
front_url = 'https://master.d3jv8ddv1656pn.amplifyapp.com'


# initing connections with services

twilio_client = Client(twilio_account_sid, twilio_auth_token)
gmail_client = SMTP(SMTP_server=smtp_server, SMTP_account=smtp_account, SMTP_password=smtp_password)
dynamodb_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id_s3, aws_secret_access_key=aws_secret_access_key_s3, region_name='us-east-1')
liqpay_client = LiqPay(liqpay_public_key, liqpay_private_key)


class OtherOperations:
	def correct_phone_number(self, number):
		number = str(number)
		if number.startswith("380") and len(number) == 12:
			return True

		return False 


	def correct_email_address(self, email):
		pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
		match = re.match(pattern, email)
		return bool(match)


	def file_handling(self, file):
		read_file = pd.read_excel(file, engine='openpyxl')
		users = read_file.values.tolist()
		return users


	def generate_password(self, length=16):
	    characters = string.ascii_letters + string.digits + string.punctuation
	    password = ''.join(random.choice(characters) for _ in range(length))
	    return password


	def send_message_to_users_email(self, action, name, email, password=None):
		if action == 'resetpassword':
			if password is not None:
				try:
					gmail_client.create_mime(
						recipient_email_addr=email,
						sender_email_addr='komunnaservice@gmail.com',
						subject=f"Зміна паролю",
						sender_display_name='Komunna Service',
						recipient_display_name=name,
						content_html=f'<h4 class="margin: 0px;">Вітаємо!</h4><p class="margin: 0px;">Ваш новий пароль для входу в аккаунт сервісу Komunna: {password}.<p><p class="margin: 0px; margin-top: 10px; font-width: bold;">З повагою, Komunna!</p>',
						content_text=f'Ваш новий пароль для входу в аккаунт сервісу Komunna: {password}.'
					)

					gmail_client.send_msg()

					return {'status': 200}
				except Exception as e:
					return {'status': 500, 'message': str(e)}
			else:
				return {'status': 500, 'message': 'Не вдалося згенерувати новий пароль'}


	def translate_month(self, month_name):
		if month_name == 'January':
			return 'Січень'
		if month_name == 'February':
			return 'Лютий'
		if month_name == 'March':
			return 'Березень'
		if month_name == 'April':
			return 'Квітень'
		if month_name == 'May':
			return 'Травень'
		if month_name == 'June':
			return 'Червень'
		if month_name == 'July':
			return 'Липень'
		if month_name == 'August':
			return 'Серпень'
		if month_name == 'September':
			return 'Вересень'
		if month_name == 'October':
			return 'Жовтень'
		if month_name == 'November':
			return 'Листопад'
		if month_name == 'December':
			return 'Грудень'


class Model:
	def __init__(self):
		self.otherOperations = OtherOperations()


	def users(self):
		try:
			scan = dynamodb_client.scan(TableName=dynamodb_table_name)
			if 'Items' not in scan.keys():
				{'status': 500, 'message': f"Отримання списку усіх користувачів: користувачів не знайдено!", 'users': None}

			users = []
			for user in scan['Items']:
				name = user['name']['S']
				email = user['email']['S']
				credit = user['credit']['S']
				users.append({"name": name, "email": email, "credit": f"{float(credit):.2f}"})

			return {'status': 200, 'message': None, 'users': users}

		except Exception as e:
			return {'status': 500, 'message': f"Отримання списку усіх користувачів: помилка {str(e)}!", 'users': None}


	def user(self, email):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})
			if 'Item' not in user.keys():
				{'status': 500, 'message': f"Отримання інформації про користувача: користувачів не знайдено!", 'users': None}

			user_credit = user['Item']['credit']['S']

			return {'status': 200, 'message': None, 'user': {'credit': f"{float(user_credit):.2f}"}}

		except Exception as e:
			return {'status': 500, 'message': f"Отримання інформації про користувача: помилка {str(e)}!", 'user': None}


	def auth(self, data):
		try:
			email = data.get('email')
			password = data.get('password')

			if None in [email, password]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для авторизації!", 'user': None}

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' not in user.keys():
				return {'status': 500, 'message': "Користувача не знайдено!", 'user': None}

			user_name = user['Item']['name']['S']
			user_email = user['Item']['email']['S']
			user_credit = user['Item']['credit']['S']
			user_password = user['Item']['password']['S']
			decrypt_user_password = cryptocode.decrypt(user_password, 'password')

			user_activity = user['Item'].get('activity')
			if user_activity is not None:
				user_activity = user_activity['S']

			if decrypt_user_password != password:
				return {'status': 500, 'message': "Невірно вказаний пароль!", 'user': None}

			return {'status': 200, 'message': None, 'user': {"name": user_name, "email": user_email, "credit": f"{float(user_credit):.2f}", "password": decrypt_user_password, "activity": user_activity}}

		except Exception as e:
			return {'status': 500, 'message': f"Авторизація: помилка {str(e)}!", 'user': None}


	def registration(self, data):
		try:
			name = data.get('name')
			email = data.get('email')
			password = data.get('password')
			confirm_password = data.get('confirm_password')

			if None in [name, email, password, confirm_password]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для реїстрації!", 'user': None}

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' in user.keys():
				return {'status': 500, 'message': "Користувач вже зареєстрований під таким email!", 'user': None}

			if password != confirm_password:
				return {'status': 500, 'message': "Непідтверджений пароль!", 'user': None}

			user_data = {
				"name": {"S": name},
				"email": {"S": email},
				"password": {"S": cryptocode.encrypt(password, 'password')},
				"credit": {"S": "0"},
				"paid": {"S": "0"}
			}

			user = dynamodb_client.put_item(TableName=dynamodb_table_name, Item=user_data)

			return {'status': 200, 'message': None, 'user': {"name": name, "email": email, "credit": "0", "password": password, "activity": None}}

		except Exception as e:
			return {'status': 500, 'message': f"Авторизація: помилка {str(e)}!", 'user': None}


	def update(self, data):
		try:
			old_email = data.get('old_email')
			new_name = data.get('new_name')
			new_email = data.get('new_email')
			new_password = data.get('new_password')

			if old_email == None:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для оновлення користувацьких даних!", 'user': None}

			user_with_old_email = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': old_email}})

			if 'Item' not in user_with_old_email.keys():
				return {'status': 500, 'message': f"Користувача з поштою {old_email} не знайдено!", 'user': None}

			if new_email is not None and new_email != old_email:
				user_with_new_email = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': new_email}})
				if 'Item' in user_with_new_email.keys():
					return {'status': 500, 'message': f"Користувач вже зареєстрований під email {new_email}!", 'user': None}

			name = user_with_old_email['Item']['name']['S'] if new_name is None else new_name
			email = user_with_old_email['Item']['email']['S'] if new_email is None else new_email
			password = user_with_old_email['Item']['email']['S'] if new_password is None else cryptocode.encrypt(new_password, 'password')
			credit = user_with_old_email['Item']['credit']['S']
			activity = user_with_old_email['Item'].get('activity')
			paid = user_with_old_email['Item']['paid']['S']

			user_data = {
				"name": {"S": name},
				"email": {"S": email},
				"password": {"S": password},
				"credit": {"S": credit},
				"paid": {"S": paid}
			}

			if activity is not None:
				activity = activity['S']
				user_data['activity'] = {"S": activity}

			dynamodb_client.delete_item(TableName=dynamodb_table_name, Key={'email': {'S': old_email}})
			dynamodb_client.put_item(TableName=dynamodb_table_name, Item=user_data)

			return {'status': 200, 'message': None, 'user': {"name": name, "email": email, "password": cryptocode.decrypt(password, "password"), "credit": f"{float(credit):.2f}", "activity": activity}}

		except Exception as e:
			return {'status': 500, 'message': f"Оновлення користувацьких даних: помилка {str(e)}!", 'user': None}


	def delete(self, data):
		try:
			email = data.get('email')
			password = data.get('password')

			if None in [email, password]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для видалення профілю!", 'user': None}

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' not in user.keys():
				return {'status': 500, 'message': "Користувача не знайдено!", 'user': None}

			user_password = user['Item']['password']['S']

			if cryptocode.decrypt(user_password, 'password') != password:
				return {'status': 500, 'message': "Невірно вказаний пароль для видалення профілю!", 'user': None}

			delete_user = dynamodb_client.delete_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			return {'status': 200, 'message': 'Профіль успішно видалено!', 'user': None}

		except Exception as e:
			return {'status': 500, 'message': f"Авторизація: помилка {str(e)}!", 'user': None}


	def resetpassword(self, email):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' not in user.keys():
				return {'status': 500, 'message': "Користувача не знайдено!", 'user': None}

			password = self.otherOperations.generate_password()
			encrypt_password = cryptocode.encrypt(password, 'password')
			name = user['Item']['name']['S']

			send_message_to_users_email = self.otherOperations.send_message_to_users_email('resetpassword', name, email, password)
			if send_message_to_users_email['status'] == 500:
				return {'status': 500, 'message': f"Зміна паролю: помилка {send_message_to_users_email['message']}"}

			dynamodb_client.update_item(TableName=dynamodb_table_name, Key={'email': {'S': email}}, AttributeUpdates={'password': {'Value': {'S': encrypt_password}, 'Action': 'PUT'}})

			return {'status': 200, 'message': f"Зміна паролю успішно виконана. Новий пароль надіслано на Вашу пошту!"}

		except Exception as e:
			return {'status': 500, 'message': f"Зміна паролю: помилка {str(e)}!"}


	def chat_history(self, email):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_chat_name, Key={'email': {'S': email}})
			messages = user.get('Item', {}).get('messages', {}).get('S')
			if messages is None:
				return {'status': 500, 'message': f"Відображення історії чата: історія відсутня!", 'messages': None}

			return {'status': 200, 'message': None, 'messages': json.loads(messages)}
		except Exception as e:
			return {'status': 500, 'message': f"Відображення історії чата: помилка {str(e)}!", 'messages': None}


	# def checkout(self, data):
	# 	try:
	# 		auth_email = data.get('auth_email')
	# 		phone = data.get('phone')
	# 		card = data.get('card')
	# 		card_exp_month = data.get('card_exp_month')
	# 		card_exp_year = data.get('card_exp_year')
	# 		card_cvv = data.get('card_cvv')

	# 		if None in [auth_email, phone, card, card_exp_month, card_exp_year, card_cvv] or 0 in [len(card), len(card_cvv), len(phone)]:
	# 			return {'status': 500, 'message': "Не вказані усі потрібні параметри для створення оплати!", "user": None}

	# 		if len(phone) != 13:
	# 			return {'status': 500, 'message': "Невірно вказан телефон! Потрібний формат: +380501234567", "user": None}

	# 		card_exp_month = f"0{str(card_exp_month)}" if len(str(card_exp_month)) == 1 else str(card_exp_month)
	# 		card_exp_year = str(card_exp_year)[2:] if len(str(card_exp_year)) == 4 else str(card_exp_year)

	# 		user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})
	# 		if 'Item' not in user.keys():
	# 			return {'status': 500, 'message': "Користувача не знайдено!", "user": None}

	# 		credit = user['Item']['credit']['S']

	# 		if credit == "0":
	# 			return {'status': 500, 'message': "Ваш борг становить 0$. Оплата не потрібна!", "user": None}

	# 		order_id = round(time() * 1000)

	# 		res = liqpay_client.api("request", {
	# 			"action"         : "pay",
	# 			"version"        : "3",
	# 			"phone"          : phone,
	# 			"amount"         : credit,
	# 			"currency"       : "USD",
	# 			"description"    : f"Оплата за послуги Komunna для користувача з поштою {auth_email}",
	# 			"order_id"       : order_id,
	# 			"card"           : card,
	# 			"card_exp_month" : card_exp_month,
	# 			"card_exp_year"  : card_exp_year,
	# 			"card_cvv"       : card_cvv
	# 		})

	# 		if res['status'] != 'success':
	# 			return {'status': 500, 'message': res['err_description'], "user": None}

	# 		dynamodb_client.update_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}}, AttributeUpdates={"credit": {"Value": {"S": "0"}, "Action": "PUT"}})

	# 		user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})
	# 		data = {
	# 			"name": user['Item']['name']['S'],
	# 			"email": user['Item']['email']['S'],
	# 			"password": cryptocode.decrypt(user['Item']['password']['S'], 'password'),
	# 			"credit": f"{float(user['Item']['credit']['S']):.2f}",
	# 		}

	# 		activity = user['Item'].get('activity')
	# 		if activity is not None:
	# 			data['activity'] = activity['S']

	# 		return {'status': 200, 'message': "Оплата пройшла успішно!", "user": data}
	# 	except Exception as e:
	# 		return {'status': 500, 'message': str(e), "user": None}


	def checkout(self, email):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' not in user.keys():
				return {'status': 500, "message": "Користувача не знайдено!"}

			credit = user['Item']['credit']['S']

			if credit == "0":
	 			return {'status': 500, "message": "Ваш борг становить 0$. Оплата не потрібна!"}

			order_id = round(time() * 1000)

			html = liqpay_client.cnb_form({
				"action"         : "pay",
				"amount"         : credit,
				"currency"       : "USD",
				"description"    : f"Оплата за послуги сервісу Komunna. Платник: {email}",
				"order_id"       : order_id,
				"version"        : "3",
				"sender_first_name": email,
				"result_url"	 : f"{front_url}/?email={email}",
				"server_url"	 : f"{api_url}/fix_pay",
			})

			return {'status': 200, "message": html}
		except Exception as e:
			return {'status': 500, "message": str(e)}


	async def fix_pay(self, request):
		try:
			form = await request.form()
			data = form.get('data')
			response = liqpay_client.decode_data_from_str(data)

			if response['status'] in ['error', 'failure']:
				return {'status': 500, 'message': response['err_description']}

			email = response['description'].split('Платник: ')[1]
			amount = response['amount']
			
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': email}})

			if 'Item' not in user.keys():
				return {'status': 500, 'message': "Користувача не знайдено!"}

			paid = float(user['Item']['paid']['S']) + float(amount)
			paid = f"{float(paid):.2f}"

			dynamodb_client.update_item(TableName=dynamodb_table_name, Key={'email': {'S': email}}, AttributeUpdates={'credit': {'Value': {'S': '0'}, 'Action': 'PUT'}, 'paid': {'Value': {'S': str(paid)}, 'Action': 'PUT'}})

			return {'status': 200, 'message': f"Оплата виконана успішно!"}

		except Exception as e:
			return {'status': 500, 'message': str(e)}


	def credit(self, auth_email, amount_spent):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})
			current_date = datetime.now()
			month_name = current_date.strftime('%B')
			month_name = self.otherOperations.translate_month(month_name)

			if 'Item' in user.keys():
				credit = float(user['Item']['credit']['S'])
				credit = credit + float(amount_spent)

				activity = user['Item'].get('activity')
				if activity is None:
					activity = {"months": [month_name], "activity": {month_name: "1"}}
				else:
					activity = json.loads(activity['S'])
					months = activity['months']
					activity_month = activity["activity"]
					if month_name in months:
						if month_name in activity_month.keys():
							count = activity_month[month_name]
							activity_month[month_name] = str(int(count) + 1)
						else:
							activity_month[month_name] = "1"
					else:
						activity['months'].append(month_name)
						
						if len(activity['months']) > 6:
							activity = {"months": [month_name], "activity": {month_name: "1"}}
						else:
							activity_month[month_name] = "1"

				dynamodb_client.update_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}}, AttributeUpdates={'credit': {"Value": {"S": str(credit)}, "Action": "PUT"}, 'activity': {'Value': {'S': json.dumps(activity)}}})

				print(f"Credit func success: credit replenished for {auth_email}")
				return 

			print(f"Credit func error: {auth_email} not found")
			return 
		except Exception as e:
			print(f"Credit func error: {str(error)}")
			return


	def if_action_true(self, auth_email):
		try:
			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})

			if 'Item' in user.keys():
				credit = float(user['Item']['credit']['S'])
				if credit >= 15.0:
					return {"error": False, "status": 500, "message": False, "credit": f"{credit:.2f}"}

				return {"error": False, "status": 200, "message": False, "credit": f"{credit:.2f}"}

			return {"error": True, "status": False, "message": "Користувача не знайдено!", "credit": False}

		except Exception as e:
			return {"error": True, "status": False, "message": str(e), "credit": False}


	def delete_task_schedule(self, data):
		try:
			auth_email = data.get('auth_email')
			created_at = data.get('created_at')

			if None in [auth_email, created_at]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для видалення відкладеної задачі!"}

			user = dynamodb_client.get_item(TableName=dynamodb_table_tasks, Key={"email": {"S": auth_email}})
			tasks = user.get('Item', {}).get('tasks', {}).get('S', [])
			if len(tasks) == 0:
				return {'status': 500, 'message': "Жодної відкладеної задачі не знайдено!"}

			tasks = json.loads(tasks)
			for task in tasks:
				if task['created_at'] == created_at:
					tasks.remove(task)
					dynamodb_client.update_item(TableName=dynamodb_table_tasks, Key={"email": {"S": auth_email}}, AttributeUpdates={"tasks": {"Value": {"S": json.dumps(tasks)}, "Action": "PUT"}})
					return {'status': 200, 'message': "Відкладена задача успішно видалена!"}

			return {'status': 500, 'message': "Вказаної відкладеної задачі не знайдено!"}
		except Exception as e:
			logger.error(str(e))
			return {"status": 500, "message": "Видалення відкладеної задачі не виконано! Спробуйте ще раз!"}


	def all_tasks_schedule(self, data):
		try:
			auth_email = data.get('auth_email')

			if None in [auth_email]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для відображення списку відкладених задач!", 'tasks': None}

			user = dynamodb_client.get_item(TableName=dynamodb_table_tasks, Key={"email": {"S": auth_email}})
			tasks = user.get('Item', {}).get('tasks', {}).get('S', "[]")
			return {'status': 200, 'message': None, 'tasks': tasks}			
		except Exception as e:
			logger.error(str(e))
			return {"status": 500, "message": "Відображення списку відкладених задач не виконано! Спробуйте ще раз!", 'tasks': None}
			

	def send_invoices(self, data):
		try:
			auth_email = data.get('auth_email')
			file = data.get('file')
			public_key = data.get('public_key')
			private_key = data.get('private_key')
			company = data.get('company')
			task_schedule = data.get('task_schedule')
			task_schedule_run_datetime = data.get('task_schedule_run_datetime')
			task_executing = data.get('task_executing')

			if None in [auth_email, file, public_key, private_key, company]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для створення розсилання інвойсу!", 'user': None}

			if_action_true = self.if_action_true(auth_email)

			if if_action_true["error"]:
				return {'status': 500, "message": if_action_true["message"], 'user': None}

			if if_action_true["status"] == 500:
				return {'status': 500, 'message': f"Накопився борг на суму {if_action_true['credit']}$. Опція буде доступна після його погашення!", 'user': None}

			if task_executing is None:
				filename = file.filename
				if not filename.endswith('.xlsx'):
					return {'status': 500, 'message': "Завантажте файл з розширенням .xlsx!", 'user': None}
				users = self.otherOperations.file_handling(file.file)
			else:
				users = file

			if len(users[0]) != 4:
				return {'status': 500, 'message': "Невірно складена таблиця!", 'user': None}

			order_id = round(time() * 1000)

			if None not in [task_schedule, task_schedule_run_datetime] and False not in [task_schedule, task_schedule_run_datetime]:
				try:
					file = self.otherOperations.file_handling(file.file)
					user_tasks = dynamodb_client.get_item(TableName=dynamodb_table_tasks, Key={"email": {"S": auth_email}})
					tasks = user_tasks.get('Item', {}).get('tasks', {}).get('S', None)
					tasks = json.loads(tasks) if tasks is not None else None
					new_task = {'target': 'invoice', 'time': task_schedule_run_datetime, 'created_at': order_id, 'file': file, 'auth_email': auth_email, 'public_key': public_key, 'private_key': private_key, 'company': company}
					if isinstance(tasks, list):
						for task in tasks:
							if task['target'] == 'invoice' and task['time'] == task_schedule_run_datetime:
								return {'status': 500, 'message': "Така задача з часом виконання вже існує!", 'user': None}
						tasks.append(new_task)

					upload_task = tasks if tasks is not None else [new_task]

					dynamodb_client.update_item(
					    TableName=dynamodb_table_tasks,
					    Key={"email": {"S": auth_email}},
					    UpdateExpression="SET tasks = :tasks",
					    ExpressionAttributeValues={":tasks": {"S": json.dumps(upload_task)}}
					)

					return {'status': 200, 'message': f"Задача для розсилання інвойсу створена на час {task_schedule_run_datetime}!", 'user': None}
				except Exception as e:
					logger.error(str(e))
					return {'status': 500, 'message': "Створення відкладеної задачі для розсилання інвойсу: опція тимчасово не працює!", 'user': None}

			amount_spent = 0
			for user in users:
				name = user[0]
				email = user[1]
				number =user[2]
				amount = user[3]

				if None not in [name, email, number, amount]:
					if_number_correct = self.otherOperations.correct_phone_number(number)
					if_email_correct = self.otherOperations.correct_email_address(email)

					if if_number_correct and if_email_correct:
						date_time = datetime.now().strftime("%m/%d/%Y")
						liqpay = LiqPay(public_key, private_key)
						res = liqpay.api("request", {
							"action"    : "invoice_send",
							"version"   : "3",
							"description": f"Вітаємо, {name}! Платіж за послуги від {company} на {date_time} р.",
							"email"     : email,
							"amount"    : amount,
							"phone"		: f"+{number}",
							"currency"  : "UAH",
							"order_id"  : order_id,
						}) 

						if res["status"] in ["invoice_wait", "success"]:
							amount_spent += 0.15
						else:
							return {'status': 500, 'message': f"Неуспішний платіж. Некоректно заповнені дані!", 'user': None}


			self.credit(auth_email, amount_spent)

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})
			data = {
				"name": user['Item']['name']['S'],
				"email": user['Item']['email']['S'],
				"password": cryptocode.decrypt(user['Item']['password']['S'], 'password'),
				"credit": f"{float(user['Item']['credit']['S']):.2f}",
			}

			activity = user['Item'].get('activity')
			if activity is not None:
				data['activity'] = activity['S']

			return {'status': 200, 'message': f"Розсилання інвойсу: операція виконана успішно на суму {amount_spent:.2f}$!", 'user': data}
		except Exception as e:
			logger.error(f"Розсилання інвойсу: помилка {str(e)}!")
			return {'status': 500, 'message': f"Розсилання інвойсу: опція тимчасово не працює!"}


	async def send_notifications(self, data):
		try:
			auth_email = data.get('auth_email')
			company = data.get('company')
			subject = data.get('subject')
			message = data.get('message')
			to_email = data.get('to_email')
			to_phone = data.get('to_phone')
			to_whatsapp = data.get('to_whatsapp')
			file = data.get('file')
			task_schedule = data.get('task_schedule')
			task_schedule_run_datetime = data.get('task_schedule_run_datetime')
			task_executing = data.get('task_executing')

			if None in [auth_email, company, file, to_email, to_phone, to_whatsapp, message, subject]:
				return {'status': 500, 'message': "Не вказані усі потрібні параметри для створення розсилання!", 'user': None}

			if_action_true = self.if_action_true(auth_email)

			if if_action_true["error"]:
				return {'status': 500, "message": if_action_true["message"], 'user': None}

			if if_action_true["status"] == 500:
				return {'status': 500, 'message': f"Накопився борг на суму {if_action_true['credit']}$. Опція буде доступна після його погашення!", 'user': None}

			if task_executing is None:
				filename = file.filename
				if not filename.endswith('.xlsx'):
					return {'status': 500, 'message': "Завантажте файл з розширенням .xlsx!", 'user': None}
				users = self.otherOperations.file_handling(file.file)
			else:
				users = file

			if len(users[0]) != 3:
				return {'status': 500, 'message': "Невірно складена таблиця!", 'user': None}

			if None not in [task_schedule, task_schedule_run_datetime] and False not in [task_schedule, task_schedule_run_datetime]:
				try:
					file = self.otherOperations.file_handling(file.file)
					user_tasks = dynamodb_client.get_item(TableName=dynamodb_table_tasks, Key={"email": {"S": auth_email}})
					tasks = user_tasks.get('Item', {}).get('tasks', {}).get('S', None)
					tasks = json.loads(tasks) if tasks is not None else None
					created_at = round(time() * 1000)
					new_task = {'target': 'notification', 'time': task_schedule_run_datetime, 'created_at': created_at, 'file': file, 'auth_email': auth_email, 'company': company, 'subject': subject, 'message': message, 'to_email': to_email, 'to_phone': to_phone, 'to_whatsapp': to_whatsapp}
					if isinstance(tasks, list):
						for task in tasks:
							if task['target'] == 'notification' and task['time'] == task_schedule_run_datetime:
								return {'status': 500, 'message': "Така задача з часом виконання вже існує!", 'user': None}
						tasks.append(new_task)

					upload_task = tasks if tasks is not None else [new_task]

					dynamodb_client.update_item(
					    TableName=dynamodb_table_tasks,
					    Key={"email": {"S": auth_email}},
					    UpdateExpression="SET tasks = :tasks",
					    ExpressionAttributeValues={":tasks": {"S": json.dumps(upload_task)}}
					)

					return {'status': 200, 'message': f"Задача для розсилання повідомлень створена на час {task_schedule_run_datetime}!", 'user': None}
				except Exception as e:
					logger.error(str(e))
					return {'status': 500, 'message': "Створення відкладеної задачі для розсилання повідомлень: опція тимчасово не працює!", 'user': None}

			statuses = []
			status_error = 200

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})
			paid = float(user['Item']['paid']['S'])

			if to_phone == True:
				if paid >= 30.0:
					send_notification_to_phones = self.send_notification_to_phones(auth_email, users, message)
					if send_notification_to_phones.get('status') == 500:
						status_error = 500
					statuses.append(send_notification_to_phones.get('message'))
				else:
					status_error = 500
					statuses.append('Розсилання на телефон: опція заблокована, поки загальна сума поповнення аккаунта не пересягне 30$.')

			if to_email == True:
				send_notification_to_emails = self.send_notification_to_emails(auth_email, company, users, subject, message)
				if send_notification_to_emails.get('status') == 500:
					status_error = 500
				statuses.append(send_notification_to_emails.get('message'))

			if to_whatsapp == True:
				send_notification_to_whatsapp = await self.send_notification_to_whatsapp(auth_email, users, company, message)
				if send_notification_to_whatsapp.get('status') == 500:
					status_error = 500
				statuses.append(send_notification_to_whatsapp.get('message'))

			user = dynamodb_client.get_item(TableName=dynamodb_table_name, Key={'email': {'S': auth_email}})

			data = {
				"name": user['Item']['name']['S'],
				"email": user['Item']['email']['S'],
				"password": cryptocode.decrypt(user['Item']['password']['S'], 'password'),
				"credit": f"{float(user['Item']['credit']['S']):.2f}",
			}

			activity = user['Item'].get('activity')
			if activity is not None:
				data['activity'] = activity['S']

			return {'status': status_error, 'message': statuses, 'user': data}

		except Exception as e:
			return {'status': 500, 'message': str(e), 'user': None}


	def send_notification_to_phones(self, auth_email, users, text):
		try:
			amount_spent = 0

			for user in users:

				name = user[0]
				number = user[2]

				if None not in [name, number]:

					if_number_correct = self.otherOperations.correct_phone_number(number)

					if if_number_correct:
						message = twilio_client.messages.create(
						  from_=twilio_phone_number,
						  body=str(text).replace("[name]", name),
						  to=f"+{number}"
						)

						amount_spent += 0.45


			self.credit(auth_email, amount_spent)

			return {'status': 200, 'message': f"Розсилання на телефон: операція виконана успішно на суму {amount_spent:.2f}$!"}

		except Exception as e:
			logger.error(f"Розсилання на телефон: помилка {str(e)}!")
			return {'status': 500, 'message': f"Розсилання на телефон: опція тимчасово не працює!"}


	async def send_notification_to_whatsapp(self, auth_email, users, company, text):
		try:
			amount_spent = 0

			url = f"https://api.ultramsg.com/{whatsapp_instance_id}/messages/chat"
			headers = {'content-type': 'application/x-www-form-urlencoded'}

			for user in users:

				name = user[0]
				number = user[2]

				if None not in [name, number]:

					if_number_correct = self.otherOperations.correct_phone_number(number)

					if if_number_correct:
						number = f"+{number}"
						message = f"Вам повідомлення від {company}\n\n{str(text).replace('[name]', name)}"

						# pywhatkit.sendwhatmsg_instantly(number, text)

						payload = f"token={whatsapp_token}&to={number}&body={message}"
						#payload = payload.encode('utf8').decode('iso-8859-1')

						async with aiohttp.ClientSession() as session:
							async with session.post(url, data=payload, headers=headers) as request:
								response = await request.json()
								if response.get('message') == 'ok':
									amount_spent += 0.15
								else:
									return {'status': 500, 'message': f"Розсилання у WhatsApp: опція тимчасово не працює!"}

			if amount_spent != 0:
				self.credit(auth_email, amount_spent)

			return {'status': 200, 'message': f"Розсилання у WhatsApp: операція виконана успішно на суму {amount_spent:.2f}$!"}

		except Exception as e:
			logger.error(f"Розсилання у WhatsApp: помилка {str(e)}!")
			return {'status': 500, 'message': f"Розсилання у WhatsApp: опція тимчасово не працює!"}


	def send_notification_to_emails(self, auth_email, company, users, subject, text):
		try:
			amount_spent = 0

			for user in users:

				name = user[0]
				email = user[1]

				if None not in [name, email]:

					if_email_correct = self.otherOperations.correct_email_address(email)

					if if_email_correct:

						gmail_client.create_mime(
							recipient_email_addr=email,
							sender_email_addr='komunnaservice@gmail.com',
							subject=f"{company}: {subject}",
							sender_display_name='Komunna Service',
							recipient_display_name=name,
							content_html='',
							content_text=str(text).replace("[name]", name)
						)

						gmail_client.send_msg()

						amount_spent += 0.20

			self.credit(auth_email, amount_spent)

			return {'status': 200, 'message': f"Розсилання на пошту: операція виконана успішно на суму {amount_spent:.2f}$!"}

		except Exception as e:
			logger.error(f"Розсилання на телефон: помилка {str(e)}!")
			return {'status': 500, 'message': f"Розсилання на пошту: опція тимчасово не працює!"}
