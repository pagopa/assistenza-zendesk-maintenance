import os

from flask import Flask, redirect, request, send_from_directory

app = Flask(__name__)
BRAND_ID_PARTNER = "360004986777"
BRAND_ID_SELFCARE = "9379749838865"
BRAND_ID_SEND = "19650024163345"
BRAND_ID_PAGOPA = "1900000625833"
BRAND_ID_ARC = "27216507367697"
BRAND_ID_APPIO = "360004986757"


@app.route("/eplogin")
def redirector():
    brand_id = request.args.get("brand_id")
    if brand_id == BRAND_ID_PARTNER or brand_id == BRAND_ID_PAGOPA:
        return redirect("https://www.pagopa.gov.it")
    elif brand_id == BRAND_ID_SEND:
        return redirect("https://notifichedigitali.pagopa.it")
    elif brand_id == BRAND_ID_SELFCARE:
        return redirect("https://selfcare.pagopa.it")
    elif brand_id == BRAND_ID_APPIO:
        return redirect("https://www.pagopa.it/it/prodotti-e-servizi/app-io")
    """ else:
        print("SSO LOGIN: No brand specified or not supported")
        return redirect("https://www.pagopa.it/it/societa/di-cosa-ci-occupiamo") """


@app.route("/eplogout")
def sso_logout():
    brand_id = request.args.get("brand_id")
    kind = request.args.get("kind")
    message = request.args.get("message")
    print(f"SSO LOGOUT: {kind} - {message}")
    if brand_id == BRAND_ID_PARTNER or brand_id == BRAND_ID_PAGOPA:
        return redirect("https://www.pagopa.gov.it")
    elif brand_id == BRAND_ID_SEND:
        return redirect("https://notifichedigitali.pagopa.it")
    elif brand_id == BRAND_ID_SELFCARE:
        return redirect("https://selfcare.pagopa.it")
    elif brand_id == BRAND_ID_APPIO:
        return redirect("https://www.pagopa.it/it/prodotti-e-servizi/app-io")
    else:
        print("SSO LOGOUT: No brand specified or not supported")
        return redirect("https://www.pagopa.it/it/societa/di-cosa-ci-occupiamo")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run()
