import os

from flask import Flask, redirect, request, send_from_directory

app = Flask(__name__)
BRAND_ID_PARTNER = "360004986777"
BRAND_ID_SELFCARE = "9379749838865"


@app.route("/eplogin")
def redirector():
    brand_id = request.args.get("brand_id")
    kind = request.args.get("kind")
    message = request.args.get("message")
    print("SSO LOGIN: %s - %s", kind, message)
    if brand_id == BRAND_ID_PARTNER:
        # Portale Partner (skip SSO -> ZD native auth.)
        return redirect("https://partner.assistenza.pagopa.it/access/normal")
    else:
        print("SSO LOGIN: No brand specified or not supported")
        return redirect("https://www.pagopa.it/it/societa/di-cosa-ci-occupiamo")


@app.route("/eplogout")
def sso_logout():
    brand_id = request.args.get("brand_id")
    kind = request.args.get("kind")
    message = request.args.get("message")
    print("SSO LOGIN: %s - %s", kind, message)
    if brand_id == BRAND_ID_PARTNER:
        # Portale Partner (skip SSO -> ZD native auth.)
        return redirect("https://partner.assistenza.pagopa.it/access/normal")
    else:
        print("SSO LOGOUT: No brand specified or not supported")
        return redirect("https://www.pagopa.it")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run()
