## API documentation for singup and login
    - Signup api :POST: https://mlm-backend-pi.vercel.app/api/users/
        mobile_number = 9876543213
        full_name = "test user3"
        password = "Admin@1234"

    - All user list registered
        - api : GET : https://mlm-backend-pi.vercel.app/api/users/

    - Login api : https://mlm-backend-pi.vercel.app/api/users/login/
        mobile_number = 987654321
        password = "Admin@1234"

    - UPA registration under user in legs:
        -   api : https://mlm-backend-pi.vercel.app/api/upausers/upa_registration/
            fields : {
                "address":"Mian street 3 Nodia West sector 4",
                "state":"UP",
                "city":"Nodia",
                "pincode":"201308",
                "reference_id":"834209" # upa unique id
            }
            pass Authorization token in header like 
            Authorization Token ****  to register any user under any user's leg

    