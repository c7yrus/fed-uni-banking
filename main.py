import tkinter as tk
from tkinter import messagebox

# from pylab import plot, show, xlabel, ylabel
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from bankaccount import BankAccount

win = tk.Tk()
# Set window size here to '440x640' pixels
win.geometry('440x640')
# Set window title here to 'FedUni Banking'
win.title('FedUni Banking')
# The account number entry and associated variable
account_number_var = tk.StringVar()
account_number_entry = tk.Entry(win, textvariable=account_number_var)


# The pin number entry and associated variable.
# Note: Modify this to 'show' PIN numbers as asterisks (i.e. **** not 1234)
pin_number_var = tk.StringVar()
account_pin_entry = tk.Entry(win, text='PIN Number', textvariable=pin_number_var, show="*")
pin_number = ''
# The balance label and associated variable
balance_var = tk.StringVar()
balance_var.set('Balance: $0.00')
balance_label = tk.Label(win, textvariable=balance_var)

# The Entry widget to accept a numerical value to deposit or withdraw
amount_text = tk.StringVar()
amount_entry = tk.Entry(win, textvariable=amount_text)

# The transaction text widget holds text of the accounts transactions
transaction_text_widget = tk.Text(win, height=10, width=48)

# The bank account object we will work with
account = BankAccount()

# ---------- Button Handlers for Login Screen ----------

def clear_pin_entry(event):
    '''Function to clear the PIN number entry when the Clear / Cancel button is clicked.'''
    # Clear the pin number entry here
    global pin_number
    pin_number_var.set('')
    pin_number = ''
    account_number_entry.focus_set()

def handle_pin_button(event):
    '''Function to add the number of the button clicked to the PIN number entry via its associated variable.'''    
    global pin_number
    eventValue = event.widget.cget("text")
    # Limit to 4 chars in length
    if len(pin_number_var.get()) < 4:
        pin_number = pin_number + eventValue
    # Set the new pin number on the pin_number_var
    pin_number_var.set(pin_number)
    # print(pin_number_var.get())

def log_in(event):
    '''Function to log in to the banking system using a known account number and PIN.'''
    global account
    global pin_number_var
    global account_num_entry
    global balance_var
    global account_file

    # Create the filename from the entered account number with '.txt' on the end
    account_file = open(account_number_var.get()+".txt", 'r+')
    # Try to open the account file for reading
    try:
        # Open the account file for reading
        file_data = account_file.readlines()
        file_data = [data.strip('\n') for data in file_data]
        # print(file_data)
        print(pin_number_var.get())
        # First line is account number
        account.account_number = file_data[0]

        # Second line is PIN number, raise exceptionk if the PIN entered doesn't match account PIN read 
        if pin_number_var.get() != file_data[1]:
            raise messagebox.showerror("Error", "Invalid PIN")

        # Read third and fourth lines (balance and interest rate) 
        else:
            account.pin_number = file_data[1]
            account.balance = file_data[2]
            balance_var.set(file_data[2])
            account.interest_rate = file_data[3]

        # Section to read account transactions from file - start an infinite 'do-while' loop here        
        transaction_data = file_data[4:]
        # print(transaction_data)
        i = 0
        while i < len(transaction_data):
            # Attempt to read a line from the account file, break if we've hit the end of the file. If we
            # read a line then it's the transaction type, so read the next line which will be the transaction amount.
            # and then create a tuple from both lines and add it to the account's transaction_list            
            account.transaction_list.append((transaction_data[i], transaction_data[i+1]))
            i += 2
        print(account.transaction_list)
        # Close the file now we're finished with it
        account_file.close()
    # Catch exception if we couldn't open the file or PIN entered did not match account PIN
    except ValueError:
        # Show error messagebox and & reset BankAccount object to default...
        messagebox.showerror("Error", "Please Ensure that you entered Details carefully")
        #  ...also clear PIN entry and change focus to account number entry
        pin_number_var.set('')
        account_number_entry.focus_set()
    # Got here without raising an exception? Then we can log in - so remove the widgets and display the account screen
    if pin_number_var.get() == file_data[1]:
        remove_all_widgets()
        create_account_screen()

# ---------- Button Handlers for Account Screen ----------

def save_and_log_out():
    '''Function  to overwrite the account file with the current state of
       the account object (i.e. including any new transactions), remove
       all widgets and display the login screen.'''
    global account
    global pin_number
    # Save the account with any new transactions
    account.save_to_file()

    # Reset the bank acount object
    account = BankAccount()
    # Reset the account number and pin to blank
    account_number_var.set('')
    pin_number_var.set('')
    pin_number = '' 
    # Remove all widgets and display the login screen again
    remove_all_widgets()
    create_login_screen()

def perform_deposit():
    '''Function to add a deposit for the amount in the amount entry to the
       account's transaction list.'''
    global account    
    global amount_entry
    global balance_label
    global balance_var

    # Try to increase the account balance and append the deposit to the account file
    try:
        # Get the cash amount to deposit. Note: We check legality inside account's deposit method
        # print(amount_entry.get())
        account.deposit_funds(amount_text.get())
        # Deposit funds
        
        # Update the transaction widget with the new transaction by calling account.get_transaction_string()
        # Note: Configure the text widget to be state='normal' first, then delete contents, then instert new
        #       contents, and finally configure back to state='disabled' so it cannot be user edited.
        account.get_transaction_string()
        account.transaction_list.append(("Deposit", float(amount_text.get())))


        transaction_text_widget = tk.Text(win, height=10, width=48)
        text_scrollbar = tk.Scrollbar(win, command=transaction_text_widget.yview, orient='vertical')
        v = [[i for i in val] for val in account.transaction_list]

        for i in v:
            for a in i:
                # _list.append(a)
                transaction_text_widget.config(state='normal')
                transaction_text_widget.insert('end',str(a) + '\n')
        transaction_text_widget.config(state='disabled')
        transaction_text_widget.grid(row=3)
        transaction_text_widget.config(yscrollcommand=text_scrollbar.set)

        # Change the balance label to reflect the new balance
        balance_var.set(str(account.balance))
        balance_label = tk.Label(win, font=12, text = "Balance: $"+ balance_var.get())
        balance_label.grid(row=1, column=1, sticky="nsew")
        # print("New Balance is: ",balance_var.get())      
        # Clear the amount entry
        amount_text.set('')
        # Update the interest graph with our new balance
        plot_interest_graph()
    # Catch and display exception as a 'showerror' messagebox with a title of 'Transaction Error' and the text of the exception
    except ValueError:
        messagebox.showerror("Transaction Error", "Amount cannot be deposit")



def perform_withdrawal():
    '''Function to withdraw the amount in the amount entry from the account balance and add an entry to the transaction list.'''
    global account    
    global amount_entry
    global balance_label
    global balance_var

    # Try to increase the account balance and append the deposit to the account file
    try:
        # Get the cash amount to deposit. Note: We check legality inside account's withdraw_funds method
        
        # Withdraw funds
        if float(amount_text.get()) < float(account.balance):        
            account.withdraw_funds(amount_text.get())
        # Update the transaction widget with the new transaction by calling account.get_transaction_string()
        # Note: Configure the text widget to be state='normal' first, then delete contents, then instert new
        #       contents, and finally configure back to state='disabled' so it cannot be user edited.
            account.get_transaction_string()
            account.transaction_list.append(("Withdrawal", float(amount_text.get())))

            transaction_text_widget = tk.Text(win, height=10, width=48)
            text_scrollbar = tk.Scrollbar(win, command=transaction_text_widget.yview, orient='vertical')
            v = [[i for i in val] for val in account.transaction_list]

            for i in v:
                for a in i:
                    # _list.append(a)
                    transaction_text_widget.config(state='normal')
                    transaction_text_widget.insert('end',str(a) + '\n')
            transaction_text_widget.config(state='disabled')
            transaction_text_widget.grid(row=3)
            transaction_text_widget.config(yscrollcommand=text_scrollbar.set)
        else:
            messagebox.showerror("Error", "Insufficient Funds to make transaction")
        # Change the balance label to reflect the new balance
        balance_var.set(str(account.balance))
        balance_label = tk.Label(win, font=12, text = "Balance: $"+ balance_var.get())
        balance_label.grid(row=1, column=1, sticky="nsew")
        # Clear the amount entry
        amount_text.set('')
        # Update the interest graph with our new balance
        plot_interest_graph()
    # Catch and display any returned exception as a messagebox 'showerror'
    except ValueError:
        messagebox.showerror("Error", "Invalid Amount to withdraw!")



# ---------- Utility functions ----------

def remove_all_widgets():
    '''Function to remove all the widgets from the window.'''
    global win
    for widget in win.winfo_children():
        widget.grid_remove()

def read_line_from_account_file():
    '''Function to read a line from the accounts file but not the last newline character.
       Note: The account_file must be open to read from for this function to succeed.'''
    global account_file
    # print(account_file)
    return account_file.readline()


def plot_interest_graph():
    '''Function to plot the cumulative interest for the next 12 months here.'''

    # YOUR CODE to generate the x and y lists here which will be plotted
    x = []
    y = []
    bal = float(account.balance)
    ir = float(account.interest_rate)
    # print("bal is: ", bal, account.interest_rate, type(account.interest_rate))
    for i in range(1,13):
        bal = bal + (bal * ir / 12)
        x.append(i)
        y.append(bal)

    # This code to add the plots to the window is a little bit fiddly so you are provided with it.
    # Just make sure you generate a list called 'x' and a list called 'y' and the graph will be plotted correctly.
    figure = Figure(figsize=(5,2), dpi=100)
    figure.suptitle('Cumulative Interest 12 Months')
    a = figure.add_subplot(111)
    a.plot(x, y, marker='o')
    a.grid()
    
    canvas = FigureCanvasTkAgg(figure, master=win)
    canvas.draw()
    graph_widget = canvas.get_tk_widget()
    graph_widget.grid(row=4, column=0, columnspan=5, sticky='nsew')


# ---------- UI Screen Drawing Functions ----------

def create_login_screen():
    '''Function to create the login screen.'''    
    
    # ----- Row 0 -----

    # 'FedUni Banking' label here. Font size is 32.
    mainLabel = tk.Label(win, font=('arial', 32, 'bold'), text = 'FedUni Banking')
    mainLabel.grid(columnspan = 3)

    # ----- Row 1 -----

    # Acount Number / Pin label here
    accLabel = tk.Label(win, font=12, text = 'Account Number / PIN')
    accLabel.grid(row = 1, column = 0)
    # Account number entry here
    account_number_entry.grid(row=1, column=1)
    account_number_entry.focus_set()
    # Account pin entry here
    account_pin_entry.grid(row=1, column=2)

    # ----- Row 2 -----

    # Buttons 1, 2 and 3 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    btn1 = tk.Button(win, padx=40, pady=40, fg='black', font=('arial', 12), text='1')
    btn1.bind('<Button-1>', handle_pin_button)
    btn1.grid(row=2, column=0, sticky="nsew")

    btn2 = tk.Button(win, fg='black', font=('arial', 12), text='2')
    btn2.bind('<Button-1>', handle_pin_button)
    btn2.grid(row=2, column=1, sticky="nsew")

    btn3 = tk.Button(win,fg='black', font=('arial', 12), text='3')
    btn3.bind('<Button-1>', handle_pin_button)
    btn3.grid(row=2, column=2, sticky="nsew")

    # ----- Row 3 -----

    # Buttons 4, 5 and 6 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    btn4 = tk.Button(win, padx=40, pady=40, fg='black', font=('arial', 12), text='4')
    btn4.bind('<Button-1>', handle_pin_button)
    btn4.grid(row=3, column=0, sticky="nsew")

    btn5 = tk.Button(win, fg='black', font=('arial', 12), text='5')
    btn5.bind('<Button-1>', handle_pin_button)
    btn5.grid(row=3, column=1, sticky="nsew")

    btn6 = tk.Button(win,fg='black', font=('arial', 12), text='6')
    btn6.bind('<Button-1>', handle_pin_button)
    btn6.grid(row=3, column=2, sticky="nsew")


    # ----- Row 4 -----

    # Buttons 7, 8 and 9 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    btn7 = tk.Button(win, padx=40, pady=40, fg='black', font=('arial', 12), text='7')
    btn7.bind('<Button-1>', handle_pin_button)
    btn7.grid(row=4, column=0, sticky="nsew")

    btn8 = tk.Button(win, fg='black', font=('arial', 12), text='8')
    btn8.bind('<Button-1>', handle_pin_button)
    btn8.grid(row=4, column=1, sticky="nsew")

    btn9 = tk.Button(win,fg='black', font=('arial', 12), text='9')
    btn9.bind('<Button-1>', handle_pin_button)
    btn9.grid(row=4, column=2, sticky="nsew")


    # ----- Row 5 -----

    # Cancel/Clear button here. 'bg' and 'activebackground' should be 'red'. But calls 'clear_pin_entry' function.
    btnClear = tk.Button(win, padx=40, pady=40, fg='black', background="red", font=('arial', 12), text='Cancel / Clear')
    btnClear.bind('<Button-1>', clear_pin_entry)
    btnClear.grid(row=5, column=0,sticky="nsew")
    # Button 0 here
    btn0 = tk.Button(win, fg='black', font=('arial', 12), text='0')
    btn0.bind('<Button-1>', handle_pin_button)
    btn0.grid(row=5, column=1, sticky="nsew")

    # Login button here. 'bg' and 'activebackground' should be 'green'). Button calls 'log_in' function.
    btnLogin = tk.Button(win, fg='black',bg='green', font=('arial', 12), text='Log In')
    btnLogin.bind('<Button-1>', log_in)
    btnLogin.grid(row=5, column=2, sticky="nsew")

    # ----- Set column & row weights -----

    # Set column and row weights. There are 5 columns and 6 rows (0..4 and 0..5 respectively)
    win.rowconfigure(0, weight=1)
    win.rowconfigure(1, weight=1)
    win.rowconfigure(2,weight=1)
    win.rowconfigure(3,weight=1)
    win.rowconfigure(4,weight=1)
    win.rowconfigure(5,weight=1)
    win.columnconfigure(0, weight = 1)
    win.columnconfigure(1, weight = 1)
    win.columnconfigure(2, weight = 1)
    win.columnconfigure(3, weight = 1)
    win.columnconfigure(4, weight = 1)

def create_account_screen():
    '''Function to create the account screen.'''
    global amount_text
    global amount_label
    global transaction_text_widget
    global balance_var
    global account
    
    # ----- Row 0 -----

    # FedUni Banking label here. Font size should be 24.
    mainLabel = tk.Label(win, font=('arial', 24), text = 'FedUni Banking')
    mainLabel.grid(columnspan = 4)

    # ----- Row 1 -----

    # Account number label here
    accountLabel = tk.Label(win, font=12, text="Account Number "+ account.account_number)
    accountLabel.grid(row=1, column=0,sticky="nsew")
    # Balance label here
    # print(balance_var)

    balance_label = tk.Label(win, font=12, text = "Balance: $"+ balance_var.get())
    balance_label.grid(row=1, column=1, sticky="nsew")
    # Log out button here
    logout_button = tk.Button(win, fg='black', font=12, text="Log Out", command=save_and_log_out)
    logout_button.grid(row=1, column=2, sticky="nsew")
    
    # ----- Row 2 -----
    # Amount label here
    amount_label = tk.Label(win, font=12, text="Amount($)")
    amount_label.grid(row=2, column=0,sticky="nsew")
    # Amount entry here
    amount_entry.grid(row=2, column=1, sticky="nsew")
    # Deposit button here
    deposit_button = tk.Button(win,text="Deposit", command= perform_deposit)
    deposit_button.grid(row=2,column=2, sticky="nsew")
    # Withdraw button here
    withdraw_button = tk.Button(win,text="Withdraw", command=perform_withdrawal)
    withdraw_button.grid(row=2, column=3, sticky="nsew")
    # NOTE: Bind Deposit and Withdraw buttons via the command attribute to the relevant deposit and withdraw
    #       functions in this file. If we "BIND" these buttons then the button being pressed keeps looking as
    #       if it is still pressed if an exception is raised during the deposit or withdraw operation, which is
    #       offputting.
    
    # ----- Row 3 -----

    # Declare scrollbar (text_scrollbar) here (BEFORE transaction text widget)
    
    transaction_text_widget = tk.Text(win, height=10, width=48)
    text_scrollbar = tk.Scrollbar(win, command=transaction_text_widget.yview, orient='vertical')
    v = [[i for i in val] for val in account.transaction_list]

    for i in v:
        for a in i:
            # _list.append(a)
            transaction_text_widget.insert('end',str(a) + '\n')
    transaction_text_widget.config(state='disabled')
    transaction_text_widget.grid(row=3)
    # Add transaction Text widget and configure to be in 'disabled' mode so it cannot be edited.
    # Note: Set the yscrollcommand to be 'text_scrollbar.set' here so that it actually scrolls the Text widget
    # Note: When updating the transaction text widget it must be set back to 'normal mode' (i.e. state='normal') for it to be edited
    # Now add the scrollbar and set it to change with the yview of the text widget
    text_scrollbar.grid(row=3, column=5)
    transaction_text_widget.config(yscrollcommand=text_scrollbar.set)
    # ----- Row 4 - Graph -----

    # Call plot_interest_graph() here to display the graph
    plot_interest_graph()

    # ----- Set column & row weights -----

    # Set column and row weights here - there are 5 rows and 5 columns (numbered 0 through 4 not 1 through 5!)
    win.rowconfigure(0, weight=1)
    win.rowconfigure(1, weight=1)
    win.rowconfigure(2,weight=1)
    win.rowconfigure(3,weight=1)
    win.rowconfigure(4,weight=1)
    win.columnconfigure(0, weight = 1)
    win.columnconfigure(1, weight = 1)
    win.columnconfigure(2, weight = 1)
    win.columnconfigure(3, weight = 1)
    win.columnconfigure(4, weight = 1)

# ---------- Display Login Screen & Start Main loop ----------

create_login_screen()
win.mainloop()
