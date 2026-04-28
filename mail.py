import mysql.connector
import datetime
import sys
import logging
import os



"""
CREATE VIEW PersistentMail as
SELECT B.id,C.name,C.mobile,C.vehicle_number,C.vehicle_type,C.total_visits,C.total_spent,C.free_washes,B.bill_no,B.total_amount,B.bill_date
FROM bills B inner join customers C
on B.customer_id = C.id
WHERE B .is_active =  1;


"""
# ------------------------------
# log configuration

# create directory
basedir=os.getcwd()
logdir=os.path.join(basedir,'logs')
os.makedirs(logdir, exist_ok=True)
log_file = os.path.join(
    logdir,
    f"SMS_Sender{datetime.datetime.today().strftime('%Y%m%d')}.log"
)

# correct filename + quotes


logging.basicConfig(
    level=logging.DEBUG,
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

# database configuration
DB_CONFIG = {
    'host': '13.233.81.208',
    'database': 'test',
    'user': 'root',
    'password': 'admin',
    'raise_on_warnings': True
}


# --------------------------------------------------------------

class SMSSender:
    def __init__(self, dbConfig):
        logging.info("*"*20)
        logging.info("Starting Mail Application")
        logging.info("*" * 20)
        self.dbConfig = dbConfig
        count=1
        #fetching users info
        for i in self.FetchActiveBills():
            logging.info(f'Sending SMS user:{count}')
            mobilenumber=self.MobileNumberValidate(i[2])
            messages=self.Generate_EnlighBill(i)


            if mobilenumber != False:
                if self.SMS_API(mobilenumber, messages):
                    self.MarkInactive(i[8],0)
                    logging.info(f'Mail sent successfully')
                else:
                    self.MarkInactive(i[8],2)
                    logging.info(f'Mail sent failed')

            count+=1


    def MarkInactive(self,BillNo,status):
        with mysql.connector.connect(**self.dbConfig) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE bills SET is_active = %s WHERE bill_no = %s", [status,BillNo])
            connection.commit()




    def FetchActiveBills(self):
        logger = logging.getLogger("FetchingActiveBills")
        try:
            with mysql.connector.connect(**self.dbConfig) as connection:
                logging.info("Connected database %s", self.dbConfig['database'])
                cursor = connection.cursor()

                # check total active bills
                cursor.execute("SELECT count(*) FROM PersistentMail")
                logger.info("Fetched active bill count: %s", cursor.fetchone()[0])

                # collecting bills data
                cursor.execute("SELECT * FROM PersistentMail")
                active_bills = cursor.fetchall()
                return active_bills


        except mysql.connector.Error as err:
            logger.error("Error connecting to database %s", self.dbConfig['database'])
            logger.error(err)
            sys.exit()

    def Generate_MarathiBill(self, data):
        marathi_message = f"""
        प्रिय {data[1]},

        सह्याद्री वॉशिंग सेंटरला भेट दिल्याबद्दल धन्यवाद 🚗✨

        🧾 बिल पावती
        बिल क्र.: {data[8]}
        दिनांक: {data[10].strftime("%d-%m-%Y %I:%M %p")}

        ग्राहक: {data[1]}
        मोबाईल: {data[2]}
        वाहन क्रमांक: {data[3]}
        वाहन प्रकार: {data[4]}

        रक्कम भरली: ₹{data[9]}

        आपली माहिती:
        एकूण भेटी: {data[5]}
        एकूण खर्च: ₹{data[6]}
        फ्री वॉश: {data[7]}

        ✨ पुन्हा भेट द्या आणि विशेष ऑफर्सचा लाभ घ्या.

        📍 सह्याद्री वॉशिंग सेंटर
        सह्याद्री बिझनेस पार्क, गुंड प्लॉट,
        परांडा रोड, साई मधुरा नगर जवळ,
        बार्शी, जि. सोलापूर - 413411

        आपल्या विश्वासाबद्दल धन्यवाद. पुन्हा भेट द्या!

        - टीम सह्याद्री वॉशिंग सेंटर
        """
        return marathi_message

    def Generate_EnlighBill(self, data):
        english_message = f"""
        Dear {data[1]},

        Thank you for visiting Sahyadri Washing Center 🚗✨

        🧾 Bill Receipt
        Bill No: {data[8]}
        Date: {data[10].strftime("%d-%m-%Y %I:%M %p")}

        Customer: {data[1]}
        Mobile: {data[2]}
        Vehicle No: {data[3]}
        Vehicle Type: {data[4]}

        Amount Paid: ₹{data[9]}

        Loyalty Details:
        Total Visits: {data[5]}
        Total Spent: ₹{data[6]}
        Free Washes: {data[7]}

        ✨ Visit again for special offers on washing and detailing services.

        📍 Sahyadri Washing Center
        Sahyadri Business Park, Gund Plot,
        Paranda Road, Near Sai Madhura Nagar,
        Barshi, Dist. Solapur - 413411

        Thank you for your support. Visit Again!

        - Team Sahyadri Washing Center
        """
        return english_message

    # validate mobile number is correct or not then trigger SMS
    def MobileNumberValidate(self, MobileNumber):
        logger = logging.getLogger("MobileNumberValidation")
        try:
            # Clean number
            number = str(MobileNumber).strip().replace(" ", "").replace("-", "")

            # Remove country code
            if number.startswith("+91"):
                number = number[3:]
            elif number.startswith("91") and len(number) == 12:
                number = number[2:]

            # Validation
            if not number.isdigit():
                logger.error("Mobile contains non-numeric characters")
                return False

            if len(number) != 10:
                logger.error("Mobile number must be 10 digits")
                return False

            if number[0] not in ['6', '7', '8', '9']:
                logger.error("Invalid Indian mobile number")
                return False

            if len(set(number)) == 1:
                logger.error("Invalid repeated digits")
                return False

            # Add country code for SMS API
            number = "91" + number
            return number

        except Exception as e:
            logger.error(f"SendSMS Error: {e}")
            return False

    def SMS_API(self, number, Message):
        logger = logging.getLogger("SMS_API")
        logger.info("Started sending SMS via API")
        logger.info("Number: %s", number)
        return False


objetct1 = SMSSender(DB_CONFIG)


