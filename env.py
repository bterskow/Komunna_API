import os


class ENV:
	def data(self):
		return {
			'smtp_server': os.environ.get('smtp_server'),
			'smtp_account': os.environ.get('smtp_account'),
			'smtp_password': os.environ.get('smtp_password'),
			'twilio_account_sid': os.environ.get('twilio_account_sid'),
			'twilio_auth_token': os.environ.get('twilio_auth_token'),
			'twilio_phone_number': os.environ.get('twilio_phone_number'),
			'aws_access_key_id': os.environ.get('aws_access_key_id'),
			'aws_secret_access_key': os.environ.get('aws_secret_access_key'),
			'dynamodb_table_name': os.environ.get('dynamodb_table_name'),
			'dynamodb_table_chat_name': os.environ.get('dynamodb_table_chat_name'),
			'dynamodb_table_tasks': os.environ.get('dynamodb_table_tasks'),
			'aws_access_key_id_s3': os.environ.get('aws_access_key_id_s3'),
			'aws_secret_access_key_s3': os.environ.get('aws_secret_access_key_s3'),
			'liqpay_public_key': os.environ.get('liqpay_public_key'),
			'liqpay_private_key': os.environ.get('liqpay_private_key'),
			'whatsapp_instance_id': os.environ.get('whatsapp_instance_id'),
			'whatsapp_token': os.environ.get('whatsapp_token'),
		}