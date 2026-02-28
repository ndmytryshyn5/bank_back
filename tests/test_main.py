import pytest
import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utils
from conftest import db, client
import constants
from src.core.traceback import traceBack

@pytest.mark.order(1)
class TestAUTH:
    def test_register(self, client: requests.Session, test_user, db):
        print()

        traceBack("Mocking the user")

        traceBack(f"Unverified user: {test_user}")

        r = client.post(f"{constants.BASE_URL}/auth/register", json=test_user)
        assert r.status_code == 200, f"Failed to start registration: {r.text}"

        traceBack(f"Switching to veryfing...")

    def test_verify(self, client: requests.Session, test_user, db):
        print()

        test_user["verification_code"] = utils.get_verification_code(test_user["email"], db)
        traceBack(f"Recieved verification code: {test_user['verification_code']}")

        r = client.post(f"{constants.BASE_URL}/auth/verify-email", json=test_user)
        assert r.status_code == 200, f"Failed to finish registration: {r.text}"
        assert r.cookies.get("authorization"), f"Registraion is not returned access: {r.text}"

        traceBack("Registration successfully finished")
        traceBack("Switching to logout...")

    def test_logout(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}

        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.post(f"{constants.BASE_URL}/auth/logout", cookies=cookies)
        assert r.status_code == 200 and ("authorization" not in client.cookies or client.cookies.get("authorization") is None), f"Logout failed"

        traceBack("Logout successfully finished")
        traceBack("Switching to password reset...")

    def test_reset(self, client: requests.Session, test_user, db):
        print()

        r = client.post(f"{constants.BASE_URL}/auth/reset", json=test_user)
        assert r.status_code == 200, f"Reset request failed {r.text}"
        traceBack("Reset requested")

        payload = {
            "token": utils.get_reset_token(test_user["email"], db),
            "new_password": "p455w0rd2"
        }

        test_user["password"] = payload["new_password"]

        traceBack(f"Token recieved, new password {payload}")

        r = client.patch(f"{constants.BASE_URL}/auth/reset", json=payload)
        assert r.status_code == 200, f"Reset confirm failed {r.text}"

        traceBack("Password reset complete")
        traceBack("Switching to 2FA login...")

    def test_login(self, client: requests.Session, test_user, db):
        print()

        r = client.post(f"{constants.BASE_URL}/auth/2fa/request", json=test_user)
        assert r.status_code == 200, f"Login request failed {r.text}"
        traceBack("Login requested")

        test_user["twofa_code"] = utils.get_2fa_code(test_user["email"], db)

        traceBack(f"2FA code recieved: {test_user['twofa_code']}")

        r = client.post(f"{constants.BASE_URL}/auth/2fa/confirm", json=test_user)
        assert r.status_code == 200, f"Login confirm failed {r.text}"

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.get(f"{constants.BASE_URL}/auth/me", cookies=cookies)
        assert r.status_code == 200, f"Login failed {r.text}"

        data = r.json()

        traceBack(f"Logged successfully: {data}")
        traceBack("END OF AUTH")

@pytest.mark.order(2)
class TestCARD:
    def test_create(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.post(f"{constants.BASE_URL}/card/create", cookies=cookies)
        assert r.status_code == 200, f"First creation card failed {r.text}"
        
        card1 = r.json()

        traceBack(f"First card created: {card1}")

        r = client.post(f"{constants.BASE_URL}/card/create", cookies=cookies)
        assert r.status_code == 200, f"Second creation card failed {r.text}"
        
        card2 = r.json()

        traceBack(f"Second card created: {card2}")

        r = client.get(f"{constants.BASE_URL}/card/", cookies=cookies)
        assert r.status_code == 200, f"Cards information getter failed {r.text}"

        data = r.json()
        assert card1["number"] == data[0].get("number") and \
               card2["number"] == data[1].get("number"), f"Cards information missing"

        card1["id"] = -1
        card2["id"] = -1

        for card in data:
            if card["number"] == card1["number"]:
                card1["id"] = card["card_id"]

            if card["number"] == card2["number"]:
                card2["id"] = card["card_id"]

            if card1["id"] != -1 and card2["id"] != -1:
                break


        assert card1["id"] != -1 and card2["id"] != -1, f"Cards not found"

        test_user["card1"] = card1
        test_user["card2"] = card2

        traceBack(f"Card list successfully loaded: {data}")
        traceBack("Switching to transfers...")
    
    def test_transfer(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "from_card_number": test_user["card2"].get("number"),
            "to_card_number": test_user["card1"].get("number"),
            "amount": 50.0
        }

        r = client.post(f"{constants.BASE_URL}/card/transfer", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Transfer failed {r.text}"
        
        data = r.json()

        traceBack(f"Transfer {test_user['card1'].get('number')} -> {test_user['card2'].get('number')} complete: {data}")
        traceBack("Switching to card deletion...")

    def test_delete(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "card_number": test_user["card2"].get("number")
        }

        r = client.delete(f"{constants.BASE_URL}/card/delete", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Card delete failed {r.text}"

        test_user.pop("card2")
        
        data = r.json()

        traceBack(f"Card deleted: {data}")
        traceBack("Switching to card history...")

    def test_history(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "card_number": test_user["card1"].get("number")
        }

        r = client.post(f"{constants.BASE_URL}/card/history", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Card history getter failed {r.text}"
        
        data = r.json()

        traceBack(f"Card history: {data}")
        traceBack("END OF CARD")

@pytest.mark.order(3)
class TestSAVINGS:
    def test_create(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "name": "My Goal",
            "goal": 650.0
        }

        r = client.post(f"{constants.BASE_URL}/savings/create", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Savings creation failed {r.text}"
        
        data = r.json()

        test_user["savings1"] = data

        payload = {
            "name": "Unachievable Goal",
            "goal": 9999.0
        }

        r = client.post(f"{constants.BASE_URL}/savings/create", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Savings creation failed {r.text}"
        
        data = r.json()

        test_user["savings2"] = data

        traceBack(f"Savings succesfully created: {test_user['savings1']}, {test_user['savings2']}")
        traceBack("Switching to top up...")
    
    def test_topup(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "amount": 30.0,
            "saving_account_id": test_user["savings1"].get("id"),
            "card_id": test_user["card1"].get("id")
        }

        r = client.post(f"{constants.BASE_URL}/savings/topUp", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Top up failed {r.text}"
        
        data = r.json()

        traceBack(f"Top up {test_user['card1'].get('number')} -> {test_user['savings1'].get('name')} complete: {data}")
        traceBack("Switching to savings decreasing...")

    def test_decrease(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "amount": 200.0,
            "saving_account_id": test_user["savings2"].get("id"),
            "card_id": test_user["card1"].get("id")
        }

        r = client.post(f"{constants.BASE_URL}/savings/decrease", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Decrease up failed {r.text}"
        
        data = r.json()

        traceBack(f"Decreasing {test_user['savings1'].get('name')} -> {test_user['card1'].get('number')} complete: {data}")
        traceBack("Switching to savings deletion...")

    def test_delete(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        payload = {
            "saving_account_id": test_user["savings2"].get("id")
        }

        r = client.delete(f"{constants.BASE_URL}/savings/delete", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Savings delete failed {r.text}"
        
        data = r.json()

        traceBack(f"Savings deleted: {data}")
        traceBack("Switching to savings getter...")

    def test_get(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.get(f"{constants.BASE_URL}/savings/", cookies=cookies)
        assert r.status_code == 200, f"Savings getter failed {r.text}"
        
        data = r.json()

        traceBack(f"Savings: {data}")
        traceBack("END OF SAVINGS")

@pytest.mark.order(4)
class TestBILLS:
    def test_create(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        utils.change_balance(test_user["card1"].get("id"), 1500.0, db)

        payload = {
            "name": "Electricity",
            "amount": 999.0,
            "due_date": "2026-06-30T23:59:59"
        }

        r = client.post(f"{constants.BASE_URL}/bills/create", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Bill creation failed {r.text}"
        
        data = r.json()

        test_user["bill1"] = data

        payload = {
            "name": "Unpayable bill",
            "amount": 5000.0,
            "due_date": "2024-06-30T23:59:59"
        }

        r = client.post(f"{constants.BASE_URL}/bills/create", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Bill creation failed {r.text}"
        
        data = r.json()

        test_user["bill2"] = data

        traceBack(f"Bills succesfully created: {test_user['bill1']}, {test_user['bill2']}")
        traceBack("Switching to paying off...")

    def test_pay(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        utils.change_balance(test_user["card1"].get("id"), 1500.0, db)

        payload = {
                "bill_id": test_user["bill1"].get("id"),
                "card_number": test_user["card1"].get("number")
        }

        r = client.post(f"{constants.BASE_URL}/bills/pay", cookies=cookies, json=payload)
        assert r.status_code == 200, f"Bill pay off failed {r.text}"
        
        data = r.json()

        traceBack(f"Bill succesfully payed off: {data}")
        traceBack("Switching to bills getter...")

    def test_show(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.get(f"{constants.BASE_URL}/bills/", cookies=cookies)
        assert r.status_code == 200, f"Bills information getter failed {r.text}"

        data = r.json()

        traceBack(f"Bills: {data}")
        traceBack("END OF BILLS")

@pytest.mark.order(999)
class TestEND:
    def test_end(self, client: requests.Session, test_user, db):
        print()

        traceBack("All GET / endpoints:")

        cookies = {"authorization": client.cookies.get("authorization")}
        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.get(f"{constants.BASE_URL}/auth/me", cookies=cookies)
        assert r.status_code == 200, f"Login failed {r.text}"

        data = r.json()

        traceBack(f"GET /auth/me: {data}")

        r = client.get(f"{constants.BASE_URL}/card/", cookies=cookies)
        assert r.status_code == 200, f"Cards information getter failed {r.text}"

        data = r.json()

        traceBack(f"GET /card [may be empty]: {data}")

        for card in data:
            payload = {
                "card_number": card["number"]
            }

            r = client.post(f"{constants.BASE_URL}/card/history", cookies=cookies, json=payload)
            assert r.status_code == 200, f"Card history getter failed {r.text}"

            history = r.json()

            traceBack(f" - History of {card['number']}: {history}")

        r = client.get(f"{constants.BASE_URL}/savings/", cookies=cookies)
        assert r.status_code == 200, f"Savings information getter failed {r.text}"

        data = r.json()

        traceBack(f"GET /savings [may be empty]: {data}")

        r = client.get(f"{constants.BASE_URL}/bills/", cookies=cookies)
        assert r.status_code == 200, f"Bills information getter failed {r.text}"

        data = r.json()

        traceBack(f"GET /bills [may be empty]: {data}")


    def test_cleanup(self, client: requests.Session, test_user, db):
        print()

        cookies = {"authorization": client.cookies.get("authorization")}

        assert cookies["authorization"], "Cookies are not saved, User is invalid"

        r = client.post(f"{constants.BASE_URL}/auth/logout", cookies=cookies)
        assert r.status_code == 200 and ("authorization" not in client.cookies or client.cookies.get("authorization") is None), f"Logout failed"

        traceBack("Logout successfully finished")

        traceBack("End of all tests. Cleaning up")