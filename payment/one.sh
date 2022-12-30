curl --location --request POST 'http://localhost:8000/moneypay/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
   "username":"TCS4",
   "password":"TCS123456",
   "password2":"TCS123456",
   "email":"TCS1253433@gmail.com",
   "first_name":"TCS",
   "last_name":"RAJ",
   "phone_number":"433456889"
}'
