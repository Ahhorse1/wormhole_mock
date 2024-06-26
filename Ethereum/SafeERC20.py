from collections import defaultdict

UINT256_MAX = (1 << 256) - 1

class SafeERC20:
    def __init__(self):
        self._totalSupply = 0
        self._balances = defaultdict(int)
        self._allowances = defaultdict(lambda: defaultdict(int))
        self._msgSender = '0x0'
        self._name = None
        self._symbol = None
        self.decimal = 18

    def constructor(self, name=None, symbol=None):
        self._name = name
        self._symbol = symbol

    def decimals(self) -> int:
        return self.decimal
    
    def set_decimals(self, decimal):
        self.decimal = decimal
    
    def set_msgSender(self, address):
        self._msgSender = address

    def set_balance(self, address, balance):
        self._totalSupply += balance
        self._balances[address] = balance
    
    def set_allowances(self, owner, spender, balance):
        self._allowances[owner][spender] = balance

    def balanceOf(self, address):
        return self._balances[address]
    
    def safeTransferFrom(self, token, from_address, to_address, value: int):
        self._callOptionalReturn(token, ['transferFrom', from_address, to_address, value])

    def approve(self, spender, value):
        owner = self._msgSender
        return self._approve(owner, spender, value)

    def allowance(self, owner, spender):
        return self._allowances[owner][spender]

    def _callOptionalReturn(self, token, data):
        if not data:
            print(f'Error Occurred {token}')
        elif data[0] == 'transferFrom':
            assert self.transferFrom(data[1], data[2], data[3]) == True, 'transferFrom Error'
    
    def transferFrom(self, from_address, to_address, value):
        # address sender = _msgSender();
        spender = self._msgSender
        assert self._spendAllowance(from_address, spender, value) != False, 'spendAllowance Error'
        assert self._transfer(from_address, to_address, value) != False, 'transfer Error'

        return True
    
    def _spendAllowance(self, owner, spender, value):
        currentAllowance = self.allowance(owner, spender)
        if currentAllowance < UINT256_MAX:
            if currentAllowance < value:
                print(f'Insufficient Allowance {spender}, {currentAllowance}, {value}')
                return False
            else:
                self._approve(owner, spender, currentAllowance - value)

    def _transfer(self, from_address, to_address, value):
        if from_address == '0x0':
            print('Invalid Sender')
            return False
        if to_address == '0x0':
            print('Invalid Reciever')
            return False
        return self._update(from_address, to_address, value)
    
    def _update(self, from_address, to_address, value):
        if from_address == '0x0':
            self._totalSupply += value
        else:
            fromBalance = self._balances[from_address]
            if fromBalance < value:
                print(f'Insufficient Balance {from_address}, {fromBalance}, {value}')
                return False
            self._balances[from_address] -= value
        
        if to_address == '0x0':
            self._totalSupply -= value
        else:
            self._balances[to_address] += value

        print(f'\nEmitting Transfer Event {from_address}, {to_address}, {value}\n')
        return True
    
    def _burn(self, account, value):
        if account == '0x0':
            print('Invalid Sender')
            return False
        
        return self._update(account, '0x0', value)
    
    def _mint(self, account, value):
        if account == '0x0':
            print('Invalid Reciever')
            return False
        
        return self._update('0x0', account, value)
    
    def _approve(self, owner, spender, value):
        if owner == '0x0':
            print('Invalid Approver')
            return False
        if spender == '0x0':
            print('Invalid Spender')
            return False
        self._allowances[owner][spender] = value

        print(f'\nEmitting Approval Event {owner}, {spender}, {value}\n')

        return True
    
