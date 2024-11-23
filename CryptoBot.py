from requests import post



class errors(BaseException):
    class UNAUTHORIZED(Exception):
        def __init__(self, name) -> None:
            self.name = name
        def __str__(self) -> str:
            return self.name
    class NOT_ENOUGH_MONEY(Exception):
        def __init__(self, name) -> None:
            self.name = name
        def __str__(self) -> str:
            return self.name

            


class Send:
    def __init__(self, TOKEN: str, fiat: str = None, asset: str = None) -> None:
        self.TOKEN = TOKEN
        self.url = "https://pay.crypt.bot/api/"
        self.headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': TOKEN}
        if fiat is None and asset is None:
            self.fiat = "usd"
            self.asset = None
        elif fiat is None:
            self.asset = asset
            self.fiat = None
        else:
            self.fiat = fiat
            self.asset = None



    def create_invoice(self, amount: float, asset: str) -> dict:
        json = {'amount': amount, "asset": asset}
        res = post(self.url + "createInvoice", json=json, headers=self.headers).json()
        if 'error' in res and res['error']['name'] == "UNAUTHORIZED":
            raise errors.UNAUTHORIZED("ТОКЕН НЕ ПОДХОДИТ")
        res = res['result']
        return res


    def get_invoice(self, invoice_id) -> dict:
        json = {'invoice_ids': invoice_id}
        res = post(self.url + "getInvoices", json=json, headers=self.headers).json()
        if 'error' in res and res['error']['name'] == "UNAUTHORIZED":
            raise errors.UNAUTHORIZED("ТОКЕН НЕ ПОДХОДИТ")
        res = res['result']['items'][0]
        return res


    def create_cheque(self, amount, asset: str = "USDT"):
        json = {'amount': amount, "asset": asset}
        res = post(self.url + "createCheck", json=json, headers=self.headers).json()
        if not 'result' in res:
            raise errors.NOT_ENOUGH_MONEY("ДЕНЯК НЕТУ")
        else:
            return res['result']
    
    def getMe(self):
        res = post(self.url + "getMe", headers=self.headers).json()
        return res
    
    def getBalance(self):
        res = post(self.url + "getBalance", headers=self.headers).json()
        return res


    




if __name__ == "__main__":
    send = Send("272439:AARtmZE2gW6DIfvnGfvG00Ho1kzik7b7IIE", asset="USDT")
    # print(send.get_invoice(10330215))
    print(send.create_invoice(1200))
    print(send.getBalance())