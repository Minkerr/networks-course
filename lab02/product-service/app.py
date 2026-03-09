import os

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOADS, exist_ok=True)

products: dict[int, dict] = {}
_next_id = 1


def product_json(p: dict) -> dict:
    return {
        "id": p["id"],
        "name": p["name"],
        "description": p["description"],
        "icon": p.get("icon"),
    }


def icon_path(product_id: int) -> str:
    return os.path.join(UPLOADS, str(product_id))


@app.route("/product", methods=["POST"])
def create_product():
    data = request.get_json(force=True, silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Expected JSON body with name and description"}), 400
    name = data.get("name")
    description = data.get("description")
    if name is None:
        return jsonify({"error": "Field 'name' is required"}), 400
    global _next_id
    pid = _next_id
    _next_id += 1
    product = {"id": pid, "name": str(name), "description": str(description) if description is not None else "", "icon": None}
    products[pid] = product
    return jsonify(product_json(product)), 201


@app.route("/product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found", "id": product_id}), 404
    return jsonify(product_json(products[product_id]))


@app.route("/product/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found", "id": product_id}), 404
    data = request.get_json(force=True, silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Expected JSON body"}), 400
    p = products[product_id]
    if "name" in data:
        p["name"] = str(data["name"])
    if "description" in data:
        p["description"] = str(data["description"])
    if "icon" in data:
        p["icon"] = data["icon"]
    return jsonify(product_json(p))


@app.route("/product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found", "id": product_id}), 404
    p = products.pop(product_id)
    path = icon_path(product_id)
    if os.path.isfile(path):
        os.remove(path)
    return jsonify(product_json(p))


@app.route("/product/<int:product_id>/image", methods=["POST"])
def upload_image(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found", "id": product_id}), 404
    data = request.get_data()
    if not data:
        return jsonify({"error": "Expected binary body"}), 400
    path = icon_path(product_id)
    with open(path, "wb") as f:
        f.write(data)
    content_type = request.content_type or "application/octet-stream"
    if content_type.startswith("image/"):
        products[product_id]["_icon_content_type"] = content_type
    else:
        products[product_id]["_icon_content_type"] = "image/png"
    products[product_id]["icon"] = f"{product_id}"
    return jsonify(product_json(products[product_id])), 200


@app.route("/product/<int:product_id>/image", methods=["GET"])
def get_image(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found", "id": product_id}), 404
    p = products[product_id]
    if not p.get("icon"):
        return jsonify({"error": "Image not found", "id": product_id}), 404
    path = icon_path(product_id)
    if not os.path.isfile(path):
        p["icon"] = None
        p.pop("_icon_content_type", None)
        return jsonify({"error": "Image not found", "id": product_id}), 404
    mimetype = p.get("_icon_content_type") or "image/png"
    return send_file(path, mimetype=mimetype)


@app.route("/products", methods=["GET"])
def list_products():
    return jsonify([product_json(p) for p in products.values()])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
