import requests
import json

base_url = 'http://127.0.0.1:8001/api/v1'
s = requests.Session()

# 1. Register
print("Registering...")
r1 = s.post(f"{base_url}/auth/register", json={
    "email": "test2@test.com",
    "password": "password123",
    "full_name": "Test User"
})
print("Register Response:", r1.status_code, r1.text)

# 2. Login
print("\nLogging in...")
r2 = s.post(f"{base_url}/auth/login", json={
    "email": "test2@test.com",
    "password": "password123"
})
print("Login Response:", r2.status_code, r2.text)
print("Cookies:", s.cookies.get_dict())

# 3. Complete onboarding
print("\nOnboarding...")
r3 = s.put(f"{base_url}/users/profile", json={
    "first_name": "Test",
    "last_name": "User",
    "risk_tolerance": "MEDIUM",
    "onboarding_completed": True
})
print("Onboarding Response:", r3.status_code, r3.text)

# 4. Logout
print("\nLogging out...")
r4 = s.post(f"{base_url}/auth/logout")
print("Logout Response:", r4.status_code, r4.text)
print("Cookies after logout:", s.cookies.get_dict())

# 5. Login again
print("\nLogging in again...")
r5 = s.post(f"{base_url}/auth/login", json={
    "email": "test2@test.com",
    "password": "password123"
})
print("Login 2 Response:", r5.status_code, r5.text)
print("Cookies:", s.cookies.get_dict())

