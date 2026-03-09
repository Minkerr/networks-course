curl -X POST http://127.0.0.1:5000/product \
  -H "Content-Type: application/json" \
  -d '{"name": "milk", "description": "3.2%"}'

curl -X GET http://127.0.0.1:5000/product/1

curl -X GET http://127.0.0.1:5000/products

curl -X PUT http://127.0.0.1:5000/product/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "2.5%"}'

curl -X DELETE http://127.0.0.1:5000/product/1

# 404
curl -X GET http://127.0.0.1:5000/product/999

curl -X POST http://127.0.0.1:5000/product/1/image \
  -H "Content-Type: image/png" \
  --data-binary @../images/get-image.png

curl -X GET http://127.0.0.1:5000/product/1/image 