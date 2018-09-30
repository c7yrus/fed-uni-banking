class BankAccount():

    def __init__(self):
        '''Constructor to set account_number to '0', pin_number to an empty string,
           balance to 0.0, interest_rate to 0.0 and transaction_list to an empty list.'''
        self.account_number = '0'
        self.pin_number = ""
        self.balance = 0.0
        self.interest_rate = 0.0
        self.transaction_list = []

    def deposit_funds(self, amount):
        '''Function to deposit an amount to the account balance. Raises an
           exception if it receives a value that cannot be cast to float.'''
        self.balance = float(self.balance)
        amount = float(amount)
        self.balance = str(self.balance + amount)
        return str(self.balance)

    def withdraw_funds(self, amount):
        '''Function to withdraw an amount from the account balance. Raises an
           exception if it receives a value that cannot be cast to float. Raises
           an exception if the amount to withdraw is greater than the available
           funds in the account.'''
        self.balance = float(self.balance)
        amount = float(amount)
        # print(amount)
        if self.balance >= amount:
            self.balance = str(self.balance - amount)
            return str(self.balance)
        else:
            return str(self.balance)

        
    def get_transaction_string(self):
        '''Function to create and return a string of the transaction list. Each transaction
           consists of two lines - either the word "Deposit" or "Withdrawal" on
           the first line, and then the amount deposited or withdrawn on the next line.'''
        
            


    def save_to_file(self):
        '''Function to overwrite the account text file with the current account
           details. Account number, pin number, balance and interest (in that
           precise order) are the first four lines - there are then two lines
           per transaction as outlined in the above 'get_transaction_string'
           function.'''
        lst = []
        lst.append(self.account_number)
        lst.append(self.pin_number)
        lst.append(float(self.balance))
        lst.append(float(self.interest_rate))

        fo = open(self.account_number+".txt", 'w')
        v = [[i for i in val] for val in self.transaction_list]
        for i in v:
            for a in i:
                lst.append(a)
        i=0
        for i in range(0,len(lst)):
            fo.write(str(lst[i])+"\n")

        fo.close()
