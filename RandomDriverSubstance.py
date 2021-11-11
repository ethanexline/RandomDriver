import xlsxwriter
import sys
import pyodbc
from fpdf import FPDF
from datetime import datetime
from operator import itemgetter
from emailing import emailing

class RandomTest:
    def __init__(self):
        self.pdf_documents = []
        #SQL Server connection object
        self.conn = pyodbc.connect('Driver={SQL Server};'
                            'Server={REDACTED};'
                            'Database={REDACTED};'
                            'Trusted_Connection=yes;')
        self.cursor = self.conn.cursor()

    ##Gets a random list of drivers. Returns a list of drivers sorted by terminal ASC
    def get_drivers(self, company, number_drug = None, number_alc = None):

        drug_sql_number = '@random_drug_number'
        alcohol_sql_number = '@random_alc_number'

        if number_drug is not None or number_alc is not None:
            drug_sql_number = int(number_drug)
            alcohol_sql_number = int(number_alc)

        drug_sql = ''' 
                DECLARE @current_count DECIMAL(10, 2),
                        @random_drug_number DECIMAL(10, 2);

                SELECT @current_count = Count(*)
                FROM   {REDACTED}
                WHERE  {REDACTED} != 'D'
                AND    {REDACTED} = ''' + str(company) + ''';

                SET @random_drug_number = ((@current_count / 12 ) * (select [{REDACTED}] from {REDACTED} where {REDACTED} = 'RND')) + .9;

                select top(cast(''' + str(drug_sql_number) + ''' as int))
                    [{REDACTED}],
                    [{REDACTED}],
                    {REDACTED},
                    {REDACTED},
                    'D' 'type',
                    {REDACTED}
                FROM {REDACTED}
                where {REDACTED} != 'D'
                and {REDACTED} not in (select {REDACTED} from {REDACTED} where {REDACTED} = 'A')
                and {REDACTED} = ''' + str(company) + '''
                order by newid();
                '''

        alcohol_sql = ''' 
                DECLARE @current_count DECIMAL(10, 2),
                        @random_alc_number DECIMAL(10, 2);

                SELECT @current_count = Count(*)
                FROM  {REDACTED}
                WHERE  {REDACTED} != 'D'
                AND    {REDACTED} = ''' + str(company) + ''';

                SET @random_alc_number = ((@current_count / 12 ) * (select [{REDACTED}] from {REDACTED} where {REDACTED} = 'RNA')) + .9;

                select top(cast(''' + str(alcohol_sql_number) + ''' as int))
                    [{REDACTED}],
                    [{REDACTED}],
                    {REDACTED},
                    {REDACTED},
                    'A' 'type',
                    {REDACTED}
                FROM {REDACTED}
                where {REDACTED} != 'D'
                and {REDACTED} not in (select {REDACTED} from {REDACTED} where {REDACTED} = 'A')
                and {REDACTED} = ''' + str(company) + '''
                order by newid();
                '''

        self.cursor.execute(drug_sql)
        random_drug_drivers = self.cursor.fetchall()

        self.cursor.execute(alcohol_sql)
        random_alcohol_drivers = self.cursor.fetchall()

        ##Combine the two into 1 sorted array (Sorted by terminal ASC)
        combined_drivers = random_drug_drivers + random_alcohol_drivers
        combined_drivers2 = sorted(combined_drivers, key=itemgetter(2))

        return combined_drivers2

    ##Records into the history table on the SQL Server
    def insert_history(self, driver):
        sql = '''INSERT INTO {REDACTED}
                ([{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}]
                ,[{REDACTED}])
            VALUES
                (cast(getdate() as date)
                ,?
                ,?
                ,0
                ,?
                ,?
                ,?
                ,?
                ,null
                ,null)'''
        
        if driver[4] == 'A':
            test_type = 'RNA'
        else:
            test_type = 'RND'

        self.cursor.execute(sql, driver[5], test_type, driver[0], driver[2], driver[1], driver[3])
        self.conn.commit()

    ##Creates a PDF for each terminal manager with terminal drivers.
    def create_driver_letters(self, drivers):

        terminal = "NONE"
        driver_pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')

        #Iterate thru driver list
        for driver in drivers:
            ##Set test type for email body.
            if driver[4] == 'A':
                test_type = 'Alcohol'
                AorAn = 'an '
            else:
                test_type = 'Controlled Substance'
                AorAn = 'a '

            ##Create paragraphs for PDF's
            paragraph_1 = '''You have been randomly selected for ''' + AorAn + test_type + ''' test in accordance with FMSCR 382.305. You are to report'''
            paragraph_1_2 = '''within 1 hour to be tested. You must proceed to the testing facility immediately for the testing procedure. Failure to comply'''
            paragraph_1_3 = '''with this request will result in the immediate termination of your employment with Fleetmaster Express, Inc. Per section'''
            paragraph_1_4 = '''382.211, a refusal of this request constitutes a positive result.'''

            paragraph_2 = '''This notification is to be presented as authorization for the test. Once you have completed the random test, return any'''
            paragraph_2_2 = '''documentation given to you by the testing facility to your home terminal.'''

            ##create new PDF if the terminal changes.
            if terminal != driver[2]:
                if terminal != 'NONE':
                    driver_pdf.output('report/' + terminal + ' ' +  datetime.today().strftime('%m-%d-%y') + '.pdf', 'F')
                    self.pdf_documents.append(terminal + ' ' +  datetime.today().strftime('%m-%d-%y') + '.pdf')
                driver_pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')
                driver_pdf.add_page()
                if driver[5] == 301:
                    driver_pdf.image('eng-logo.PNG', 5, 8, 95)
                else:
                    driver_pdf.image('flmr-logo.jpg', 5, 8, 95)

                terminal = driver[2]
            else: #Else, add them to the current PDF
                driver_pdf.add_page()
                if driver[5] == 301:
                    driver_pdf.image('eng-logo.PNG', 5, 8, 95)
                else:
                    driver_pdf.image('flmr-logo.jpg', 5, 8, 95)   

            driver_pdf.set_font('Arial', 'B', 16)
            driver_pdf.cell(105)
            driver_pdf.cell(10, 5, test_type)
            driver_pdf.ln(5)

            driver_pdf.set_font('Arial', 'B', 12)
            driver_pdf.cell(105)
            driver_pdf.cell(10, 5, 'Random Selection: ' + datetime.today().strftime('%m-%d-%y'))
            driver_pdf.ln(10) 

            driver_pdf.cell(105)
            driver_pdf.cell(10, 5, 'Employee Name: ')
            driver_pdf.set_font('Arial', '', 12)
            driver_pdf.cell(25)
            driver_pdf.cell(10, 5, driver[1])
            driver_pdf.ln(5)
            driver_pdf.set_font('Arial', 'B', 12)
            driver_pdf.cell(112)
            driver_pdf.cell(10, 5, 'Employee ID: ')
            driver_pdf.set_font('Arial', '', 12)
            driver_pdf.cell(17.5)
            driver_pdf.cell(10, 5, driver[0])
            driver_pdf.ln(5)
            driver_pdf.set_font('Arial', 'B', 12)
            driver_pdf.cell(120)
            driver_pdf.cell(10, 5, 'Terminal: ')
            driver_pdf.set_font('Arial', '', 12)
            driver_pdf.cell(10)
            driver_pdf.cell(10, 5, driver[2])
            
            driver_pdf.ln(18)
            
            driver_pdf.cell(.1)
            driver_pdf.set_font('Arial', '', 10)
            driver_pdf.cell(0,0, paragraph_1)
            driver_pdf.ln(5)
            driver_pdf.cell(0,0, paragraph_1_2)
            driver_pdf.ln(5)
            driver_pdf.cell(0,0, paragraph_1_3)
            driver_pdf.ln(5)
            driver_pdf.cell(0,0, paragraph_1_4)
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, paragraph_2)
            driver_pdf.ln(5)
            driver_pdf.cell(0,0, paragraph_2_2)
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, 'Thank you for your cooperation.')
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, 'Director of Safety and Risk Management')
            driver_pdf.ln(8)
            driver_pdf.line(10, 110, 200, 110)
            driver_pdf.ln(14)
            driver_pdf.cell(0,0, 'I understand the requirements of this letter and will comply with the instructions as stated.')
            driver_pdf.ln(15)
            driver_pdf.cell(0,0, 'Notification Date/Time (military time): ')
            driver_pdf.line(70, 135, 130, 135)
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, 'Name of Supervisor giving notification: ')

            driver_pdf.line(72.5, 143, 130, 143)
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, 'Signature: ')
            driver_pdf.line(28, 151, 100, 151)
            driver_pdf.ln(8)
            driver_pdf.cell(0,0, 'Date: ')
            driver_pdf.line(20.5, 159, 70, 159)

            self.insert_history(driver)
        driver_pdf.output('report/' + terminal + ' ' +  datetime.today().strftime('%m-%d-%y') + '.pdf', 'F')
        self.pdf_documents.append(terminal + ' ' +  datetime.today().strftime('%m-%d-%y') + '.pdf')


    ##Create the summary page.
    def create_summary(self, test_drivers):

        self.pdf_documents.append('Random Driver List for ' +  datetime.today().strftime('%m-%d-%y') + '.pdf')

        summary_pdf = FPDF()
        summary_pdf.add_page()
        summary_pdf.image('flmr-logo.jpg', 10, 8, 95)

        summary_pdf.set_font('Arial', 'B', 12)
        summary_pdf.cell(100)
        summary_pdf.cell(10, 5, 'Alcohol & Controlled Substance')
        summary_pdf.ln(5)

        summary_pdf.set_font('Arial', 'B', 10)
        summary_pdf.cell(105)
        summary_pdf.cell(10, 5, 'Random Selection: ' + datetime.today().strftime('%m-%d-%y'))
        summary_pdf.ln(20)

        summary_pdf.cell(1)
        summary_pdf.cell(8, 5, 'Terminal')
        summary_pdf.cell(20)
        summary_pdf.cell(10, 5, 'Employee Code')
        summary_pdf.cell(40)
        summary_pdf.cell(10, 5, 'Name')
        summary_pdf.cell(50)
        summary_pdf.cell(10, 5, 'Hire Date')
        summary_pdf.cell(15)
        summary_pdf.cell(10, 5, 'Test Type')

        summary_pdf.ln(3)
        summary_pdf.line(10,40,194,40)
        summary_pdf.ln(3)
        summary_pdf.set_font('Arial', '', 10)

        #foreach driver in the list, do the following.
        for driver in test_drivers:
            summary_pdf.cell(1)
            summary_pdf.cell(8, 5, driver[2])
            summary_pdf.cell(20)
            summary_pdf.cell(10, 5, driver[0])
            summary_pdf.cell(40)
            summary_pdf.cell(10, 5, driver[1])
            summary_pdf.cell(50)
            summary_pdf.cell(10, 5, driver[3])
            summary_pdf.cell(15)
            if driver[4] == 'A':
                summary_pdf.cell(10, 5, 'Alcohol')
            else:
                summary_pdf.cell(10, 5, 'Drug')

            summary_pdf.ln(5)
                
        summary_pdf.output('report/' + 'Random Driver List for ' +  datetime.today().strftime('%m-%d-%y') + '.pdf', 'F')

    ##Assemble the email body.
    def create_email_body(self, drivers):

        email_body = '''<b><h1>Employees Selected:</h1></b> <br>'''
        last_terminal = ''
        for driver in drivers:
            #If the terminal changes, add an extra break.
            if last_terminal != str(driver[2]):
                email_body += '<br>'
                print('added break ' + str(last_terminal) + ' ' + str(driver[2]))
            
            if str(driver[4]) == 'A':
                test_type = 'Alcohol'
            else:
                test_type = 'Controlled Substance'

            email_body += str(driver[2]) + '-' + driver[1] + '(' + driver[0] + ') - ' + test_type + '<br>'
            
            last_terminal = str(driver[2])

        
        return email_body


try:
    #fleetmaster tester
    tester_flt = RandomTest()
    #Get random Fleetmaster drivers from database
    drivers_flt = tester_flt.get_drivers(102)
    #Create summary page flt
    tester_flt.create_summary(drivers_flt)
    #Create detail page flt
    tester_flt.create_driver_letters(drivers_flt)   
            
    #Send the email with multiple attachments. create_email_body() is called here.
    email = emailing("ethane@fleetmasterexpress.com", "Fleetmaster Random Selections for " + datetime.today().strftime('%Y-%m-%d'), tester_flt.create_email_body(drivers_flt), tester_flt.pdf_documents, "report/")
    email.send_mail()

    #Now, lets do the englander drivers. 

    #englander test
    tester_eng = RandomTest()
    #Get random Englander drivers from database
    drivers_eng = tester_eng.get_drivers(301)
    #Create summary page eng
    tester_eng.create_summary(drivers_eng)
    #Create detail page eng
    tester_eng.create_driver_letters(drivers_eng)

    #Send the email with multiple attachments. create_email_body() is called here.
    email = emailing("ethane@fleetmasterexpress.com", "Englander Random Selections for " + datetime.today().strftime('%Y-%m-%d'), tester_eng.create_email_body(drivers_eng), tester_eng.pdf_documents, "report/")
    email.send_mail()

##If any errors occur that are not handled otherwise, send an email to let someone know!
except Exception as e:
    print(e)
    email = emailing("ethane@fleetmasterexpress.com", "ERROR! Random selections report has failed!", 'Random selection report has encountered an error - ' + str(e))
    email.send_mail()

