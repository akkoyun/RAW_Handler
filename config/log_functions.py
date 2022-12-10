def Log_API_Online():

    # LOG
	print("------------------------------------------------")
	print("Kafka IoT Data Producer - ONLINE")
	print("------------------------------------------------")

def Log_API_Offline():

	# LOG
	print("------------------------------------------------")
	print("Kafka IoT Data Producer - OFFLINE")
	print("------------------------------------------------")

def Log_API_Error():

    # Print LOG
    print("API Error --> Sended to Kafka Error Queue..")

def Log_API_Incomming_Data(TimeStamp, ID, Command):

	print("Incomming Data -->", TimeStamp, " : ", ID, " - ", Command, " --> Sended to Queue..")

# LOG Kafka Header
def Log_Kafka_Header(Command, Device_ID, Device_IP, Device_Time, Kafka_Topic, Kafka_Partition, Kafka_Offset):

	# Print LOG
	print("................................................................................")
	print("Command     : ", Command)
	print("Device ID   : ", Device_ID)
	print("Client IP   : ", Device_IP)
	print("Device Time : ", Device_Time)
	print("Topic : ", Kafka_Topic, " - Partition : ", Kafka_Partition, " - Offset : ", Kafka_Offset)
	print("................................................................................")
