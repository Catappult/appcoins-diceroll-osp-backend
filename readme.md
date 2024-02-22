# Catappult One-Step Payment (OSP) Backend Implementation
This project is an example of a very basic backend implementation for the Catappult One-Step Payment (OSP) system using FastAPI and Docker. Catappult OSP is a simple and easy solution to implement billing in your application. It consists of a URL that launches the AppCoins Wallet app to process the payment.
### How to Run
**Prerequisites**

- Docker

**Steps**

Clone the repository to your local machine.
Navigate to the project directory.
```
cd osp-backend
```
Build the Docker image using the provided Dockerfile with the following command:
```   
docker build -t osp-backend .
```
Run the Docker container with the following command:
```
docker run --rm -p 8000:8000 -e SECRET_KEY='YOUR_SECRET_KEY' -e BASE_URL='YOUR_BACKEND_BASE_URL' osp-backend
```
You can also optionally pass the PACKAGE_NAME variable with your package name.

For local testing we recommeding using tools like [ngrok](https://ngrok.com) which once installed and with a free account can be ran simple with 
```
ngrok http 8000
```
After running this command you can pass the URL that ngrok gives you to the `BASE_URL` argument in the `docker run` command.

The secret key can be obtained via [this documentation](https://docs.catappult.io/docs/secret-key-management). The `BASE_URL` will be used for the callback handler.

### API Endpoints
The application exposes the following endpoints:

`GET //osp_url/{product}`: Generates a URL with a order reference and signature. This URL is used to launch the AppCoins Wallet app for processing the payment.

`POST /callback_handler`: Handles callbacks from the Catappult OSP system and verifies the data integrity of the transaction.

`GET /callback_result/{order_reference}`: Returns the status of a specific order reference. Returns 404 if the order reference is not found.

### Additional Information
The project follows the flow outlined in the Catappult OSP documentation:

1. The end-user tries to buy a product on your application.
2. Applications requests the URL for the product by calling `GET /osp_url`.
2. The application launches the OSP billing flow by calling the generated OSP URL.
3. The AppCoins Wallet reads the OSP URL, handles the payment, and on completion, calls your web service endpoint (handled by the `POST /callback_handler` endpoint in this project).
4. Your web service validates the transaction data (handled by the verify_data_integrity function in this project).
5. You give the product to the end user.


