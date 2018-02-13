import sys
import os
import numpy as np

path_dir = os.getcwd()

def str_to_f(s):
    try:
        f = float(s)
    except TypeError:
        f = 0
    return f

def safe_round(f):
    if f - int(f) >= 0.5:
        i = int(f) + 1
    else:
        i = int(f)
    return i

def load_data():
    '''

    :return:
     returns the lines of donor transactions as a list of lists. The indexing of the
     list on axis=1 corresponds to the Federal Election Commission's (FEC) defined dictionary
     @http://classic.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml
    '''
    raw_transactions = []
    percentile = 100
    try:
        with open(path_dir + path_itcont) as f:
            lines = list(f)
        for each in lines:
            if each.count('|') == 20:
                raw_transactions.append(each[:-1].split('|'))
    except FileNotFoundError:
        print('\nThe \'itcont.txt\' file was not found')
        print('Invalid path is: {}'.format(path_itcont))

    try:
        with open(path_dir + path_percentile) as f:
            percentile = f.readline()
        if '\n' in percentile:
            percentile = percentile[:-1]
        percentile = str_to_f(percentile)
    except FileNotFoundError:
        print('The \'percentile.txt\' file was not found')
        print('Invalid path is: {}'.format(path_percentile))
    return raw_transactions, percentile

def validate_tranaction(t):
    '''
    :param t:
     t is a transaction line list conforming to the index of
     the data dictionary as described by the FEC's website.
    :return:
     True is returned if the transaction meets the criteria defined by
     False if the transaction is not interesting to the user
    '''
    #print(t[15], t[13], t[10], t[0], t[14])
    if type(t) is not list:
        return False
    elif len(t) < 21:
        return False
    elif t[15] is not '': #checks for any entry in field 'OTHER_ID'
        return False
    elif len(t[13]) is not 8 or not t[13].isnumeric(): #checks for valid `TRANSACTION_DT`
        return False
    elif len(t[10]) < 5 or not t[10].isnumeric(): #checks for valid 'ZIP_CODE'
        return False
    elif 0 >= len(t[7]) < 201: #checks for valid 'NAME'
        return False
    elif len(t[0]) is not 9: #checks for valid 'CMTE_ID'
        return False
    elif len(t[14]) is None: #checks for valid 'TRANSACTION_AMT'
        return False
    return True

def running_totals(recipient, year, zip, contribution):
    dict_key = '{}_'.format(recipient) + \
               '{}_'.format(year) + \
               '{}'.format(zip)
    try:
        current_contributions = running_total_record[dict_key]
    except:
        current_contributions = []

    current_contributions.append(contribution)
    current_contributions = sorted(current_contributions)
    running_total_record[dict_key] = current_contributions

    number_of_contributions = len(current_contributions)

    year_sum = safe_round(sum(current_contributions))

    percentile_contribution = np.percentile(current_contributions, percentile, interpolation='nearest')

    return year_sum, number_of_contributions, percentile_contribution

def create_first_emit_record(a=[], b=[]):

    # is the donation to the same recipient?
    if a[0] == b[0]:
        same_recipient = True
    else:
        same_recipient = False

    # is the donation in the same calendar year?
    if int(b[13][-4:]) == int(a[13][-4:]):
        same_year = True
    else:
        same_year = False

    contribution_a = str_to_f(a[14])
    contribution_b = str_to_f(b[14])
    if contribution_a is 0 or contribution_b is 0:
        # original data entry is malformed
        return False

    record = ''
    contribution = contribution_b
    prefix = b

    if not same_year:
        if int(a[13][-4:]) > int(b[13][-4:]):
            prefix = a
            contribution = contribution_a

    if same_year:
        if same_recipient:
            prefix = b
            contribution = contribution_b

        elif not same_recipient:
            contribution = contribution_a
            prefix = a
            CMTE_ID = prefix[0]
            ZIP_CODE = prefix[10][:5]
            YEAR = prefix[13][-4:]
            running_total, number_cont, percentile_cont = running_totals(CMTE_ID, YEAR, ZIP_CODE, contribution)
            record = '{:s}|'.format(CMTE_ID) + \
                     '{:s}|'.format(ZIP_CODE) + \
                     '{:s}|'.format(YEAR) + \
                     '{:.0f}|'.format(percentile_cont) + \
                     '{:.0f}|'.format(running_total) + \
                     '{:d}___'.format(number_cont)
            contribution = contribution_b
            prefix = b

    CMTE_ID = prefix[0]
    ZIP_CODE = prefix[10][:5]
    YEAR = prefix[13][-4:]
    running_total, number_cont, percentile_cont = running_totals(CMTE_ID, YEAR, ZIP_CODE, contribution)

    record = '{:s}|'.format(CMTE_ID) + \
             '{:s}|'.format(ZIP_CODE) + \
             '{:s}|'.format(YEAR) + \
             '{:.0f}|'.format(percentile_cont) + \
             '{:.0f}|'.format(running_total) + \
             '{:d}'.format(number_cont)




    return record

def modify_existing_record(a, b):
    CMTE_ID = a[:9]
    ZIP_CODE = a[10:15]
    YEAR = a[16:20]
    contribution = str_to_f(b[14])
    running_total, number_cont, percentile_cont = running_totals(CMTE_ID, YEAR, ZIP_CODE, contribution)
    record = '{:s}|'.format(CMTE_ID) + \
             '{:s}|'.format(ZIP_CODE) + \
             '{:s}|'.format(YEAR) + \
             '{:.0f}|'.format(percentile_cont) + \
             '{:.0f}|'.format(running_total) + \
             '{:d}'.format(number_cont)
    return record

def create_new_record(b):
    CMTE_ID = b[0]
    ZIP_CODE = b[10][:5]
    YEAR = b[13][-4:]
    contribution = str_to_f(b[14])
    running_total, number_cont, percentile_cont = running_totals(CMTE_ID, YEAR, ZIP_CODE, contribution)
    record = '{:s}|'.format(CMTE_ID) + \
             '{:s}|'.format(ZIP_CODE) + \
             '{:s}|'.format(YEAR) + \
             '{:.0f}|'.format(percentile_cont) + \
             '{:.0f}|'.format(running_total) + \
             '{:d}'.format(number_cont)
    return record

def parse_transactions(transactions=[]):
    emit=[]
    omit=[]
    for x in range(26):
        omit.append([])

    while transactions:
        transaction = transactions.pop(0)
        valid = validate_tranaction(transaction)
        if not valid:
            continue

            # unique_donor_id = donor name + zip code  example; SABOURIN, JOE02895
        unique_donor_id = transaction[7] + transaction[10][:5]
        while unique_donor_id.startswith(' '):
            unique_donor_id = unique_donor_id[1:]
        omit_index = ord(unique_donor_id[0].upper())-65
        if unique_donor_id in all_repeat_donors:
            CMTE_ID = transaction[0]
            ZIP_CODE = transaction[10][:5]
            YEAR = transaction[13][-4:]
            existing_line = ''
            for index, line in enumerate(emit):
                if line.startswith(CMTE_ID) and line[10:15] == ZIP_CODE and line[16:20] == YEAR:
                    existing_line = line
                    record = modify_existing_record(existing_line, transaction)
                    emit.append(record) # looks like we should append instead of modify, so
                    #emit[index] = record   # it's appended
                    break
            if existing_line == '':
                record = create_new_record(transaction)
                emit.append(record)

        elif unique_donor_id in omit[omit_index]:
            i = omit[omit_index].index(unique_donor_id)
            omit_line = omit[omit_index].pop(i+1)
            record = create_first_emit_record(omit_line, transaction)
            if '___' in record:
                all_repeat_donors.append(omit[omit_index].pop(i))
                records = record.split('___')
                emit.append(records[0])
                emit.append(records[1])
            else:
                all_repeat_donors.append(omit[omit_index].pop(i))
                emit.append(record)
        else:
            omit[omit_index].append(unique_donor_id)
            omit[omit_index].append(transaction)

    return emit

def write_output(lines):
    try:
        with open(path_dir + path_output, 'w') as f:
            for line in lines:
                if len(line) < 2:
                    print('skip',line)
                f.write(line + '\n')
            f.flush()
    except FileNotFoundError:
        if os.path.exists(path_dir) and not os.path.exists(path_dir + '/output'):
            os.makedirs(path_dir + '/output')
            return write_output(lines)
    return True

if __name__ == "__main__":

    #tock = time.time()
    global path_itcont, path_percentile, path_output
    global running_total_record, all_repeat_donors
    running_total_record = {}
    all_repeat_donors = []

    if len(sys.argv) == 4:
        print('\nincreasing understanding....')
        path_itcont = str(sys.argv[1])
        path_percentile = str(sys.argv[2])
        path_output = str(sys.argv[3])
    else:
        print('Paths to three files must be included with the execution of this script.')
        print('Example:')
        print('python3 ./src/repeating_donors.py input/itcont.txt input/percentile.txt output/repeat_donors.txt')

    raw_transactions, percentile = load_data()
    emits = parse_transactions(raw_transactions)
    write_output(emits)

    #tick = time.time()
    #print('took {0:.2f}s'.format(tick-tock))

    print('\n')





