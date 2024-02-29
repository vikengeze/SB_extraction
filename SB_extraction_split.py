#Assuming full files are customer.csv, invoice.csv, invoice_item.csv by default
#Assuming output files (extraction files) are cust_out.csv, inv_out.csv, inv_it_out.csv by default
#Some items start with ” instead of “(ex:”Maria” instead of “Maria”), fixed for uniformity, could also completely remove “”
#Same code as SB_extraction.py, but full info method is split into get_cust_info, get_inv_info and get_inv_it_info
#Also an extra method (get_inv_codes) is added to get relevant invoices

import os 

class FileOps:
    def __init__(self, samples_n='samples.csv', full_cus='customer.csv', full_inv='invoice.csv', full_inv_it='invoice_item.csv',
                 cust_out='cust_out.csv', inv_out='inv_out.csv', inv_it_out='inv_it_out.csv'): 
        self.samples_n = samples_n #customer codes file
        self.full_cus = full_cus #3 full files used to extract from
        self.full_inv = full_inv
        self.full_inv_it = full_inv_it
        self.cust_out = cust_out #3 output extraction files
        self.inv_out = inv_out
        self.inv_it_out = inv_it_out


    def get_cust_codes(self, num, encoding='UTF-8'): #num is amount of codes to extract, UTF-8>=ascii

        try:
            with open(self.samples_n, 'r', encoding=encoding) as file:
                counter = 0
                cust_codes = [] #list w/customer codes
                next(file) #skip header line
                for line in file: 
                    #for each line we get the customer code
                    cust_codes.append(line.strip())
                    counter += 1
                    if counter >= num: #alrdy found {num} amount of codes -- (could be == instead)
                        return cust_codes
                print(f"Only found {counter} customer codes in sample file instead of {num}")
                return cust_codes        
        except FileNotFoundError:
            return f'No file named {self.samples_n} is found'
        except Exception as error:
            return f'Could not open {self.samples_n}: {str(error)}'
        
    def get_inv_codes(self, cust_codes, encoding='UTF-8'): #num is amount of codes to extract, UTF-8>=ascii

        try:
            with open(self.full_inv, 'r', encoding=encoding) as file:
                inv_codes = [] #list w/invoice codes
                next(file) #skip header line
                for line in file: 
                    #for each line we get the invoice code if customer is relevant
                    info = line.replace(',”', ',“').strip().split(',') #splits line into a list 
                    if info[0] in cust_codes:
                        inv_codes.append(info[1])
                return inv_codes        
        except FileNotFoundError:
            return f'No file named {self.samples_n} is found'
        except Exception as error:
            return f'Could not open {self.samples_n}: {str(error)}'
        
    def get_cust_info(self, customer_codes, encoding='UTF-8'): #opens each of the full files in turn, inserts information into dictionaries 
        #and then writes relevant information to extraction files(for each file seperately)

        if not customer_codes:
            print(f"List of customer codes is empty")
            return
        
        #adding extracted information to dictionaries before writing to files -- using unique values as keys
        customer_information = {} #key, [values] -> customer_code, [first_name, last_name]

        try: #open the full customer file to get names for each code
            with open(self.full_cus, 'r', encoding=encoding) as file:
                headers = file.readline().replace(',”', ',“').strip() #first line is headers (fixing “”)
                customer_headers = headers.split(',')
                for line in file: #line by line -> less mem
                    info = line.replace(',”', ',“').strip().split(',') #splits line into a list 
                    if info[0] in cust_codes:
                        customer_information[info[0]] = info[1:] #if we dont know how many values we want to have in the future
                        #customer_information[info[0]] = [info[1], info[2]]
        except FileNotFoundError:
            return f'No file named {self.full_cus} is found'
        except Exception as error:
            return f'Could not open {self.full_cus}: {str(error)}'
        
        mode = 'w' #this is the mode to open output file with
        if os.path.exists(self.cust_out): #if the file exists we might not want to overwrite it
            mode = input("Customer extraction file already exists, would you append(a) to it or overwrite it(w)?").lower()
            if mode != 'a' and mode != 'w':
                print('Invalid choice, going to append')
                mode = 'a'

        try: #open the customer extraction file to write to it
            with open(self.cust_out, mode, encoding=encoding) as file:
                file.write(f"{','.join(customer_headers)}\n") #write the headers separated by commas
                for key in customer_information:
                    file.write(f"{key},{','.join(customer_information[key])}\n") #write every value in the dictionary separated by commas
        except Exception as error:
            return f'Could not open or create {self.cust_out}: {str(error)}'
        

    def get_inv_info(self, customer_codes, encoding='UTF-8'):

        invoice_information = {} #key, [values] -> invoice_code, [customer_code, amount, date]
        try:
            with open(self.full_inv, 'r', encoding=encoding) as file:
                headers = file.readline().replace(',”', ',“').strip() #first line is always headers
                invoice_headers = headers.split(',')
                for line in file:
                    info = line.replace(',”', ',“').strip().split(',')
                    if info[0] in customer_codes:
                        invoice_information[info[1]] = info[0:1] + info[2:] #if we dont know how many values we want to have in the future
                        #invoice_information[info[1]] = [info[0], info[2], info[3]]
        except FileNotFoundError:
            return f'No file named {self.full_inv} is found'
        except Exception as error:
            return f'Could not open {self.full_inv}: {str(error)}'

        mode = 'w' #this is the mode to open output file with
        if os.path.exists(self.inv_out): #if the file exists we might not want to overwrite it
            mode = input("Invoices extraction file already exists, would you append(a) to it or overwrite it(w)?").lower()
            if mode != 'a' and mode != 'w':
                print('Invalid choice, going to append')
                mode = 'a'

        try: #open the invoice extraction file to write to it
            with open(self.inv_out, mode, encoding=encoding) as file:
                file.write(f"{','.join(invoice_headers)}\n") #write the headers separated by commas
                for key in invoice_information:
                    file.write(f"{key},{','.join(invoice_information[key])}\n") #write every value in the dictionary separated by commas
        except Exception as error:
            return f'Could not open or create {self.inv_out}: {str(error)}'

        #del customer_information


    def get_inv_it_info(self, invoice_codes, encoding='UTF-8'):

        invoice_item_information = {} #key, [values] -> [invoice_code, item_code], [amount, quantity]

        try:
            with open(self.full_inv_it, 'r', encoding=encoding) as file:
                headers = file.readline().replace(',”', ',“').strip() #first line is always headers
                invoice_item_headers = headers.split(',')
                for line in file:
                    info = line.replace(',”', ',“').strip().split(',')
                    if info[0] in invoice_codes:
                        invoice_item_information[info[0], info[1]] = info[2:] #if we dont know how many values we want to have in the future
                        #invoice_item_information[info[0], info[1]] = [info[2], info[3]]
        except FileNotFoundError:
            return f'No file named {self.full_inv_it} is found'
        except Exception as error:
            return f'Could not open {self.full_inv_it}: {str(error)}'

        mode = 'w' #this is the mode to open output file with
        if os.path.exists(self.inv_it_out): #if the file exists we might not want to overwrite it
            mode = input("Invoice items extraction file already exists, would you append(a) to it or overwrite it(w)?").lower()
            if mode != 'a' and mode != 'w':
                print('Invalid choice, going to append')
                mode = 'a'

        try: #open the invoice items extraction file to write to it
            with open(self.inv_it_out, mode, encoding=encoding) as file:
                file.write(f"{','.join(invoice_item_headers)}\n") #write the headers separated by commas
                for key in invoice_item_information:
                    file.write(f"{key[0]},{key[1]},{','.join(invoice_item_information[key])}\n") #write every value in the dictionary separated by commas
        except Exception as error:
            return f'Could not open or create {self.inv_it_out}: {str(error)}'

file_op = FileOps("samples.csv") 

#num_of_codes = input("Enter amount of customer codes to extract?")
cust_codes = file_op.get_cust_codes(1) #get 1 customer code (only 2 in sample file)
inv_codes = file_op.get_inv_codes(cust_codes) #gets all invoices from relevant customers
file_op.get_cust_info(cust_codes) #extract information for said customer codes
file_op.get_inv_info(cust_codes) 
file_op.get_inv_it_info(inv_codes)